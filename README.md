# Новий Telegram-бот

Мінімальний каркас для бота на aiogram 3.

## Запуск

1. Створи бота в [@BotFather](https://t.me/BotFather), отримай токен.
2. Скопіюй `.env.example` в `.env` і вкажи свій токен:
   ```
   BOT_TOKEN=твій_токен
   ```
3. Встанови залежності та запусти:
   ```
   pip install -r requirements.txt
   python main.py
   ```

Далі можна додавати свої команди та обробники в `main.py`.
