# Product Requirements Document (PRD)
# Telegram Dating Bot dengan Sistem Gamification

**Nama Kerja Proyek:** Zuzu Match Bot
**Platform:** Telegram (Bot API + Telegram Web App / Mini App)
**Dokumen disusun oleh:** Senior Product Manager & UX Strategist
**Versi:** 1.0

---

## 1. Overview & Vision

### 1.1 Ringkasan Produk
Zuzu Match adalah bot kencan (dating bot) di Telegram yang menggabungkan mekanisme pencarian jodoh berbasis minat dan lokasi dengan lapisan gamification penuh — level, EXP, quest harian, streak, virtual currency, dan leaderboard. Alih-alih pengalaman swipe-dan-lupa seperti aplikasi dating konvensional, Zuzu Match memperlakukan proses berkenalan sebagai sebuah "perjalanan" (journey) yang terstruktur dan menyenangkan, di mana setiap interaksi kecil punya nilai dan progres yang terlihat.

### 1.2 Masalah yang Dipecahkan
Aplikasi dating konvensional (Tinder, Bumble, dll) memiliki beberapa masalah kronis yang divalidasi oleh riset UX industri:

| Masalah | Dampak pada Pengguna |
|---|---|
| **Ghosting tinggi** | Pengguna kehilangan minat setelah match karena tidak ada dorongan untuk melanjutkan percakapan |
| **Awkward opener** | Kebanyakan percakapan mati di 3 pesan pertama karena basa-basi generik ("hai", "apa kabar") |
| **Fatigue swipe** | Swiping tanpa umpan balik yang bermakna membuat pengguna cepat bosan dan churn |
| **Kurangnya insentif untuk konsisten** | Tidak ada alasan untuk kembali membuka aplikasi setiap hari jika tidak ada notifikasi match baru |
| **Onboarding di aplikasi terpisah** | Perlu install aplikasi baru, verifikasi ulang, membuat friksi akuisisi pengguna |

Zuzu Match menjawab masalah ini dengan native distribution Telegram (tanpa install aplikasi terpisah) dan sistem gamification yang mengubah "usaha berkenalan" menjadi progres yang bisa dilihat, dirayakan, dan dikompetisikan.

### 1.3 Visi Jangka Panjang
Menjadikan Zuzu Match sebagai **"social dating layer" nomor satu di ekosistem Telegram** — bukan sekadar bot pencari jodoh, tetapi sebuah ekosistem sosial mini (mini-app) tempat pengguna membangun reputasi, komunitas, dan koneksi romantis melalui interaksi yang terasa seperti bermain game ringan, bukan seperti "berjualan diri sendiri" di marketplace jodoh.

---

## 2. Target Audience

### 2.1 Demografi
- **Usia:** 18–32 tahun (inti: 20–27 tahun)
- **Lokasi:** Kota-kota urban/sub-urban dengan penetrasi Telegram tinggi (Indonesia, Rusia, Timur Tengah, Asia Tenggara, Eropa Timur, komunitas crypto/tech global)
- **Status:** Mahasiswa, pekerja muda, freelancer, digital native
- **Device:** Mayoritas mobile-first, terbiasa dengan mini-app/Web App di dalam Telegram

### 2.2 Psikografi
- Terbiasa dengan game mobile kasual (Duolingo streak, Genshin daily login, dsb) — sudah paham dan menyukai mekanisme reward loop
- Skeptis terhadap aplikasi dating "serius" yang terasa transaksional
- Menyukai humor, referensi meme, dan interaksi ringan sebelum berkomitmen pada percakapan yang lebih dalam
- Mencari validasi sosial ringan (level, badge, leaderboard) sebagai bagian dari motivasi, bukan hanya mencari pasangan semata
- Nyaman dengan komunitas berbasis grup/channel Telegram

### 2.3 Perilaku di Telegram
- Sudah menggunakan Telegram sebagai aplikasi chat utama, sering tergabung di banyak grup dan channel
- Terbiasa berinteraksi dengan bot (bot game, bot util, bot trading) sehingga tidak asing dengan UX berbasis inline button dan command
- Cenderung membuka Telegram berkali-kali sehari — kanal distribusi dengan frekuensi tinggi, cocok untuk mekanik streak harian

---

## 3. User Personas

