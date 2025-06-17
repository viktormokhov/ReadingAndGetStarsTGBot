import hmac
import hashlib
import logging
from urllib.parse import unquote

def validate_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    try:
        data_pairs = []
        hash_value = None

        for pair in init_data.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                value = unquote(value)
                if key == 'hash':
                    hash_value = value
                else:
                    data_pairs.append(f"{key}={value}")

        if not hash_value:
            return False

        # Сортировка по ключам (на случай дубликатов)
        data_pairs.sort(key=lambda x: x.split('=')[0])

        data_check_string = '\n'.join(data_pairs)

        secret_key = hmac.new(
            b'WebAppData',
            bot_token.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return calculated_hash == hash_value
    except Exception as e:
        logging.error(f"Validation error: {e}")
        return False
