import asyncio
import aiohttp
import logging
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Bot tokenini kiriting
BOT_TOKEN = "7609705273:AAFoIawJBTGTFxECwhSjc7vpbgMBcveT_ko"

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# JSON fayl nomi
USER_DATA_FILE = "user_data.json"

# JSON fayldan ma'lumotlarni yuklash
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# JSON faylga ma'lumotlarni saqlash
def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# User ma'lumotlarini yuklash
user_data_storage = load_user_data()

# Matnlar
TEXTS = {
    "uz": {
        "choose_language": "Tilni tanlang / Выберите язык:",
        "greeting": "Assalomu alaykum! Ro'yxatdan o'tish uchun telefon raqamingizni yuboring.",
        "phone_button": "📱 Telefon raqamini yuborish",
        "phone_received": "Telefon raqamingiz qabul qilindi. Ro'yxatdan o'tkazish...",
        "registration_success": "✅ Muvaffaqiyatli ro'yxatdan o'tdingiz!\n\nQuyidagi tugma orqali Web App'ni ochishingiz mumkin:",
        "already_registered": "✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n📱 Telefon: +{phone}\n\n🌐 Web App'ni ochish:",
        "error_occurred": "❌ Xatolik yuz berdi (Status: {status})\n\n🔧 Backend xabari: {response_text}\n\nIltimos, keyinroq qayta urinib ko'ring.",
        "network_error": "❌ Network xatoligi:\n{error}\n\nServer bilan bog'lanishda muammo bor.",
        "unexpected_error": "❌ Kutilmagan xatolik:\n{error}\n\nIltimos, keyinroq qayta urinib ko'ring.",
        "please_send_phone": "Iltimos, telefon raqamingizni yuboring.",
        "web_app_button": "🌐 Web App ochish",
        "start_command": "Ro'yxatdan o'tish uchun /start buyrug'ini yuboring.",
        "uzbek": "🇺🇿 O'zbek",
        "russian": "🇷🇺 Русский"
    },
    "ru": {
        "choose_language": "Tilni tanlang / Выберите язык:",
        "greeting": "Добро пожаловать! Для регистрации отправьте свой номер телефона.",
        "phone_button": "📱 Отправить номер телефона",
        "phone_received": "Номер телефона получен. Регистрируем...",
        "registration_success": "✅ Успешно зарегистрированы!\n\nВы можете открыть Web App с помощью кнопки ниже:",
        "already_registered": "✅ Вы уже зарегистрированы!\n\n📱 Телефон: +{phone}\n\n🌐 Открыть Web App:",
        "error_occurred": "❌ Произошла ошибка (Status: {status})\n\n🔧 Сообщение от сервера: {response_text}\n\nПожалуйста, попробуйте позже.",
        "network_error": "❌ Сетевая ошибка:\n{error}\n\nПроблема с подключением к серверу.",
        "unexpected_error": "❌ Неожиданная ошибка:\n{error}\n\nПожалуйста, попробуйте позже.",
        "please_send_phone": "Пожалуйста, отправьте свой номер телефона.",
        "web_app_button": "🌐 Открыть Web App",
        "start_command": "Для регистрации отправьте команду /start.",
        "uzbek": "🇺🇿 O'zbek",
        "russian": "🇷🇺 Русский"
    }
}

# States
class RegistrationStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_phone = State()