### Persona 1: "Dinda, si Pencari Koneksi Santai"
- **Usia:** 23 tahun, Content Creator/Freelancer di kota besar
- **Tujuan:** Mencari koneksi romantis tanpa tekanan berlebihan, menikmati proses berkenalan sebagai hiburan
- **Frustrasi:** Bosan dengan swipe app yang terasa seperti "belanja orang", ingin sesuatu yang lebih playful
- **Perilaku Kunci:** Aktif di beberapa grup Telegram komunitas hobi, senang mengoleksi badge/achievement di aplikasi lain
- **Kebutuhan Produk:** Quest harian yang ringan, ice-breaker otomatis, tidak perlu effort besar untuk mulai chat

### Persona 2: "Rangga, si Kompetitif Achiever"
- **Usia:** 26 tahun, Software Engineer / Web3 enthusiast
- **Tujuan:** Ingin merasa "menang" dalam prosesnya — suka progres terukur dan status sosial
- **Frustrasi:** Merasa dating app biasa tidak memberi umpan balik atas usahanya (berapa banyak yang melihat profil, dsb)
- **Perilaku Kunci:** Rajin streak di Duolingo, main game leaderboard, terbiasa dengan sistem XP dan crafting
- **Kebutuhan Produk:** Leaderboard, level visibility, virtual currency yang bisa ditukar boost profil

### Persona 3: "Sarah, si Pemula yang Cemas Sosial"
- **Usia:** 20 tahun, Mahasiswa
- **Tujuan:** Ingin berlatih berkenalan tanpa tekanan sosial tinggi, mencari lingkungan yang "aman" dan terstruktur
- **Frustrasi:** Merasa canggung memulai obrolan, sering tidak tahu harus bilang apa
- **Perilaku Kunci:** Jarang memulai chat duluan, tapi responsif jika diberi prompt/template
- **Kebutuhan Produk:** Quest ice-breaker terpandu (conversation starter otomatis), sistem yang tidak menghakimi bila lambat merespons

---

## 4. Core Features (MVP)

### 4.1 Onboarding
- Mulai via `/start`, disambut dengan narasi ringan bergaya "onboarding game" (bukan form kaku)
- Login/verifikasi otomatis via Telegram ID (tanpa perlu OTP tambahan di MVP)
- Progressive profiling: data diminta bertahap (foto → bio singkat → minat → preferensi pencarian), masing-masing tahap memberi EXP awal agar pengguna merasakan reward loop sejak menit pertama
- Verifikasi foto sederhana (selfie check / anti-fake profile) sebagai syarat naik ke Level 1

### 4.2 Profiling
- Profil terdiri dari: foto (1–6), bio, minat (tag-based, bukan free text agar mudah di-matching), preferensi usia/lokasi/gender
- "Profile Completeness Score" ditampilkan sebagai progress bar — bukan sekadar persentase, tapi terhubung ke EXP
- Badge kecil otomatis untuk profil lengkap ("Verified", "Storyteller" jika bio > panjang tertentu, dll)

### 4.3 Match-Making System berbasis Quest/Game
- Alih-alih swipe biasa, penemuan profil dibungkus sebagai **"Quest Harian"**: pengguna diberi 5–10 kandidat per hari sebagai bagian dari misi harian
- Setiap keputusan (like/pass) memberi EXP kecil; menyelesaikan quest harian (misal: menilai semua kandidat hari itu) memberi bonus EXP + currency
- Mutual like memicu "Match Event" dengan animasi/pesan perayaan (bukan notifikasi datar)
- Compatibility score ditampilkan berbasis kecocokan tag minat, bukan hanya foto

### 4.4 Sistem Level & EXP
- EXP didapat dari: menyelesaikan profil, quest harian, membalas chat dalam rentang waktu tertentu, menyelesaikan "conversation milestone" (misal 10 pesan terkirim di satu match)
- Level membuka fitur/kosmetik: filter pencarian lebih spesifik, badge visual di profil, jumlah quest tambahan per hari
- Level TIDAK dipakai untuk "membeli" keunggulan matching yang tidak adil (lihat prinsip fairness di bagian Monetization)

### 4.5 Chat System
- Chat terjadi langsung di dalam Telegram (native chat experience via bot relay atau deep-link ke percakapan)
- Ice-breaker otomatis: setelah match, bot menawarkan 3 opsi starter question bertema (random dari minat bersama)
- "Reply streak" tracker antar dua pengguna untuk mendorong keberlanjutan obrolan (lihat detail di gamification)
- Reminder halus (bukan spam) jika sebuah match tidak dibalas dalam 24–48 jam

---

## 5. Algoritma Matching Berbasis AI

