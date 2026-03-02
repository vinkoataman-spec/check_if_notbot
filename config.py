import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")
# Посилання на тг-канал (за замовчуванням — твій канал)
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/truexanewsua")
# Telegram ID того, хто отримує статистику (число, дізнатися можна в @userinfobot)
_admin_id = os.getenv("ADMIN_ID", "")
ADMIN_ID = int(_admin_id) if _admin_id.isdigit() else None
