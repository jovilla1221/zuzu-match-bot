# Agents Guidelines — Zuzu Match Bot

> Dokumen ini adalah **acuan dan batasan** bagi agen AI yang bekerja pada proyek ini.
> Tujuannya untuk memberikan konteks domain yang cukup tanpa mendikte detail implementasi,
> sehingga agen memiliki ruang untuk mengambil keputusan teknis yang tepat sambil tetap
> terarah dan tidak berhalusinasi.

---

## 1. Konteks Produk

### Apa produk ini?
- **Zuzu Match Bot** — bot kencan (dating bot) berbasis Telegram.
- Platform: Telegram Bot API + Telegram Web App (Mini App).
- Menggabungkan mekanisme pencarian pasangan dengan sistem gamification (level, EXP, quest, streak, currency virtual, leaderboard).

### Siapa penggunanya?
- Usia 18–32 tahun, mayoritas 20–27 tahun.
- Pengguna aktif Telegram di kota urban/sub-urban.
- Mobile-first, terbiasa dengan bot dan mini-app Telegram.
- Familiar dengan mekanisme game kasual (streak, XP, daily quest).

### Apa tujuan utama produk?
- Mengurangi ghosting dan percakapan mati di dating app.
- Membuat proses berkenalan terasa menyenangkan (gamified journey), bukan transaksional.
- Distribusi native di Telegram — tanpa install aplikasi terpisah.

---

## 2. Batasan Domain — Apa yang Boleh dan Tidak Boleh Diasumsikan

### ✅ Agen BOLEH mengasumsikan:
- Produk ini berjalan di ekosistem Telegram (Bot API, Web App/Mini App, inline mode, group chat).
- Autentikasi utama menggunakan Telegram ID (bukan email/password tradisional di MVP).
- Bahasa utama pengguna adalah Bahasa Indonesia, namun sistem harus siap untuk multi-bahasa di masa depan.
- Arsitektur data harus mencatat sinyal interaksi (like/pass, reply time, message count, quest completion) sejak awal, meskipun belum semua data dipakai di fase MVP.

### ❌ Agen TIDAK BOLEH mengasumsikan:
- Tech stack spesifik (bahasa pemrograman, framework, database) kecuali sudah secara eksplisit ditentukan oleh developer di codebase atau instruksi terpisah.
- Detail implementasi algoritma matching — pendekatan bertahap (hybrid) sudah direncanakan, tapi agen tidak boleh mengarang detail teknis algoritma yang belum diputuskan.
- Struktur database, skema API, atau arsitektur microservices/monolith — keputusan ini belum diambil kecuali ada file teknis yang secara eksplisit mendefinisikannya.
- Model pembayaran atau integrasi payment selain Telegram Stars di fase awal.
- Jumlah pengguna, skala infrastruktur, atau metrik performa yang spesifik di luar apa yang tertulis di PRD.

---

## 3. Prinsip Arsitektur yang Harus Diikuti

Agen harus mematuhi prinsip-prinsip berikut saat membuat keputusan teknis:

### 3.1 Data-First
- Rancang skema data interaksi sejak awal (like, pass, reply time, chat milestones, quest completion).
- Data ini menjadi fondasi untuk algoritma matching yang lebih canggih di fase berikutnya.
- Jangan buang sinyal — catat setiap interaksi yang berpotensi menjadi training data.

### 3.2 Modular & Bertahap
- Arsitektur harus mendukung pengembangan bertahap sesuai fase di PRD:
  - **MVP**: Onboarding, profiling, quest-based matching, level/EXP dasar, chat, daily streak.
  - **Fase 2**: Virtual currency (Spark), leaderboard, monetisasi.
  - **Fase 3**: Fitur inovatif (Blind Date Roulette, Squad Quest, dll).
- Komponen harus bisa ditambahkan tanpa rewrite besar pada komponen yang sudah ada.

### 3.3 Telegram-Native
- Manfaatkan fitur bawaan Telegram secara maksimal: inline buttons, callback queries, inline mode, deep linking, group/channel features, Telegram Stars.
- Jangan membangun ulang apa yang sudah disediakan Telegram secara native.
- UX harus terasa natural bagi pengguna Telegram, bukan seperti aplikasi web yang dipaksakan ke dalam chat.

### 3.4 Fairness by Design
- Sistem gamification dan monetisasi TIDAK boleh menciptakan keunggulan matching yang tidak adil ("pay-to-win love").
- Virtual currency (Spark) hanya untuk kenyamanan, kosmetik, dan percepatan — bukan untuk menjual probabilitas match.
- Level tidak boleh dipakai untuk "membeli" keunggulan matching.

---

## 4. Fitur Inti yang Menjadi Scope

Berikut adalah domain fitur yang menjadi konteks kerja agen. Agen boleh bekerja pada area ini, namun harus merujuk ke PRD untuk detail bisnis logic yang spesifik.