Salah satu keputusan teknis paling krusial di produk ini adalah memilih pendekatan algoritma yang dipakai untuk merekomendasikan kandidat di setiap Quest Harian. Berikut analisis beberapa pendekatan yang relevan, beserta rekomendasi.

### 5.1 Perbandingan Pendekatan Algoritma

| Pendekatan | Cara Kerja | Kelebihan | Kekurangan | Relevansi untuk Zuzu Match |
|---|---|---|---|---|
| **Content-Based Filtering** | Mencocokkan berdasarkan kemiripan atribut eksplisit (tag minat, usia, lokasi, preferensi) | Mudah diimplementasikan, tidak butuh data historis, hasil mudah dijelaskan ke user | Rentan "filter bubble" — user hanya bertemu orang yang sangat mirip dirinya, kurang eksploratif | Cocok untuk **cold-start** (user baru) karena belum ada data interaksi |
| **Collaborative Filtering** | Merekomendasikan berdasarkan pola perilaku user lain yang mirip ("orang yang like X juga like Y") | Menangkap pola preferensi tersembunyi yang tidak eksplisit ditulis user | Butuh volume data interaksi besar (like/pass) agar akurat, lemah di awal (cold-start) | Efektif setelah user based bertumbuh, kurang cocok di fase awal MVP |
| **Embedding/NLP-Based Matching** | Bio, jawaban quest, dan gaya chat diubah jadi vector embedding (mis. via model bahasa), kemiripan dihitung via cosine similarity | Bisa menangkap "kecocokan gaya komunikasi", bukan sekadar tag minat; menangkap nuansa yang tidak bisa dicentang di form | Butuh biaya komputasi lebih tinggi, perlu data teks yang cukup (bio, jawaban quest) | Sangat relevan karena Zuzu Match punya banyak teks natural dari quest & chat sebagai sumber sinyal |
| **Reinforcement Learning berbasis Engagement** | Model belajar dari sinyal implisit — reply-rate, panjang percakapan, kecepatan balas — untuk mengoptimalkan match yang menghasilkan percakapan berkelanjutan | Optimasi langsung ke tujuan bisnis (mengurangi ghosting, bukan sekadar mutual like) | Kompleks, butuh eksperimen A/B matang, risiko bias eksploitasi sinyal jangka pendek | Selaras dengan visi anti-ghosting produk, tapi baiknya diterapkan di fase lanjutan setelah data cukup |
| **Rule-Based / Heuristic** | Filter keras berdasarkan preferensi eksplisit (usia, lokasi, gender) sebelum algoritma lain jalan | Menjamin batasan dasar (mis. rentang usia) selalu dihormati | Tidak "cerdas", hanya penyaring awal | Tetap dibutuhkan sebagai **layer penyaring pertama**, bukan pengganti algoritma utama |

### 5.2 Rekomendasi: Pendekatan Hybrid Bertahap

Direkomendasikan pendekatan **hybrid** yang berkembang seiring maturitas data, bukan satu algoritma tunggal sejak awal:

1. **Fase MVP (data minim):**
   Rule-Based filtering (usia, lokasi, gender, preferensi eksplisit) dikombinasikan dengan Content-Based Filtering (kemiripan tag minat). Cukup ringan secara komputasi dan tidak butuh volume data besar untuk mulai berfungsi dengan baik.

2. **Fase Growth (setelah cukup data interaksi, umumnya beberapa ribu user aktif):**
   Tambahkan Collaborative Filtering di atas hasil Content-Based, untuk mulai menangkap pola preferensi implisit yang tidak tertulis di profil.

3. **Fase Scale (data percakapan & quest sudah kaya):**
   Tambahkan Embedding/NLP-Based Matching menggunakan teks dari bio dan jawaban quest, untuk menangkap kecocokan gaya komunikasi — ini yang membedakan Zuzu Match dari dating app biasa, karena datanya berasal dari interaksi quest yang kaya konteks, bukan sekadar swipe kosong.

4. **Fase Optimasi Lanjutan:**
   Terapkan lapisan Reinforcement Learning berbasis sinyal engagement (reply-rate, kelangsungan chat) untuk mengoptimalkan langsung ke metrik bisnis inti — mengurangi ghosting — bukan hanya memaksimalkan jumlah mutual like.

