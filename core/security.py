import hashlib
import hmac
import time
from urllib.parse import parse_qsl


def verify_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> bool:
    """
    Verifies Telegram Web App initData string authenticity.
    Returns True if data is authentic and signed by bot_token.
    Always enforces signature + timestamp validation (no DEBUG bypass).
    """
    if not init_data or not bot_token:
        return False

    try:
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed_data.pop("hash", None)
        if not received_hash:
            return False

        # Timestamp validation — reject stale/expired init_data
        auth_date = parsed_data.get("auth_date")
        if auth_date:
            try:
                age = abs(time.time() - int(auth_date))
                if age > max_age_seconds:
                    return False
            except (ValueError, TypeError):
                return False

        # Sort keys alphabetically
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(parsed_data.items())
        )

        # WebApp secret key is HMAC of bot token with "WebAppData"
        secret_key = hmac.new(
            b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
        ).digest()

        # Compute data hash
        computed_hash = hmac.new(
            secret_key, data_check_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_hash.lower(), received_hash.lower())
    except Exception:
        return False
