import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")
# Посилання на тг-канал (за замовчуванням — твій канал)
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/test123456789absd")


def _extract_channel_username(link: str) -> str:
    """
    Дістати юзернейм каналу з посилання, наприклад:
    https://t.me/test123456789absd -> truexanewsua
    """
    if not link:
        return ""
    # Беремо все після останнього слеша і прибираємо параметри
    tail = link.rsplit("/", 1)[-1]
    tail = tail.split("?", 1)[0]
    return tail.lstrip("@")


CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "") or _extract_channel_username(CHANNEL_LINK)

# Telegram ID того, хто отримує статистику (число, дізнатися можна в @userinfobot)
_admin_id = os.getenv("ADMIN_ID", "")
ADMIN_ID = int(_admin_id) if _admin_id.isdigit() else None