### 5.3 Mengapa Pendekatan Bertahap, Bukan Langsung "AI Penuh" di MVP
- Model yang kompleks (embedding, RL) butuh volume data yang belum ada di hari pertama peluncuran — membangunnya terlalu awal berisiko menghasilkan rekomendasi buruk karena data latih tidak representatif.
- Rule-based + content-based di awal lebih mudah di-debug dan hasilnya bisa dijelaskan ke user ("kalian match karena sama-sama suka hiking"), yang penting untuk membangun trust di fase awal.
- Sinyal gamification (EXP, quest completion, reply speed) yang dikumpulkan sejak MVP justru menjadi data training yang berharga untuk fase Collaborative Filtering dan RL nantinya — sehingga arsitektur data sebaiknya dirancang untuk mencatat sinyal ini sejak awal meski algoritmanya belum dipakai.

### 5.4 Catatan Teknis untuk Tim Engineering
- Rancang skema data interaksi (like/pass, reply time, message count per match, quest completion) sejak MVP, meskipun belum dipakai algoritma canggih — ini adalah fondasi dataset untuk model masa depan.
- Untuk embedding teks, evaluasi model embedding yang efisien secara biaya untuk skala produksi, dengan mempertimbangkan trade-off antara akurasi dan latensi/biaya inferensi.
- Terapkan monitoring bias: pastikan algoritma tidak secara sistematis mengurangi visibilitas kelompok tertentu (mis. berdasarkan gender ratio yang tidak seimbang di early user base).

---

## 6. Gamification Mechanics

### 5.1 Sistem Leveling & EXP
| Aksi | EXP |
|---|---|
| Melengkapi profil (per tahap) | 20–50 EXP |
| Menyelesaikan quest harian | 30 EXP |
| Mendapat mutual match | 15 EXP |
| Membalas pesan dalam <1 jam | 5 EXP |
| Mencapai milestone chat (10/25/50 pesan) | 25–100 EXP |
| Menjaga streak login 7 hari berturut-turut | 100 EXP bonus |

- Level dibagi dalam tier: **Newbie (1–5) → Explorer (6–15) → Charmer (16–30) → Icon (31+)**
- Tiap naik level memicu perayaan visual singkat (mendorong dopamine hit) dan membuka 1 fitur/kosmetik kecil

### 5.2 Daily Streak
- Streak dihitung dari: membuka bot dan menyelesaikan minimal 1 quest per hari
- Streak yang terputus tidak menghapus level, hanya mereset counter streak — menghindari rasa "dihukum" berlebihan yang bisa memicu churn
- Streak Freeze: item yang bisa didapat gratis (dari quest) atau dibeli, agar pengguna tidak panik kehilangan streak karena satu hari absen (terinspirasi dari mekanik Duolingo)

### 5.3 Virtual Currency ("Spark")
- Diperoleh dari: menyelesaikan quest, naik level, event komunitas (leaderboard mingguan)
- Digunakan untuk: super-like terbatas, profile boost sementara (visibilitas lebih tinggi di antrean quest orang lain), buka 1 filter pencarian premium sementara, streak freeze
- **Prinsip penting:** Spark tidak bisa dipakai untuk "membeli level" atau melihat siapa yang like Anda secara instan tanpa usaha — currency hanya mempercepat/mempercantik pengalaman, bukan menjual keunggulan matching yang tidak adil

### 5.4 Leaderboard
- Leaderboard mingguan berbasis EXP di dalam radius kota/region (bukan global, agar tetap relevan secara lokal)
- Kategori leaderboard ganda agar tidak hanya menghargai "paling populer": **Most Active**, **Best Conversationalist** (berdasarkan reply-rate & panjang percakapan), **Rising Star** (user baru dengan progres tercepat)
- Top 10 mingguan mendapat badge kosmetik + bonus Spark — dijaga agar tetap ringan (fun), tidak menciptakan tekanan sosial berlebihan atau rasa "kalah"

---

## 7. User Flow

```
1. User membuka bot via /start
2. Onboarding singkat (narasi + progressive profiling bertahap, tiap tahap +EXP)
3. Verifikasi foto dasar → naik ke Level 1
4. Bot menyajikan Quest Harian pertama (5–10 profil kandidat)
5. User menilai kandidat (like/pass) → EXP bertambah tiap aksi
6. Terjadi Mutual Like → "Match Event" (animasi/pesan perayaan)
7. Bot menawarkan 3 ice-breaker starter question bertema minat bersama
8. User memilih/mengirim starter → percakapan dimulai di thread chat bot
9. Selama chat berlangsung, milestone (10/25/50 pesan) memicu bonus EXP
10. Jika user menyelesaikan seluruh quest harian → bonus EXP + Spark, streak +1
11. Reminder halus jika match tidak dibalas dalam 24–48 jam
12. Ringkasan mingguan: level naik, posisi leaderboard, quest baru tersedia
```

