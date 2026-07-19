# ADR-002: Photo Verification — AI-Based Feasibility

**Status:** Proposed (2026-07-15)
**Decider:** Tuan
**Context:** Zuzu Match Bot perlu verifikasi pengguna adalah manusia sungguhan dan fotonya sesuai dengan identitasnya (mencegah catfishing, fake profile). agents.md belum menentukan mekanisme.

---

## Problem

Bagaimana cara memverifikasi bahwa pengguna yang upload foto profil benar-benar orang yang sama di foto, tanpa engineering cost yang besar di MVP?

---

## Analisis Akurasi AI-Verifikasi

### Skenario Live: User Upload Foto → Selfie Check

Ada 3 dimensi verifikasi yang relevan:

#### 1. Face Matching (Apakah foto selfie = foto profil?)
| Approach | Akurasi (benchmark publik LFW/CFP) | Kebutuhan Compute | Latency |
|----------|--------------------------------------|-------------------|---------|
| **DeepFace + Facenet512** | 98.5% | CPU saja, 2-5s/foto | Medium |
| **InsightFace** | 99.4% | GPU recommended | Fast |
| **MediaPipe Face Mesh + cosine sim.** | ~92% | CPU, realtime | Very fast |
| **AWS Rekognition** | ~99% | API call | Fast |
| **Google Cloud Vision** | ~99% | API call | Fast |

#### 2. Liveness Detection (Apakah foto bukan foto dari foto / deepfake?)
| Approach | Akurasi | Notes |
|----------|---------|-------|
| **MediaPipe + blink detection** | ~90% | Face spoof: user diminta kedip, gerak kepala |
| **Deep lace-based (CNN classifier)** | ~95% | Butuh training dataset |
| **AWS Rekognition Face Liveness** | ~99% | Video-based, 5 detik |

#### 3. Fake Profile Detection (Apakah foto dicuri dari internet?)
| Approach | Akurasi | Notes |
|----------|---------|-------|
| **Google Reverse Image Search (unofficial)** | ~85% | Butuh scraping, unreliable |
| **TinEye API** | ~95%+ | Berbayar, REST API |
| **Custom embedding + laion5B index** | Overkill | Jangan di MVP |

---

## Rekomendasi untuk MVP

### Hybrid Approach: Automated + Manual Review

**✅ Face Matching**: **DeepFace (Facenet512)** — di-host di VPS, CPU-only, 2-5s per foto.

**✅ Liveness Sederhana**: Setelah user upload foto profil, minta selfie dengan **pose unik** (misal "tunjuk jari kelingking ke kiri") — jadi mirror test + challenge-response. Tidak perlu model liveness terpisah.

**✅ NSFW Filter**: Library `detect-nsfw` atau `nsfwjs` untuk reject foto tidak pantas.

**❌ Skip di MVP**: Reverse image search (mahal, engineering heavy). Ganti dengan report button dan queue manual review.

### Flow MVP
```
User upload foto profil
→ NSFW filter (pass/reject langsung)
→ User upload selfie dengan pose spesifik
→ DeepFace compare selfie vs foto profil
→ Match score > 70% → VERIFIED, naik Level 1
→ Match score 50-70% → QUEUE manual review (admin bot)
→ Match score < 50% → REJECT, coba lagi
```

### Tabel Realistis
| Situasi | Probabilitas | Action |
|---------|------------|--------|
| User asli, foto jelas | → 95% auto-verified |
| User asli, foto gelap/ambigu | → 3-4% manual review, kebanyakan approve |
| Catfish pakai foto orang | → DeepFace deteksi mismatch, reject/queue |
| AI-generated photo | → Tidak terdeteksi sebagai selfie asli (error face detection → minta ulang) |
| Spam bot upload random | → NSFW filter catch + face detection gagal |

---

## Kesimpulan Akurasi

**AI-based photo verification cukup akurat untuk MVP** dengan pendekatan hybrid:

> Face matching DeepFace (CPU) + NSFW filter + challenge-response selfie + manual review queue untuk edge case.

Tapi **tidak 100%** — ada false positive (user asli ditolak karena foto kurang jelas) dan false negative (catfish yang pintar lolos). Risiko ini dimitigasi dengan:
1. Clear instruction saat minta selfie ("selfie dengan pose spesifik, bukan foto dari kamar")
2. Retry mechanism (kesempatan kedua)
3. Manual review queue via admin bot
4. Report system: user lain bisa report fake profile

**Lebih baik user asli masuk queue manual (sedikit delay) daripada catfish auto-approved.**

---

## Alternatif Pro

Kalau Tuan **tidak mau** self-verify AI-based:

| Alternatif | Pro | Kontra |
|------------|-----|--------|
| **Manual review semua** | Paling akurat | Scalability problem: butuh admin |
| **Sosial verification** (konek IG/Twitter) | Sudah selesai di platform lain | Butuh OAuth, engineering heavy |
| **Phone OTP** | Mencegah multi-akun | Butuh gateway SMS/PWA |
| **No verification (trust-based)** | Zero friction | Pasti kena spam bot + catfish |

---

## Keputusan

Menunggu Tuan: apakah ingin lanjut dengan **AI-verifikasi hybrid** (DeepFace + selfie challenge + manual review queue) di MVP?

### Jika Ya → impact:
- install `deepface` (pip, ~200MB model download)
- Tambah endpoint upload foto + selfie di FastAPI
- Admin bot panel untuk review queue
- Sesi onboarding: foto → selfie → verify → Level 1

### Jika Tidak → fallback:
- Upload foto biasa tanpa verifikasi
- Trust-based + report button
- (Verifikasi ditunda ke fase 2)

---

## Related
- PRD.md §4.1 — Verifikasi foto sederhana sebagai syarat Level 1
- agents.md §6 butir 4 — Detail implementasi verifikasi foto belum diputuskan
- ADR-001 §5 Q1 — Dibahas terpisah
