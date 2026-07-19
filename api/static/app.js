// Zuzu Match Mini App Frontend Client Logic
document.addEventListener("DOMContentLoaded", () => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
        tg.ready();
        tg.expand();
    }

    const initData = tg?.initData || "";

    const ALL_INTERESTS = [
        "Gaming 🎮", "Music 🎵", "Travel ✈️", "Coffee ☕", "Anime 🌸",
        "Hiking 🏔️", "Tech 💻", "Movies 🍿", "Fitness 🏋️", "Cooking 🍳",
        "Photography 📷", "Art 🎨", "Books 📚", "Pets 🐶", "K-Pop 💃"
    ];

    let selectedInterests = new Set();

    // DOM Elements
    const displayNameEl = document.getElementById("display-name");
    const userTierEl = document.getElementById("user-tier");
    const userStreakEl = document.getElementById("user-streak");
    const userSparkEl = document.getElementById("user-spark");
    const levelInfoEl = document.getElementById("user-level-info");
    const expBarEl = document.getElementById("exp-bar");
    const bioInput = document.getElementById("bio-input");
    const interestsGrid = document.getElementById("interests-grid");
    const genderSelect = document.getElementById("gender-select");

    const saveBioBtn = document.getElementById("save-bio-btn");
    const saveInterestsBtn = document.getElementById("save-interests-btn");
    const savePrefsBtn = document.getElementById("save-prefs-btn");

    function renderInterestsGrid() {
        interestsGrid.replaceChildren();
        ALL_INTERESTS.forEach(tag => {
            const btn = document.createElement("div");
            btn.className = "tag-item" + (selectedInterests.has(tag) ? " selected" : "");
            btn.textContent = tag;
            btn.addEventListener("click", () => {
                if (selectedInterests.has(tag)) {
                    selectedInterests.delete(tag);
                } else {
                    selectedInterests.add(tag);
                }
                renderInterestsGrid();
            });
            interestsGrid.appendChild(btn);
        });
    }

    async function loadUserProfile() {
        if (!initData) {
            displayNameEl.textContent = "Demo User (Web Sandbox)";
            renderInterestsGrid();
            return;
        }

        try {
            const res = await fetch(`/webapp/profile/me?init_data=${encodeURIComponent(initData)}`);
            if (!res.ok) throw new Error("Gagal mengambil profil.");
            
            const data = await res.json();
            updateUI(data);
        } catch (err) {
            console.error("Load Profile Error:", err);
        }
    }

    function updateUI(data) {
        displayNameEl.textContent = data.username || "Adventurer";
        userTierEl.textContent = data.tier;
        userStreakEl.textContent = data.streak;
        userSparkEl.textContent = data.spark;
        levelInfoEl.textContent = `Level ${data.level} (${data.exp} total EXP)`;
        expBarEl.style.width = `${data.completeness_score}%`;
        bioInput.value = data.bio || "";

        if (data.interests && Array.isArray(data.interests)) {
            selectedInterests = new Set(data.interests);
        }
        renderInterestsGrid();
    }

    saveBioBtn.addEventListener("click", async () => {
        const bioText = bioInput.value.trim();
        if (bioText.length < 10) {
            alert("⚠️ Bio terlalu singkat (min. 10 karakter)!");
            return;
        }

        try {
            const res = await fetch("/webapp/profile/bio", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ init_data: initData, bio: bioText })
            });
            if (res.ok) {
                const updated = await res.json();
                updateUI(updated);
                alert("✨ Bio berhasil disimpan! (+30 EXP awarded)");
            }
        } catch (e) {
            alert("Gagal menyimpan bio.");
        }
    });

    saveInterestsBtn.addEventListener("click", async () => {
        const interestsArr = Array.from(selectedInterests);
        if (interestsArr.length < 3) {
            alert("⚠️ Pilih minimal 3 minat!");
            return;
        }

        try {
            const res = await fetch("/webapp/profile/interests", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ init_data: initData, interests: interestsArr })
            });
            if (res.ok) {
                const updated = await res.json();
                updateUI(updated);
                alert("🎯 Tag minat berhasil disimpan! (+30 EXP awarded)");
            }
        } catch (e) {
            alert("Gagal menyimpan minat.");
        }
    });

    savePrefsBtn.addEventListener("click", async () => {
        const selectedGender = genderSelect.value;
        const genderPref = selectedGender === "ALL" ? ["MALE", "FEMALE", "NON_BINARY"] : [selectedGender];

        try {
            const res = await fetch("/webapp/profile/preferences", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    init_data: initData,
                    age_min: 18,
                    age_max: 35,
                    radius_km: 50,
                    gender_pref: genderPref
                })
            });
            if (res.ok) {
                const updated = await res.json();
                updateUI(updated);
                alert("⚙️ Preferensi berhasil disimpan!");
            }
        } catch (e) {
            alert("Gagal menyimpan preferensi.");
        }
    });

    loadUserProfile();
});
