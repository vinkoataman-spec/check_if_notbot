import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN

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
    [InlineKeyboardButton(text="Так", callback_data="confirm_human")]
])


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Ти точно людина?",
        reply_markup=confirm_human_kb,
    )


@dp.callback_query(lambda c: c.data == "confirm_human")
async def process_confirm_human(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Ви підтвердили, що ви людина.")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Тут буде допомога по командах.")


async def main():
    logger.info("Бот запущено")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