| Domain Fitur | Deskripsi Singkat |
|---|---|
| **Onboarding** | Registrasi via `/start`, progressive profiling bertahap, setiap tahap memberi EXP |
| **Profiling** | Foto, bio, tag minat, preferensi; profile completeness terhubung ke EXP |
| **Quest-Based Matching** | Penemuan profil dibungkus sebagai quest harian (5–10 kandidat/hari) |
| **Matching Algorithm** | Hybrid bertahap: rule-based → content-based → collaborative → embedding → RL |
| **Sistem Level & EXP** | EXP dari berbagai aksi, level membuka fitur/kosmetik, tier system |
| **Chat System** | Chat via bot relay, ice-breaker otomatis, reply streak tracker, reminder |
| **Daily Streak** | Streak dari aktivitas harian, streak freeze tersedia, reset tidak menghapus level |
| **Virtual Currency (Spark)** | Didapat dari quest/level, digunakan untuk boost/freeze/super-like |
| **Leaderboard** | Mingguan, regional, multi-kategori (Most Active, Best Conversationalist, Rising Star) |
| **Monetisasi** | Freemium + Telegram Stars + Subscription + Cosmetic Store + Season Pass |

---

## 5. Aturan Perilaku Agen

### 5.1 Jangan Mengarang
- Jika informasi tidak tersedia di PRD atau codebase, **tanyakan** — jangan buat asumsi sendiri.
- Jangan mengarang nama API, endpoint, atau nama tabel database yang belum didefinisikan.
- Jangan membuat keputusan arsitektural besar (pilihan database, framework, deployment strategy) tanpa konfirmasi.

### 5.2 Selalu Merujuk ke Sumber
- Saat membuat keputusan, rujuk ke PRD.md sebagai sumber kebenaran untuk business logic.
- Jika ada file teknis lain di repo (misalnya schema, config, atau dokumen arsitektur), prioritaskan file tersebut di atas asumsi.
- Jika ada kontradiksi antara PRD dan codebase yang sudah ada, tanyakan klarifikasi.

### 5.3 Keamanan Tidak Boleh Dikompromikan
- Semua data pengguna (profil, foto, percakapan, preferensi) adalah data sensitif.
- Validasi input dari pengguna di setiap titik masuk.
- Ikuti prinsip least privilege untuk akses database dan API.
- Jangan pernah hardcode secret, API key, atau token di source code.
- Foto dan media pengguna harus divalidasi (tipe file, ukuran) sebelum disimpan.

### 5.4 Gamification Harus Konsisten
- Setiap tabel EXP, level threshold, dan reward yang tertulis di PRD harus dianggap sebagai **referensi awal** yang bisa disesuaikan.
- Jangan mengarang nilai EXP atau mekanisme reward baru tanpa konteks.
- Tier system: Newbie (1–5) → Explorer (6–15) → Charmer (16–30) → Icon (31+).

### 5.5 UX Harus Telegram-First
- Interaksi utama via inline button dan callback, bukan perintah teks panjang.
- Pesan bot harus ringkas, friendly, dan bergaya percakapan (bukan formal/kaku).
- Animasi dan perayaan (match event, level up) harus memanfaatkan media Telegram (sticker, GIF, formatted text).

---

## 6. Hal-Hal yang Belum Diputuskan

Agen **harus bertanya** sebelum mengambil keputusan pada topik berikut:

- [ ] Tech stack backend (bahasa, framework, runtime)
- [ ] Database yang digunakan (SQL vs NoSQL, provider spesifik)
- [ ] Arsitektur deployment (monolith vs microservices, cloud provider)
- [ ] Strategi hosting dan scaling
- [ ] Detail implementasi verifikasi foto (manual review vs AI-based)
- [ ] Mekanisme chat relay spesifik (direct Telegram chat vs in-bot thread)
- [ ] Detail format data profil (field lengkap, validasi rules)
- [ ] Strategi caching dan rate limiting
- [ ] Monitoring dan observability stack
- [ ] CI/CD pipeline

---

## 7. Konvensi Penamaan & Organisasi

Sampai konvensi resmi ditentukan oleh developer, agen harus:
- Menggunakan penamaan yang deskriptif dan konsisten (camelCase atau snake_case — ikuti konvensi bahasa yang dipilih).
- Memisahkan concern secara logis (handler, service, repository/data layer, model).
- Menulis komentar untuk logic bisnis yang kompleks.
- Menyertakan docstring/JSDoc untuk fungsi publik.
- Tidak mencampur bahasa (pilih satu: Bahasa Indonesia atau English) untuk penamaan variabel dan fungsi — defaultnya English.

---

## 8. Testing & Verifikasi

- Setiap fitur baru harus disertai minimal unit test untuk business logic inti.
- Agen harus memverifikasi bahwa kode bisa di-build/run tanpa error sebelum menyatakan selesai.
- Jangan skip error handling — selalu tangani edge case yang jelas terlihat.
- Untuk server/service yang dijalankan saat testing, gunakan localhost/127.0.0.1 — **JANGAN** gunakan 0.0.0.0.

---

## 9. Referensi Utama

| Dokumen | Lokasi | Fungsi |
|---|---|---|
| PRD (Product Requirements Document) | `PRD.md` | Sumber kebenaran untuk business logic, fitur, dan strategi produk |
| Agents Guidelines (dokumen ini) | `agents.md` | Batasan dan acuan perilaku agen AI |

> **Catatan:** Seiring proyek berkembang, dokumen teknis lain (architecture decision records, API spec, database schema) akan ditambahkan. Agen harus selalu memeriksa apakah ada dokumen baru sebelum membuat asumsi.
