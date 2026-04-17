from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
import asyncio

# ================= НАСТРОЙКИ =================
TOKEN = "8711922225:AAFbzLmblNrsl3uR8vrOJyZ6_32AlvGdbS0"   # Твой токен

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню
@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 1 День", callback_data="tarif_1")],
        [InlineKeyboardButton(text="💎 7 Дней", callback_data="tarif_7")],
        [InlineKeyboardButton(text="💎 30 Дней", callback_data="tarif_30")]
    ])
    await message.answer("🔥 Выбери длительность доступа:", reply_markup=kb)

# Обработка выбора тарифа
@dp.callback_query(F.data.startswith("tarif_"))
async def choose_tarif(callback):
    data = callback.data
    
    if data == "tarif_1":
        await send_invoice(callback.message, "1 день", 40, "Обычный", 35, "Выходные")
    elif data == "tarif_7":
        await send_invoice(callback.message, "7 дней", 175, "Обычный", 125, "Выходные")
    elif data == "tarif_30":
        await send_invoice(callback.message, "30 дней", 350, "Обычный", 300, "Выходные")

# Функция отправки инвойса
async def send_invoice(message, days, price_normal, label_normal, price_weekend, label_weekend):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💎 {label_normal} — {price_normal} ⭐️", callback_data=f"pay_{days.replace(' ', '')}_normal")],
        [InlineKeyboardButton(text=f"🔥 {label_weekend} — {price_weekend} ⭐️", callback_data=f"pay_{days.replace(' ', '')}_weekend")]
    ])
    await message.edit_text(f"Выбери цену за {days}:", reply_markup=kb)

# Обработка оплаты
@dp.callback_query(F.data.startswith("pay_"))
async def process_payment(callback):
    data = callback.data.split("_")
    days = data[1]
    type_pay = data[2]
    
    if type_pay == "normal":
        price = 40 if days == "1" else 175 if days == "7" else 350
    else:
        price = 35 if days == "1" else 125 if days == "7" else 300

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Доступ на {days} дней",
        description=f"Активация доступа на {days} дней",
        payload=f"access_{days}_{type_pay}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Доступ", amount=price)]
    )

# Обязательная обработка
@dp.pre_checkout_query()
async def pre_checkout(pre: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre.id, ok=True)

# Успешная оплата
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    amount = message.successful_payment.total_amount
    
    await message.answer(f"""
✅ <b>Оплата прошла успешно!</b>

Ты купил доступ на <b>{payload.split('_')[1]} дней</b>
⭐️ Списано: {amount} Stars

Доступ активирован. Приятного использования!
    """, parse_mode="HTML")

# Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