---

## 8. Monetization Strategy

Prinsip utama: **jangan pernah menjual keunggulan matching yang membuat pengalaman gratis terasa tidak adil ("pay-to-win love")**. Monetisasi difokuskan pada kenyamanan, kosmetik, dan percepatan — bukan probabilitas mendapatkan pasangan.

| Model | Deskripsi | Contoh Item |
|---|---|---|
| **Freemium** | Fitur inti (quest harian, matching, chat, leveling) gratis selamanya | Quest harian standar, chat tanpa batas dengan match yang sudah terjadi |
| **Telegram Stars** | Mata uang native Telegram untuk transaksi mikro tanpa perlu payment gateway eksternal | Beli Spark tambahan, buka slot quest ekstra harian, streak freeze instan |
| **Subscription (Premium Pass)** | Langganan bulanan untuk pengguna yang lebih serius | Quest harian lebih banyak, filter pencarian lanjutan, badge kosmetik eksklusif, lihat siapa yang menyelesaikan quest tentang Anda (bukan siapa yang like — tetap menjaga fairness) |
| **Cosmetic Store** | Item visual murni, tidak memengaruhi peluang match | Frame profil, animasi match event custom, tema chat |
| **Event/Season Pass** | Musiman (mis. "Season of Connection"), quest tematik dengan reward eksklusif | Badge musiman, currency bonus |

**Yang sengaja TIDAK dijual:** melihat siapa yang like Anda secara instan tanpa usaha (agar tidak menciptakan skenario "beli untuk lihat semua orang yang tertarik", yang secara industri terbukti memicu perilaku dating app yang predatory/tidak sehat), serta prioritas tampil di depan antrean orang lain secara permanen.

---

## 9. Success Metrics (KPI)

| Kategori | Metrik | Target Indikatif (3 bulan pasca-launch) |
|---|---|---|
| **Aktivasi** | % user yang menyelesaikan onboarding penuh | >70% |
| **Engagement** | DAU/MAU ratio | >35% |
| **Retensi** | D1 / D7 / D30 retention | 50% / 25% / 12% |
| **Gamification Health** | Rata-rata streak length | >4 hari |
| **Matching** | Jumlah mutual match per user aktif/minggu | >3 |
| **Percakapan** | % match yang berlanjut >10 pesan (proxy anti-ghosting) | >40% |
| **Monetisasi** | Konversi free-to-paid | 3–5% |
| **Monetisasi** | ARPPU (Average Revenue Per Paying User) bulanan | Ditentukan per market |
| **Kepuasan** | NPS pengguna aktif | >30 |
| **Keamanan/Trust** | Tingkat laporan profil palsu per 1000 user | Serendah mungkin, dipantau ketat |

---

## 10. Rekomendasi 5 Fitur Baru Inovatif (Beyond MVP)

Fitur-fitur berikut dirancang untuk memperdalam gamification dan memanfaatkan keunggulan unik ekosistem Telegram yang tidak mudah direplikasi oleh aplikasi dating berbasis native app biasa.

### 9.1 "Blind Date Roulette" via Telegram Group Voice/Video Chat
**Konsep:** Fitur mingguan di mana bot mencocokkan 2 pengguna secara acak (berdasarkan minimum compatibility score) untuk sesi voice/video chat singkat (5–10 menit) menggunakan fitur Group Video Call Telegram, tanpa perlu melihat foto profil sebelumnya (blind format).

**Mengapa kuat:**
- Telegram punya fitur voice/video chat grup native yang jarang dimanfaatkan aplikasi dating pihak ketiga
- Menghilangkan bias "swipe berdasarkan foto semata", relevan dengan tren anti-lookism di Gen Z/Milenial
- Elemen "roulette" secara psikologis memicu rasa penasaran dan excitement (variable reward), meningkatkan retensi mingguan
- Bisa menjadi konten viral organik ("blind date challenge") yang mendorong akuisisi pengguna baru dari word-of-mouth

### 9.2 "Squad Quest" — Misi Kolaboratif via Telegram Group
**Konsep:** Pengguna bisa membentuk atau bergabung ke grup kecil (3–5 orang teman/single) untuk menyelesaikan quest sosial bersama (misal: saling membantu memberi masukan bio, saling menyemangati streak, atau "double date quest" antar dua pasangan match).

