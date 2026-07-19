# Technical Implementation Plan — Zuzu Match Bot (MVP)

**Workspace:** `/home/filla_saputro/zuzu-bot/`
**Based on:** PRD.md, agents.md, ADR-001, ADR-002
**Status:** Draft — butuh approval Tuan sebelum implementasi

---

## 1. Project Structure

```
zuzu-bot/
├── pyproject.toml                 # dependencies (aiogram 3, FastAPI, SQLAlchemy 2, asyncpg, redis, pydantic, deepface, etc.)
├── .env.example                   # template env vars
├── .env                           # actual (gitignored)
├── alembic/                       # migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── bot/                           # aiogram 3.x bot
│   ├── __init__.py                # bot entry point
│   ├── main.py                    # dispatcher, middlewares, startup/shutdown
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── db.py                  # DB session middleware
│   │   ├── logging.py
│   │   └── rate_limit.py
│   ├── filters/
│   │   └── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py               # /start, onboarding entry
│   │   ├── profile.py             # /profile, edit profile
│   │   ├── quest.py               # /quest, daily candidates
│   │   ├── chat.py                # match chat relay
│   │   ├── admin.py               # admin commands (review queue)
│   │   └── errors.py              # error handlers
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline.py              # inline button builders
│   │   └── reply.py               # reply keyboards
│   ├── states/
│   │   ├── __init__.py
│   │   ├── onboarding.py          # FSM states for progressive profiling
│   │   ├── profile_edit.py
│   │   └── quest.py
│   └── utils/
│       ├── __init__.py
│       ├── messages.py            # user-facing copy (Indonesia, casual)
│       └── helpers.py
├── api/                           # FastAPI app (Mini App / Web App endpoints)
│   ├── __init__.py
│   ├── main.py                    # FastAPI app + lifespan
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── webapp.py              # Mini App: photo upload, bio, interests
│   │   ├── health.py              # /healthz
│   │   └── admin.py               # admin dashboard (optional)
│   ├── dependencies.py            # DB session, auth
│   └── schemas/
│       ├── __init__.py
│       ├── profile.py             # Pydantic models for Web App
│       └── photo.py
├── core/                          # shared config, db, utils
│   ├── __init__.py
│   ├── config.py                  # pydantic-settings
│   ├── database.py                # async engine, session factory
│   ├── exp.py                     # EXP calculation, level thresholds
│   ├── matching.py                # MVP matching: rule + content-based
│   ├── photo_verify.py            # DeepFace wrapper + NSFW filter
│   └── security.py                # secrets, token validation
├── models/                        # SQLAlchemy models
│   ├── __init__.py
│   ├── base.py                    # DeclarativeBase + TimestampMixin
│   ├── user.py
│   ├── profile.py
│   ├── interaction.py
│   ├── match.py
│   └── quest.py
├── services/                      # business logic (called by handlers & API)
│   ├── __init__.py
│   ├── user_service.py
│   ├── profile_service.py
│   ├── matching_service.py
│   ├── quest_service.py
│   ├── chat_service.py
│   ├── gamification_service.py    # EXP, level, streak, spark
│   └── verification_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_matching.py
│   ├── test_exp.py
│   └── test_verification.py
├── scripts/
│   ├── init_db.py                 # create tables (dev)
│   ├── seed_interests.py          # seed interest tags
│   └── run_bot.py                 # systemd entry: python -m scripts.run_bot
├── adr/
│   ├── ADR-001-tech-stack.md
│   └── ADR-002-photo-verification.md
└── docker/                        # optional, later
    ├── Dockerfile.bot
    ├── Dockerfile.api
    └── docker-compose.yml
```

---

## 2. Database Schema (SQLAlchemy Models)

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `users` | `telegram_id PK`, `username`, `level`, `exp`, `spark`, `streak`, `onboarding_step` | Core identity + gamification |
| `profiles` | `user_id FK`, `bio`, `photo_file_ids[]`, `selfie_file_id`, `age`, `gender`, `location`, `lat/lon`, `interests[]`, `preferences JSONB`, `completeness_score`, `badges[]` | Profile detail |
| `interactions` | `id PK`, `user_id FK`, `target_id FK`, `action ENUM`, `timestamp`, `metadata JSONB` | Training data foundation |
| `matches` | `id PK`, `user_a FK`, `user_b FK`, `status ENUM`, `message_count`, `compatibility_score` | Mutual likes |
| `quests` | `id PK`, `user_id FK`, `quest_date`, `candidates[]`, `details JSONB`, `completed` | Daily quest log |

**Migration tool:** Alembic (generate first migration after model freeze).

---

## 3. Bot Architecture (aiogram 3.x)

