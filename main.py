import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN, CHANNEL_LINK, ADMIN_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

if not TOKEN:
    logger.error("Встанови BOT_TOKEN у .env або змінній середовища")
    raise SystemExit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Клавіатура "Ти точно людина?"
confirm_human_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Я людина", callback_data="confirm_human")]
])


def _user_info(user: types.User) -> str:
    """Текст про користувача для статистики."""
    name = user.full_name or "Без імені"
    username = f"@{user.username}" if user.username else "немає юзернейму"
    return f"{name} ({username}), ID: {user.id}"


async def _notify_admin(text: str):
    """Надіслати повідомлення відповідальному за бота."""
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        except Exception as e:
            logger.warning("Не вдалося надіслати статистику адміну: %s", e)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Ти точно людина?",
        reply_markup=confirm_human_kb,
    )
    await _notify_admin(
        "🟢 <b>Активував бота</b>\n" + _user_info(message.from_user)
    )


@dp.callback_query(lambda c: c.data == "confirm_human")
async def process_confirm_human(callback: types.CallbackQuery):
    await callback.answer()
    user = callback.from_user
    await _notify_admin(
        "✅ <b>Підтвердив, що не робот</b>\n" + _user_info(user)
    )
    text = "Ви підтвердили, що ви людина."
    if CHANNEL_LINK:
        text += f'\n\nНаш канал: <a href="{CHANNEL_LINK}">перейти в канал</a>'
    await callback.message.edit_text(text, parse_mode="HTML")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Тут буде допомога по командах.")


async def main():
    logger.info("Бот запущено")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
