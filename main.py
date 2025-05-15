import logging
import json
from datetime import datetime, time, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import (
    WebAppInfo, 
    Message, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    ChatMemberUpdated
)
from aiogram.client.default import DefaultBotProperties

# Настройки
API_TOKEN = '7676713420:AAH1gzBOLvIYFsn6qxhGaj0ce_rr9ApykLI'
GROUP_ID = -1002414553290
MOSCOW_TZ_OFFSET = timedelta(hours=3)  # UTC+3 для Москвы

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def is_working_hours():
    """Проверяет, рабочее ли сейчас время в Москве (с 10:00 до 22:00)"""
    now_utc = datetime.utcnow()
    now_moscow = now_utc + MOSCOW_TZ_OFFSET
    return time(10, 0) <= now_moscow.time() <= time(22, 0)

async def send_welcome_message(chat_id: int):
    """Функция для отправки приветственного сообщения"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="Оформить заявку", 
                web_app=WebAppInfo(url="https://alekseys90.github.io/nevelskogo/")
            )]
        ],
        resize_keyboard=True
    )
    await bot.send_message(
        chat_id,
        "Рады видеть Вас в телеграмм боте винотеки DRINX Невельского! Нажмите кнопку ниже, чтобы оставить заявку.",
        reply_markup=markup
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    if is_working_hours():
        await send_welcome_message(message.chat.id)
    else:
        await message.answer(
            "Приносим свои извинения, в данный момент мы не работаем (часы работы с 10:00 до 22:00).\n\n"
            "Мы будем рады видеть Вас в винотеке DRINX Невельского с 10:00 до 22:00!\n"
            "Вы можете отправить заявку в рабочее время, нажав /start"
        )

@dp.message(lambda m: m.web_app_data is not None)
async def handle_web_app_data(message: Message):
    """Обработчик данных из WebApp"""
    if not is_working_hours():
        await message.answer(
            "⏳ <b>Винотека сейчас закрыта</b>\n\n"
            "Мы получили вашу заявку, но обработаем её только в рабочее время с 10:00.\n"
            "Спасибо за понимание!"
        )
        return

    try:
        data = json.loads(message.web_app_data.data)
        logger.info(f"Получены данные: {data}")

        text = (
            "📥 <b>Новая заявка:</b>\n\n"
            f"👤 Имя: {data.get('name', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указано')}\n"
            f"🛎 Услуга: {data.get('service_type', 'Не указано')}"
        )

        await bot.send_message(GROUP_ID, text)
        await message.answer("✅ Ваша заявка успешно отправлена! Мы свяжемся с Вами в ближайшее время. Если у Вас срочный вопрос, пожалуйста, свяжитесь с нами по телефону +7 991 742 20 05 📞")

    except Exception as e:
        logger.exception("Ошибка при обработке данных")
        await message.answer("❌ Произошла ошибка при отправке заявки. Приносим свои извинения, на данный момент мы не можем принять заявку. Пожалуйста, свяжитесь с нами по телефону +7 991 742 20 05 📞")

@dp.message(F.text & ~F.text.startswith('/start'))
async def handle_other_messages(message: Message):
    """Обработчик других текстовых сообщений"""
    if not is_working_hours():
        await message.answer(
            "⏳ <b>Винотека сейчас закрыта</b>\n\n"
            "Часы работы: с 10:00 до 22:00\n\n"
            "Вы можете оставить заявку, нажав /start в рабочее время"
        )
    else:
        await message.delete()
        await message.answer(
            "Пожалуйста, используйте кнопку меню для взаимодействия с ботом.\n"
            "Нажмите /start для открытия меню.",
            reply_markup=types.ReplyKeyboardRemove()
        )

@dp.message()
async def handle_other_content(message: Message):
    """Обработчик других типов контента"""
    if not is_working_hours():
        await message.answer(
            "⏳ <b>Винотека сейчас закрыта</b>\n\n"
            "Мы работаем ежедневно с 10:00 до 22:00\n"
            "Будем рады видеть Вас в рабочее время с 10:00 до 22:00!"
        )
    else:
        await message.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())