### 3.1 FSM States — Onboarding Flow
```
ONBOARD_START
  → ONBOARD_PHOTO          (upload foto profil)
  → ONBOARD_SELFIE         (challenge pose selfie)   ← AI verification here
  → ONBOARD_BIO            (text input)
  → ONBOARD_INTERESTS      (multi-select dari tag list)
  → ONBOARD_PREFERENCES    (age range, gender, location radius)
  → ONBOARD_COMPLETE       (Level 1, EXP awarded)
```

### 3.2 Main Handlers
| Command / Trigger | Handler | FSM State |
|-------------------|---------|-----------|
| `/start` | `start.cmd_start` | any → ONBOARD_START (if new) / MAIN_MENU |
| `/profile` | `profile.profile_flow` | profile view/edit |
| `/quest` | `quest.quest_flow` | daily candidates |
| `/chat` | `chat.chat_flow` | match conversation |
| Inline buttons | callback routers | per-flow states |

### 3.3 Middlewares
- **DbSessionMiddleware**: attach `AsyncSession` to `data["session"]`
- **LoggingMiddleware**: log updates, latency
- **RateLimitMiddleware**: per-user token bucket (Redis)
- **AuthMiddleware**: auto-create User row on first sight

---

## 4. API Layer (FastAPI) — Mini App Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/webapp/profile/photo` | Upload profile photo (returns file_id) |
| `POST` | `/webapp/profile/selfie` | Upload verification selfie + pose check |
| `POST` | `/webapp/profile/bio` | Save bio |
| `POST` | `/webapp/profile/interests` | Save interest tags |
| `POST` | `/webapp/profile/preferences` | Save search preferences |
| `GET` | `/webapp/profile/me` | Get current profile (for Mini App render) |
| `GET` | `/healthz` | Health check (systemd / monitoring) |

**Auth:** `initData` validation from Telegram Web App (HMAC check with bot token).

---

## 5. Matching Algorithm (MVP — Rule + Content-Based)

### 5.1 Flow
```
daily_quest(user_id):
  1. Load user profile + preferences
  2. Rule filter: age ∈ [pref_min, pref_max], gender ∈ pref_genders,
     location within radius (PostGIS or haversine), not interacted today
  3. Content score: cosine_similarity(user.interests[], candidate.interests[])
  4. Rank: score = w_rule * 1.0 + w_content * cosine
  5. Take top 5-10 → create Quest row with candidates[]
  6. Return candidate profiles (photo, bio snippet, compatibility %)
```

### 5.2 Weights (tunable)
- `w_rule = 0.4` (hard filter = pass/fail; only pass candidates scored)
- `w_content = 0.6` (cosine 0-1)

### 5.3 Data Freshness
- Quest generated once per day (cron or on-demand at first `/quest`)
- Candidates excluded if `interactions` exists for today

---

## 6. Photo Verification (AI Hybrid — ADR-002)

### 6.1 Pipeline
```
POST /webapp/profile/photo
  → save telegram file_id
  → NSFW filter (detect-nsfw) → reject if score > 0.7
  → respond: "OK, sekarang selfie dengan pose: tunjuk jari kelingking ke kiri 🤙"

POST /webapp/profile/selfie
  → save file_id
  → DeepFace.verify(img1=profile, img2=selfie, model_name="Facenet512", detector_backend="opencv")
  → score = distance * 100  (lower distance = higher match)
  → if score >= 70: VERIFIED → user.level = 1, award EXP
  → if 50 <= score < 70: QUEUE admin review (admin bot notification)
  → if score < 50: REJECT → "Foto tidak cocok, coba lagi dengan pencahayaan lebih baik"
```

### 6.2 Admin Review Queue
- Bot sends to admin chat: photo pair + score + buttons `[Approve] [Reject] [Request Retake]`
- Admin action updates `user.photo_verified`, `level`, `exp`

### 6.3 Dependencies
- `deepface` (Facenet512 model ~200MB downloaded on first run)
- `opencv-python-headless`
- `detect-nsfw` or `nsfwjs` (Python port)

---

## 7. Gamification System

### 7.1 EXP Table (from PRD §5.1)
| Action | EXP |
|--------|-----|
| Profile step complete | 30 |
| Daily quest complete | 30 |
| Mutual match | 15 |
| Reply < 1 hour | 5 |
| Chat milestone 10/25/50 msgs | 25/50/100 |
| 7-day streak bonus | 100 |

### 7.2 Level Thresholds (cumulative)
```
L0: 0      (Unverified)
L1: 50     L2: 120    L3: 200    L4: 300    L5: 420    ← Newbie
L6: 560    ...        L15: 2720  ← Explorer
L16: 3060  ...        L30: 9920  ← Charmer
L31+: +700/level       ← Icon
```

### 7.3 Streak Logic
- Increment if user completes ≥1 quest today
- Reset to 0 if missed (no penalty to level/exp)
- Streak freeze: consume 1 `spark` or item