# Til tanlash keyboard
language_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Telefon raqami uchun keyboard (dinamik)
def get_phone_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]["phone_button"], request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# /start komandasi
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    # Start parametrini olish (table_id)
    command_text = message.text
    table_id = None
    
    if len(command_text.split()) > 1:
        table_id = command_text.split()[1]
        await state.update_data(table_id=table_id)
    
    user_id = str(message.from_user.id)
    
    # User ma'lumotlarini tekshirish
    if user_id in user_data_storage:
        # Foydalanuvchi avval ro'yxat o'tgan
        user_info = user_data_storage[user_id]
        lang = user_info.get("language", "uz")
        
        # Web App URL yaratish
        web_app_url = f"https://www.amur1.uz/?phone={user_info['phone_number']}&password={user_id}"
        
        # Agar table_id mavjud bo'lsa, qo'shish
        if table_id:
            web_app_url = f"https://www.amur1.uz/?table_id={table_id}&phone={user_info['phone_number']}&password={user_id}"
        
        # Web App tugmasi
        web_app_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=TEXTS[lang]["web_app_button"],
                    web_app=WebAppInfo(url=web_app_url)
                )]
            ]
        )
        
        await message.answer(
            TEXTS[lang]["already_registered"].format(phone=user_info['phone_number']),
            reply_markup=web_app_keyboard
        )
    else:
        # Yangi foydalanuvchi - til tanlash
        await message.answer(
            TEXTS["uz"]["choose_language"],
            reply_markup=language_keyboard
        )
        await state.set_state(RegistrationStates.waiting_for_language)

# Til tanlash
@dp.message(RegistrationStates.waiting_for_language)
async def language_handler(message: types.Message, state: FSMContext):
    if message.text == "🇺🇿 O'zbek":
        selected_lang = "uz"
    elif message.text == "🇷🇺 Русский":
        selected_lang = "ru"
    else:
        await message.answer(
            TEXTS["uz"]["choose_language"],
            reply_markup=language_keyboard
        )
        return
    
    # Tanlangan tilni saqlash
    await state.update_data(language=selected_lang)
    
    await message.answer(
        TEXTS[selected_lang]["greeting"],
        reply_markup=get_phone_keyboard(selected_lang)
    )
    await state.set_state(RegistrationStates.waiting_for_phone)

