# ADR-001: Tech Stack — Backend, Database, Deployment, Matching

**Status:** Proposed (2026-07-15)
**Decider:** Tuan
**Context:** MVP Zuzu Match Bot — fase 1 (onboarding, profiling, quest-based matching, level/EXP dasar, chat, daily streak)

---

## 1. Backend Stack

### Decision
- **Language:** Python 3.11+
- **Telegram framework:** aiogram 3.x (async)
- **HTTP/API layer:** FastAPI (untuk Web App / Mini App callbacks + admin endpoints)
- **ORM:** SQLAlchemy 2.0 (async) + asyncpg driver
- **Task queue:** Celery + Redis (atau asyncio background tasks untuk MVP awal)
- **Validation:** Pydantic v2

### Rationale
- aiogram async-native, cocok untuk bot Telegram dengan tinggi concurrency (user typing, callback queries)
- FastAPI terpisah dari bot loop — bot handle updates, FastAPI handle Web App POST data (profile foto, bio)
- SQLAlchemy async avoid blocking DB calls di event loop

### Consequences
✅ Async performant untuk Telegram update handling
✅ Separation of concerns: bot (aiogram) vs web (FastAPI)
✅ Type-safe dengan Pydantic
❌ Dua event loop need care (bot loop vs FastAPI uvicorn) — jalanin sebagai 2 proses terpisah
❌ Learning curve aiogram FSM untuk onboarding flow

---

## 2. Database

### Decision
- **Primary DB:** PostgreSQL 15+ (di VPS yang sama)
- **Cache/Queue:** Redis (same VPS)
- **JSONB column** untuk sinyal interaksi (like/pass, reply time, chat milestones) — fleksibel untuk fase embedding nanti

### Schema (early draft — NOT final)
```
users (telegram_id PK, username, photo_verified, level, exp, streak, ...)
profiles (user_id FK, bio, interests[], age, location, preferences JSONB)
matches (user_a, user_b, status, created_at)
interactions (user_id, target_id, action, timestamp, metadata JSONB)  ← training data foundation
quests (user_id, date, candidates[], completed)
```

### Rationale
- ACID untuk data user profile & match (consistency penting)
- JSONB untuk sinyal interaksi — tidak perlu ALTER TABLE setiap tambah metrik
- PostgreSQL di VPS yang sama = latency rendah, tidak ada egress cost

### Consequences
✅ Relational integrity untuk match/user
✅ JSONB fleksibel untuk ML signals masa depan
✅ Co-located dengan app = cepat
❌ Manual backup needed (VPS tidak managed DB)
❌ Scaling horizontal perlu replikasi nanti

---

## 3. Deployment

### Decision
- **Target:** VPS GCP yang sama (IP 34.101.158.162, OS user `filla_saputro`)
- **Process manager:** systemd (bot service, FastAPI service)
- **Reverse proxy:** Nginx + Cloudflare Tunnel (untuk Web App HTTPS)
- **Container:** Opsional — MVP jalanin bare metal Python venv dulu, Docker saat stabil
- **DB:** PostgreSQL + Redis di-install di VPS, bukan managed service

### Rationale
- Sudah punya VPS GCP → tidak perlu cloud spend tambahan
- systemd reliable untuk long-running bot
- Cloudflare Tunnel → Web App bisa HTTPS tanpa expose port

### Consequences
✅ Zero additional infra cost
✅ Full control
❌ Manual backup & monitoring
❌ Single point of failure (VPS down = bot down)
❌ Scaling = vertical upgrade VPS

---

## 4. Matching Algorithm

### Decision (sesuai PRD §5.2 — Hybrid Bertahap)
- **MVP (Fase 1):** Rule-Based + Content-Based Filtering
  - Rule-Based: filter hard (usia range, lokasi radius, gender preference)
  - Content-Based: cosine similarity tag minat (interests[])
  - Compatibility score = weighted sum (tag overlap + rule pass)
- **Fase 2 (Growth):** + Collaborative Filtering (user-user similarity dari `interactions` table)
- **Fase 3 (Scale):** + Embedding/NLP matching (bio + quest answers → vector)
- **Fase 4 (Optimization):** + Reinforcement Learning (engagement signals)

### Implementation Notes MVP
- Compatibility score dihitung di Python (numpy) atau SQL query dengan JSONB ops
- Candidate pool: query `profiles` dengan rule filter, rank by content score, ambil top 5-10 per hari
- Setiap keputusan user (like/pass) dicatat di `interactions` → fondasi data untuk fase 2+

### Consequences
✅ Explainable ("kalian match karena sama-suka hiking") — build trust di MVP
✅ Cold-start friendly (tidak butuh data historis)
✅ Data-first: interactions table sejak hari 1
❌ Belum "AI" betulan di MVP — butuh volume data untuk fase lanjut
❌ Filter bubble risk (hanya ketemu yang mirip) — mitigate di fase 2 dengan collaborative

---

## Open Questions (belum diputuskan — tanyakan Tuan)

| # | Topic | Status |
|---|-------|--------|
| Q1 | Photo verification method (manual vs AI) | **DIBAHAS TERPISAH** — lihat ADR-002 |
| Q2 | Chat relay mechanism | Belum |
| Q3 | Caching strategy | Belum |
| Q4 | Rate limiting | Belum |
| Q5 | Monitoring/observability | Belum |
| Q6 | CI/CD pipeline | Belum |

---

## Related
- PRD.md §5 (Algoritma Matching)
- agents.md §6 (Hal yang belum diputuskan)
- ADR-002: Photo Verification (AI-based) — pending
