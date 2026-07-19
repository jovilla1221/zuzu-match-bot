"""User-facing message templates for Zuzu Match Bot."""

WELCOME_NEW = (
    "Halo, adventurer! 👋 Selamat datang di **Zuzu Match**! 💖\n\n"
    "Bosan sama dating app yang serba swipe-dan-ghosting? Di sini, setiap cara kamu berkenalan "
    "itu kayak main RPG! Kamu bakal dapet **EXP**, naik **Level**, ngumpulin **Spark ⚡**, "
    "dan nemuin match yang beneran pas sama vibe kamu!\n\n"
    "Yuk, kita mulai petualangan kamu! Langkah pertama: **Upload Foto Profil terbaikmu** 📸\n"
    "*(Bonus +30 EXP menantimu!)*"
)

WELCOME_BACK = (
    "Halo lagi, {name}! 🌟 Selamat datang kembali di Zuzu Match!\n\n"
    "📊 **Status Kamu:**\n"
    "• Level: {level} ({tier})\n"
    "• EXP: {exp}\n"
    "• Streak: 🔥 {streak} Hari\n"
    "• Spark: ⚡ {spark}\n\n"
    "Pilih menu di bawah untuk lanjut cari jodoh atau cek quest harianmu!"
)

ONBOARD_PHOTO_PROMPT = (
    "📸 **Step 1.5: Foto Profil**\n\n"
    "Kirimkan 1 foto profil terbaik kamu! Gunakan foto yang jelas kelihatan wajah kamu ya, biar pasangan lain makin tertarik ✨"
)

ONBOARD_GENDER_PROMPT = (
    "🚻 **Step 1: Gender Kamu**\n\n"
    "Nama panggilan yang bagus!\n"
    "Sekarang, beritahu kami apa gender kamu agar sistem bisa merekomendasikan profil yang pas!"
)

ONBOARD_BIO_PROMPT = (
    "✍️ **Step 2: Bio Singkat**\n\n"
    "Foto kece udah dipasang (+30 EXP 🎉)!\n"
    "Sekarang, tulis bio singkat tentang dirimu (min. 10 karakter). Apa hobi unikmu, atau tipe orang yang lagi kamu cari?"
)

ONBOARD_INTERESTS_PROMPT = (
    "🎯 **Step 3: Tag Minat & Hobi**\n\n"
    "Bio menarik tersimpan (+30 EXP 🎉)!\n"
    "Pilih minimal **3 minat/hobi** yang paling menggambarkan kamu dari tombol di bawah ini:"
)

ONBOARD_PREFERENCES_PROMPT = (
    "⚙️ **Step 4: Preferensi Pencarian**\n\n"
    "Tag minat tersimpan (+30 EXP 🎉)!\n"
    "Terakhir, pilih preferensi gender yang ingin kamu temui:"
)

ONBOARD_COMPLETE = (
    "🥳 **ONBOARDING SELESAI!** 🎉🎉\n\n"
    "Profil kamu sudah siap 100%! Kamu mendapatkan total bonus onboarding **+120 EXP** "
    "dan resmi naik ke **Level 1** ({tier})! 🚀\n\n"
    "Gunakan command `/quest` untuk melihat pasangan quest harian kamu hari ini!"
)

PROFILE_VIEW = (
    "👤 **Profil Zuzu Kamu**\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "📛 Nama: {username}\n"
    "🎖️ Tier: **{tier}** (Level {level})\n"
    "✨ Progress Level: [{progress_bar}] {exp_in_level}/{required} EXP\n"
    "🔥 Streak Active: {streak} Hari\n"
    "⚡ Spark Balance: {spark}\n"
    "📊 Kelengkapan Profil: {completeness}%\n\n"
    "📝 **Bio:**\n_{bio}_\n\n"
    "🏷️ **Minat:** {interests}\n"
    "🏷️ **Badges:** {badges}\n"
    "━━━━━━━━━━━━━━━━━━━"
)

LEVEL_UP = (
    "🎉 **LEVEL UP!** 🎉\n\n"
    "Selamat! Kamu baru saja naik ke **Level {level}** ({tier})! ✨\n"
    "Kamu mendapatkan bonus **+5 Spark ⚡**!"
)