**Mengapa kuat:**
- Memanfaatkan struktur Group Telegram yang sudah familiar bagi pengguna
- Dating terasa kurang menakutkan bila dilakukan bersama teman ("wingman digital"), sangat relevan untuk persona seperti Sarah yang cemas sosial
- Menambah lapisan retensi sosial: pengguna kembali bukan hanya untuk mencari jodoh, tapi juga untuk komunitas pertemanannya
- Membuka potensi monetisasi baru: "Squad Pass" berbayar untuk fitur grup lanjutan

### 9.3 "Compatibility Card" via Inline Mode — Shareable ke Chat Lain
**Konsep:** Menggunakan Inline Mode Telegram (`@zuzumatchbot`), pengguna bisa memanggil bot langsung di chat manapun untuk membagikan "kartu profil ringkas" bergaya game (level, badge, compatibility teaser) ke teman atau grup lain, mengundang orang untuk mencoba bot.

**Mengapa kuat:**
- Inline Mode adalah fitur khas Telegram yang jarang dieksploitasi aplikasi dating — memberi keunggulan distribusi viral tanpa perlu link eksternal
- Kartu bergaya "trading card" (mirip game collectible) memicu rasa bangga menunjukkan level/badge, mendorong sharing organik (social proof loop)
- Berfungsi sebagai growth loop K-factor: setiap share berpotensi mengonversi 1 pengguna baru
- Memperkuat identitas gamification produk — pengguna "menunjukkan" progres game mereka, bukan sekadar profil dating

### 9.4 "Mystery Gift Economy" via Telegram Stars — Micro-Gifting Antar Match
**Konsep:** Pengguna bisa mengirim "virtual gift" bertema (bunga digital, kopi digital, dsb) ke match mereka menggunakan Telegram Stars, dengan efek animasi ringan di chat. Penerima gift mendapat EXP bonus, dan pengirim mendapat badge "Generous Spark" bila konsisten.

**Mengapa kuat:**
- Memanfaatkan Telegram Stars sebagai infrastruktur pembayaran mikro native, mengurangi friksi monetisasi dibanding payment gateway eksternal
- Micro-gifting terbukti secara psikologis meningkatkan rasa keterikatan (reciprocity principle) dan menjadi ice-breaker non-verbal yang mengurangi awkwardness memulai chat
- Menjadi revenue stream tambahan yang terasa menyenangkan, bukan predatory, karena nilainya kecil dan simbolik
- Cocok dengan psikografi Gen Z yang terbiasa dengan gifting di platform live-streaming/game

### 9.5 "Public Leaderboard Channel" — Broadcast Channel Komunitas Regional
**Konsep:** Channel Telegram publik (terpisah dari bot) yang menampilkan leaderboard mingguan regional secara anonim/tersamarkan (misal hanya username & level, tanpa foto), highlight "Success Story" (pasangan yang setuju dipublikasikan), dan quest tematik komunitas.

**Mengapa kuat:**
- Memanfaatkan format Channel Telegram sebagai kanal konten pasif yang meningkatkan top-of-mind awareness tanpa harus membuka bot
- Leaderboard publik (dengan opsi privasi ketat) menciptakan tekanan sosial positif dan rasa kompetisi komunitas, memperkuat elemen gamification di luar sesi chat 1-on-1
- Success story yang dipublikasikan menjadi social proof organik yang sangat efektif untuk kredibilitas produk dating (bukti bahwa bot benar-benar menghasilkan koneksi nyata)
- Channel bisa menjadi kanal akuisisi mandiri (orang join channel dulu sebelum memutuskan mencoba bot), memperluas funnel di luar direct bot discovery

---

## Ringkasan Prioritas Implementasi

| Fase | Fokus |
|---|---|
| **MVP (Fase 1)** | Onboarding, Profiling, Match-making berbasis Quest, Level & EXP dasar, Chat System, Daily Streak sederhana |
| **Fase 2** | Virtual Currency (Spark), Leaderboard regional, Monetisasi Telegram Stars & Premium Pass |
| **Fase 3 (Beyond MVP)** | Blind Date Roulette, Squad Quest, Compatibility Card (Inline Mode), Mystery Gift Economy, Public Leaderboard Channel |

---

*Dokumen ini adalah working draft dan disarankan untuk divalidasi lebih lanjut melalui riset kualitatif (user interview) dan uji coba konsep (concept testing) sebelum masuk ke tahap desain teknis dan development.*