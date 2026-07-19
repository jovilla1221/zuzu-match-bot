import json
import urllib.request
from typing import List, Optional
from loguru import logger
from core.config import settings

FALLBACK_ICE_BREAKERS = [
    "Kalian sama-sama suka {interest}! Ceritain hal paling berkesan buat kamu tentang itu!",
    "Suka {interest}? Kalau besok diajak hangout bareng buat nikmatin ini, mau ke mana?",
    "Pilihan unik: {interest}! Dari skala 1-10 seberapa antusias kamu?",
]


class GeminiAIService:
    """Wrapper service for Google Gemini 2.5 Flash AI model."""

    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

    def _call_gemini_api(self, prompt):
        """Performs raw REST API POST request to Google Gemini API endpoint."""
        if not self.api_key or "Placeholder" in self.api_key:
            return None

        # Prioritize models confirmed working; deduplicate while preserving order
        models_to_try = [
            self.model_name,
            "gemini-3.1-flash-lite",
            "gemini-3.1-flash-lite-preview",
            "gemini-flash-lite-latest",
        ]
        models_to_try = list(dict.fromkeys(models_to_try))

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300,
            }
        }
        data_json = json.dumps(payload).encode("utf-8")

        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            req = urllib.request.Request(
                url, data=data_json, headers={"Content-Type": "application/json"}
            )

            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e:
                logger.warning(f"Gemini API call to model {m} failed ({e}). Trying next model if available...")

        return None

    def generate_ai_ice_breakers(
        self, user1_name, user2_name, common_interests
    ):
        """Generates 3 witty Indonesian dating ice-breakers via Gemini 2.5 Flash."""
        interest_str = ", ".join(common_interests) if common_interests else "hal-hal seru"
        prompt = (
            f"Kamu adalah AI matchmaker gaul dan ramah di bot dating Telegram. "
            f"{user1_name} dan {user2_name} baru saja mutual match! Minat bersama mereka adalah: {interest_str}.\n"
            f"Buatkan tepat 3 baris pertanyaan pembuka percakapan (ice-breaker) yang unik, lucu, ramah, dan santai dalam Bahasa Indonesia casual.\n"
            f"Format output: Berikan 3 baris teks tanpa nomor atau bullet point tambahan."
        )

        ai_response = self._call_gemini_api(prompt)
        if ai_response:
            lines = [line.strip("-123. ") for line in ai_response.split("\n") if line.strip()]
            if len(lines) >= 3:
                return lines[:3]

        topic = common_interests[0] if common_interests else "hal-hal baru"
        return [tmpl.format(interest=topic) for tmpl in FALLBACK_ICE_BREAKERS]

    def generate_ai_bio(
        self,
        interests,
        current_bio="",
        user_prompt="",
    ):
        """Generates a playful, catchy dating profile bio via Gemini 2.5 Flash.

        Args:
            interests: User interest tags
            current_bio: Current bio (optional)
            user_prompt: Optional user guidance on style/tone they want
        """
        prompt_parts = [
            "Tuliskan 1 paragraf bio profil dating Telegram yang menarik, santai, dan lucu (maksimal 150 karakter) "
            "dalam Bahasa Indonesia casual.\n"
        ]

        if user_prompt:
            prompt_parts.append(f"Tulis HANYA berdasarkan topik/gaya ini: {user_prompt}\n")
        else:
            tag_str = ", ".join(interests) if interests else "ngopi, musik, traveling"
            prompt_parts.append(f"Fokus pada minat berikut: {tag_str}.\n")

        if current_bio:
            prompt_parts.append(f"Bio saat ini (sebagai referensi tambahan): {current_bio}\n")

        prompt_parts.append(
            "Sertakan emoji yang pas! Jangan berikan teks pembuka, langsung tuliskan bionya."
        )

        prompt = "".join(prompt_parts)

        ai_response = self._call_gemini_api(prompt)
        if ai_response:
            return ai_response.strip("\"'")

        return f"Penikmat {tag_str} Mencari teman ngobrol seru dan partner jalan santai"
