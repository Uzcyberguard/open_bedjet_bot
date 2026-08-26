import asyncio
import re
from datetime import datetime
from database import save_phone, get_saved_phone, phone_exists
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import BOT_TOKEN, OPEN_BUDGET_LINK, ADMIN_GROUP_ID


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()





# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    user_id = message.from_user.id

    await message.answer(
        "🏘 Assalomu alaykum!\n\n"
        "Ovoz berish uchun avval telefon raqamingizni kiriting.\n\n"
        "📱 Format:\n"
        "+998XXXXXXXXX"
    )


# =========================
# TELEFON RAQAM
# =========================

@dp.message(F.text)
async def get_phone(message: Message):

    phone = message.text.strip()
    user_id = message.from_user.id

    # +998 + 9 ta raqam
    if not re.fullmatch(r"\+998\d{9}", phone):

        await message.answer(
            "❌ Telefon raqami noto‘g‘ri.\n\n"
            "To‘g‘ri format:\n"
            "+998901234567"
        )

        return

    # Telefon raqamni vaqtincha saqlaymiz
    saved = save_phone(user_id, phone)

    if phone_exists(phone):
        await message.answer(
            "⚠️ Bu telefon raqami allaqachon ro‘yxatdan o‘tgan."
        )
        return

    save_phone(user_id, phone)

    # Ovoz berish tugmasi
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗳 Ovoz berish",
                    url=OPEN_BUDGET_LINK
                )
            ]
        ]
    )

    await message.answer(
        "✅ Telefon raqamingiz qabul qilindi!\n\n"
        "Endi quyidagi tugmani bosib, "
        "rasmiy Open Budget saytida ovoz bering.\n\n"
        "Ovoz berganingizdan keyin shu botga "
        "📸 screenshot yuboring.",
        reply_markup=keyboard
    )


# =========================
# SCREENSHOT
# =========================

@dp.message(F.photo)
async def get_screenshot(message: Message):

    user_id = message.from_user.id

    # Telefon raqami kiritilganmi?
    phone = get_saved_phone(user_id)

    if phone is None:
        await message.answer(
            "❌ Avval telefon raqamingizni yuboring."
        )
        return

    # Eng katta sifatdagi rasm
    photo = message.photo[-1]

    username = message.from_user.username

    if username:
        username_text = f"@{username}"
    else:
        username_text = "Username yo‘q"

    # Admin tugmalari
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve:{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"reject:{user_id}"
                )
            ]
        ]
    )
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    caption = (
        "🆕 Yangi ovoz tekshiruvi\n\n"
        f"👤 User: {username_text}\n\n"
        f"🆔 ID: {user_id}\n\n"
        f"📱 Telefon: {phone}\n\n"
        f"🕐 Vaqt: {now}\n\n"
        "📸 Screenshot quyida.\n\n"
        "Admin tekshirishi kerak."
    )

    # Screenshotni admin guruhiga yuborish
    await bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=photo.file_id,
        caption=caption,
        reply_markup=keyboard
    )

    await message.answer(
        "📸 Screenshotingiz qabul qilindi.\n\n"
        "⏳ Admin tekshiruvini kuting."
    )


# =========================
# ADMIN TASDIQLASH
# =========================

@dp.callback_query(F.data.startswith("approve:"))
async def approve_vote(callback):

    user_id = int(callback.data.split(":")[1])

    # Faqat admin guruhidagi odam tasdiqlay oladi
    if callback.message.chat.id != ADMIN_GROUP_ID:
        await callback.answer(
            "❌ Bu amal faqat adminlar guruhida ishlaydi.",
            show_alert=True
        )
        return

    await bot.send_message(
        user_id,
        "✅ Ovozingiz qabul qilindi!\n\n"
        "Rahmat! 🏘"
    )

    await callback.message.edit_caption(
        caption=callback.message.caption
        + "\n\n✅ TASDIQLANDI"
    )

    await callback.answer("Tasdiqlandi ✅")


# =========================
# ADMIN RAD ETISH
# =========================

@dp.callback_query(F.data.startswith("reject:"))
async def reject_vote(callback):

    user_id = int(callback.data.split(":")[1])

    # Faqat admin guruhida
    if callback.message.chat.id != ADMIN_GROUP_ID:
        await callback.answer(
            "❌ Bu amal faqat adminlar guruhida ishlaydi.",
            show_alert=True
        )
        return

    await bot.send_message(
        user_id,
        "❌ Afsuski, yuborgan screenshotingiz "
        "tasdiqlanmadi.\n\n"
        "Iltimos, ovoz berishni tekshirib, "
        "to‘g‘ri screenshot yuboring."
    )

    await callback.message.edit_caption(
        caption=callback.message.caption
        + "\n\n❌ RAD ETILDI"
    )

    await callback.answer("Rad etildi ❌")


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

async def main():

    print("Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())