# Telefon raqami yuborilganda
@dp.message(RegistrationStates.waiting_for_phone)
async def phone_handler(message: types.Message, state: FSMContext):
    # Tanlangan tilni olish
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    if message.contact:
        # Telefon raqami olindi
        phone_number = message.contact.phone_number
        user_id = message.from_user.id
        full_name = message.from_user.full_name or "User"
        
        # Telefon raqamini tozalash (+ belgisini olib tashlash)
        if phone_number.startswith("+"):
            clean_phone = phone_number[1:]  # + belgisini olib tashlash
        else:
            clean_phone = phone_number
        
        # API ga yuborish uchun ma'lumotlar
        registration_data = {
            "full_name": full_name,
            "number": clean_phone,
            "password": str(user_id),
            "tg_id": user_id,
            "language": "ru"
        }
        
        await message.answer(
            TEXTS[lang]["phone_received"],
            reply_markup=ReplyKeyboardRemove()
        )
        
        # API ga so'rov yuborish
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://uzjoylar-yoqj.onrender.com/api/register",
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    # Response textini olish
                    response_text = await response.text()
                    
                    # Logging uchun ma'lumotlar
                    logging.info(f"API Response Status: {response.status}")
                    logging.info(f"API Response Text: {response_text}")
                    logging.info(f"Sent data: {registration_data}")
                    
                    # Foydalanuvchi ma'lumotlarini saqlash
                    user_info = {
                        "user_id": user_id,
                        "full_name": full_name,
                        "phone_number": clean_phone,
                        "username": message.from_user.username,
                        "language": lang,
                        "registration_time": datetime.now().isoformat(),
                        "api_response_status": response.status,
                        "api_response_text": response_text
                    }
                    
                    # User ma'lumotlarini JSON faylga saqlash
                    user_data_storage[str(user_id)] = user_info
                    save_user_data(user_data_storage)
                    
                    logging.info(f"User data saved for user_id {user_id}: {user_info}")
                    
                    # Agar table_id mavjud bo'lsa, alohida saqlash
                    if user_data.get("table_id"):
                        table_id = user_data["table_id"]
                        logging.info(f"Table ID {table_id} linked to user {user_id}")
                    
                    if response.status == 200:
                        # Muvaffaqiyatli ro'yxat - Web App tugmasi yaratish
                        web_app_url = f"https://www.amur1.uz/?phone={clean_phone}&password={user_id}"
                        
                        # Agar table_id mavjud bo'lsa, qo'shish
                        if user_data.get("table_id"):
                            web_app_url = f"https://www.amur1.uz/?table_id={user_data['table_id']}&phone={clean_phone}&password={user_id}"
                        
                        # Web App tugmasi bilan inline keyboard
                        web_app_keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(
                                    text=TEXTS[lang]["web_app_button"],
                                    web_app=WebAppInfo(url=web_app_url)
                                )]
                            ]
                        )
                        
                        await message.answer(
                            TEXTS[lang]["registration_success"],
                            reply_markup=web_app_keyboard
                        )
                    elif response.status == 400:
                        # Oldin ro'yxat o'tgan yoki boshqa 400 xatolik
                        # Web App tugmasi bilan javob berish
                        web_app_url = f"https://www.amur1.uz/?phone={clean_phone}&password={user_id}"
                        
                        # Agar table_id mavjud bo'lsa, qo'shish
                        if user_data.get("table_id"):
                            web_app_url = f"https://www.amur1.uz/?table_id={user_data['table_id']}&phone={clean_phone}&password={user_id}"
                        
                        web_app_keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(
                                    text=TEXTS[lang]["web_app_button"],
                                    web_app=WebAppInfo(url=web_app_url)
                                )]
                            ]
                        )
                        
                        await message.answer(
                            TEXTS[lang]["already_registered"].format(phone=clean_phone),
                            reply_markup=web_app_keyboard
                        )
                    else:
                        # Boshqa xatolik
                        await message.answer(
                            TEXTS[lang]["error_occurred"].format(
                                status=response.status,
                                response_text=response_text
                            )
                        )
                        
        except aiohttp.ClientError as e:
            # Network xatoliklari
            logging.error(f"Network error: {e}")
            await message.answer(
                TEXTS[lang]["network_error"].format(error=str(e))
            )
        except Exception as e:
            # Boshqa xatoliklar
            logging.error(f"Unexpected error: {e}")
            await message.answer(
                TEXTS[lang]["unexpected_error"].format(error=str(e))
            )
    else:
        # Telefon raqami yuborilmagan
        await message.answer(
            TEXTS[lang]["please_send_phone"],
            reply_markup=get_phone_keyboard(lang)
        )
    
    await state.clear()

# Boshqa barcha xabarlar
@dp.message()
async def other_messages(message: types.Message):
    await message.answer(
        TEXTS["uz"]["start_command"]
    )

# Saqlab olingan ma'lumotlarni ko'rish uchun admin komandasi
@dp.message(Command("admin"))
async def admin_handler(message: types.Message):
    if message.from_user.id != 1066137436:  # Admin ID sini o'zgartiring
        await message.answer("❌ Sizda bu komandani ishlatish huquqi yo'q!")
        return
    
    if not user_data_storage:
        await message.answer("📊 Hozircha hech qanday ma'lumot saqlanmagan.")
        return
    
    admin_text = "📊 Saqlangan foydalanuvchi ma'lumotlari:\n\n"
    
    for user_id, user_info in user_data_storage.items():
        admin_text += f"🔸 User ID: {user_id}\n"
        admin_text += f"   👤 Ism: {user_info['full_name']}\n"
        admin_text += f"   📞 Telefon: +{user_info['phone_number']}\n"
        admin_text += f"   👥 Username: @{user_info['username'] or 'None'}\n"
        admin_text += f"   🌐 Til: {user_info['language']}\n"
        admin_text += f"   📅 Vaqt: {user_info['registration_time']}\n"
        admin_text += f"   ✅ Status: {user_info['api_response_status']}\n\n"
    
    await message.answer(admin_text)

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())