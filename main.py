import asyncio
import logging
from datetime import datetime, timedelta, date

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN, CHANNEL_LINK, ADMIN_ID, CHANNEL_USERNAME

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

# Користувачі, яких треба перевіряти на підписку
pending_subscribers: set[int] = set()

# Статистика за поточний день (унікальні користувачі)
users_started: set[int] = set()
users_confirmed: set[int] = set()
users_subscribed: set[int] = set()
# Інформація про користувачів (щоб показати список)
users_info: dict[int, str] = {}


# Клавіатура "Ти точно людина?"
confirm_human_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Я людина", callback_data="confirm_human")]
])


def _user_info(user: types.User) -> str:
    """Текст про користувача для статистики."""
    name = user.full_name or "Без імені"
    username = f"@{user.username}" if user.username else "немає юзернейму"
    return f"{name} ({username}), ID: {user.id}"


def _remember_user(user: types.User) -> None:
    """Зберегти інформацію про користувача для подальшого перегляду."""
    users_info[user.id] = _user_info(user)


async def _notify_admin(text: str):
    """Надіслати повідомлення відповідальному за бота."""
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        except Exception as e:
            logger.warning("Не вдалося надіслати статистику адміну: %s", e)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    users_started.add(user.id)
    _remember_user(user)

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
    users_confirmed.add(user.id)
    _remember_user(user)
    await _notify_admin(
        "✅ <b>Підтвердив, що не робот</b>\n" + _user_info(user)
    )
    # Якщо відомий юзернейм каналу — додаємо в список на перевірку
    if CHANNEL_USERNAME:
        pending_subscribers.add(user.id)

    text = "Ви підтвердили, що ви людина."
    if CHANNEL_LINK:
        text += f'\n\nНаш канал: <a href="{CHANNEL_LINK}">перейти в канал</a>'
    await callback.message.edit_text(text, parse_mode="HTML")


async def check_subscriptions_loop():
    """Раз на хвилину перевіряє, хто з pending_subscribers уже підписався на канал."""
    if not CHANNEL_USERNAME:
        return
    chat_id = f"@{CHANNEL_USERNAME}"
    while True:
        try:
            if pending_subscribers:
                # Копія, щоб можна було змінювати оригінальний сет
                for user_id in list(pending_subscribers):
                    try:
                        member = await bot.get_chat_member(chat_id, user_id)
                        status = str(getattr(member, "status", "")).lower()
                        if status not in ("left", "kicked"):
                            # Вважаємо, що підписався
                            users_subscribed.add(user_id)
                            await _notify_admin(
                                "📢 <b>Підписався на телеграм-канал</b>\n"
                                f"ID: {user_id}"
                            )
                            pending_subscribers.discard(user_id)
                    except Exception as e:
                        logger.debug("Помилка під час перевірки підписки для %s: %s", user_id, e)
                    # Невелика пауза між запитами, щоб не спамити API
                    await asyncio.sleep(0.2)
        except Exception as e:
            logger.warning("Помилка в циклі перевірки підписок: %s", e)

        # Пауза 60 секунд між циклами
        await asyncio.sleep(60)


async def daily_stats_loop():
    """Раз на день надсилає адміну зведену статистику та обнуляє лічильники."""
    current_day: date | None = date.today()
    while True:
        now = datetime.now()
        # рахуємо час до наступної опівночі
        tomorrow = now + timedelta(days=1)
        next_midnight = datetime.combine(tomorrow.date(), datetime.min.time())
        wait_seconds = (next_midnight - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        stats_day = current_day or date.today()
        current_day = date.today()

        starts_count = len(users_started)
        confirmed_count = len(users_confirmed)
        subscribed_count = len(users_subscribed)

        if ADMIN_ID:
            text = (
                f"📊 <b>Статистика за {stats_day.strftime('%d.%m.%Y')}</b>\n\n"
                f"• Користувачів натиснули /start: <b>{starts_count}</b>\n"
                f"• Користувачів підтвердили, що не робот: <b>{confirmed_count}</b>\n"
                f"• Користувачів (з тих, кого відстежували) підписалися на канал: <b>{subscribed_count}</b>\n"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="Подивитися користувачів",
                    callback_data="show_daily_users",
                )
            ]])
            await bot.send_message(
                ADMIN_ID,
                text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

        # Обнуляємо статистику на новий день
        users_started.clear()
        users_confirmed.clear()
        users_subscribed.clear()
        users_info.clear()


@dp.callback_query(lambda c: c.data == "show_daily_users")
async def show_daily_users(callback: types.CallbackQuery):
    """Показати адміну список користувачів за поточний день."""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Недостатньо прав.", show_alert=True)
        return

    await callback.answer()

    if not users_info:
        await callback.message.answer("За сьогодні користувачів не зафіксовано.")
        return

    lines = [f"👥 <b>Користувачі за сьогодні ({len(users_info)}):</b>"]
    for info in users_info.values():
        lines.append(f"• {info}")

    text = "\n".join(lines)
    await callback.message.answer(text, parse_mode="HTML")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Тут буде допомога по командах.")


async def main():
    logger.info("Бот запущено")
    # Запускаємо фонову перевірку підписок та щоденну статистику
    asyncio.create_task(check_subscriptions_loop())
    asyncio.create_task(daily_stats_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
