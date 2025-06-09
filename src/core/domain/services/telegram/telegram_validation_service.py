import hmac
import hashlib
import logging
from urllib.parse import unquote

def validate_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """Валидация данных Telegram WebApp"""
    try:
        data_pairs = []
        hash_value = None

        for pair in init_data.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                if key == 'hash':
                    hash_value = unquote(value)
                else:
                    data_pairs.append(f"{key}={value}")

        if not hash_value:
            return False

        data_pairs.sort()
        data_check_string = '\n'.join(data_pairs)
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return calculated_hash == hash_value
    except Exception as e:
        logging.error(f"Telegram data validation error: {e}")
        return False