### 7.4 Spark (Virtual Currency)
- Earn: quest complete, level up, leaderboard weekly
- Spend: super-like, profile boost, streak freeze, cosmetic

---

## 8. Chat Relay (Open Question — Q2)

**Belum diputuskan.** Opsi:
1. **Bot relay**: user A → bot → user B (simpler, bot sees all messages)
2. **Direct chat**: deep-link `tg://user?id=...` setelah match (privacy, tapi bot tidak track message_count)
3. **Thread in group**: bot create private group per match (Telegram feature)

**Rekomendasi MVP:** Opsi 1 (bot relay) — memungkinkan tracking `message_count`, `reply_time`, ice-breaker injection, reminder. Nanti migrasi ke opsi 2/3 kalau scale.

---

## 9. Deployment (VPS GCP)

### 9.1 Services (systemd)
```
zuzu-bot.service        # python -m scripts.run_bot
zuzu-api.service        # uvicorn api.main:app --host 127.0.0.1 --port 8000
postgresql.service      # system package
redis.service           # system package
nginx.service           # reverse proxy + static (if any)
cloudflared.service     # tunnel for HTTPS Mini App
```

### 9.2 Nginx Config (sketch)
```nginx
server {
  listen 80;
  server_name bot.domain.com;
  location /webhook { proxy_pass http://127.0.0.1:8000; }  # FastAPI
  location / { proxy_pass http://127.0.0.1:8080; }         # optional admin UI
}
```

### 9.3 Cloudflare Tunnel
- `cloudflared tunnel run --token $TOKEN` → exposes `https://xxx.trycloudflare.com` → Mini App URL

---

## 10. Open Questions (Need Tuan Decision)

| # | Topic | Options | Rec |
|---|-------|---------|-----|
| Q1 | Photo verification | AI hybrid (DeepFace) vs skip | AI hybrid (per ADR-002) |
| Q2 | Chat relay | Bot relay / Direct / Group thread | Bot relay MVP |
| Q3 | Caching | Redis: user profile, quest candidates, leaderboard | Redis |
| Q4 | Rate limiting | Token bucket per user (Redis) | 30 req/min |
| Q5 | Monitoring | Prometheus + Grafana / Sentry / loguru file | loguru file + Sentry free |
| Q6 | CI/CD | GitHub Actions → build → deploy SSH | manual dulu |
| Q7 | Interest tags | Fixed taxonomy vs user-generated | Fixed (seed 50-100 tags) |
| Q8 | Leaderboard scope | Weekly, per city (radius) | Weekly, kota |
| Q9 | Admin bot | Separate bot or same bot with filter | Same bot, admin middleware |
| Q10 | Analytics events | Custom table or PostHog/GA | Custom `analytics_events` table |

---

## 11. Implementation Order (Suggested)

| Phase | Deliverable | Est. Effort |
|-------|-------------|-------------|
| 0 | Repo init, pyproject, .env, config, DB models, Alembic init | 2h |
| 1 | User/Profile CRUD + onboarding FSM (photo → bio → interests → prefs) | 4h |
| 2 | Photo verification: NSFW + DeepFace + admin review queue | 3h |
| 3 | Daily quest generation + matching (rule + content) | 4h |
| 4 | Match flow: like/pass → mutual → chat relay (bot) | 4h |
| 5 | Gamification: EXP, level, streak, spark, leaderboard | 3h |
| 6 | FastAPI Mini App endpoints + Web App frontend (HTML/JS) | 4h |
| 7 | Deployment: systemd, Nginx, Cloudflare, backup script | 2h |
| 8 | Testing, bugfix, seed data, docs | 3h |
| **Total** | **MVP ready** | **~29h** |

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| DeepFace model download fails on VPS (no internet) | Medium | High | Pre-download model, copy to VPS |
| Telegram Web App initData validation edge cases | Medium | Medium | Use `aiogram.webhook` validation helper |
| Matching quality poor (filter bubble) | High (MVP) | Medium | Log compatibility scores, plan collaborative phase |
| VPS single point of failure | High | High | Daily DB backup to GCS/S3; document restore |
| Spam/fake profiles bypass verification | Medium | High | Report button, rate limit, manual review queue |

---

## 13. Next Steps (Awaiting Tuan)

1. **Approve/reject** Photo Verification approach (AI hybrid vs skip)
2. **Decide** Chat Relay mechanism (Q2)
3. **Confirm** Interest tag taxonomy (fixed vs dynamic)
4. **Pick** Monitoring stack (Sentry free tier OK?)
5. **Go/No-go** untuk mulai Phase 0 implementation

---

*Document version: 1.0 — 2026-07-15*
*Location: `/home/filla_saputro/zuzu-bot/TECHNICAL_PLAN.md`*