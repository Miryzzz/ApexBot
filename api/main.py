import asyncio
import json
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from http.server import BaseHTTPRequestHandler

# --- КОНФИГ ---
TELEGRAM_TOKEN = "8205546825:AAE_f2o4Flap-omNJK_6R61iHHZjEbbghsE"
APEX_API_KEY = "02bc8279638509d6997130e7fc25273f"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# --- СЛОВАРИ ---
MAP_TRANSLATION = {
    "World's Edge": "🌋 Край Света", "Storm Point": "⛈ Место Бури",
    "Broken Moon": "🌒 Расколотая Луна", "Olympus": "☁️ Олимп",
    "Kings Canyon": "🦖 Каньон Кингс", "E-District": "🌃 Квартал Электро"
}

MAP_IMAGES = {
    "World's Edge": "https://apexlegendsstatus.com/assets/maps/Worlds_Edge.png",
    "Storm Point": "https://apexlegendsstatus.com/assets/maps/Storm_Point.png",
    "Broken Moon": "https://apexlegendsstatus.com/assets/maps/Broken_Moon.png",
    "Olympus": "https://apexlegendsstatus.com/assets/maps/Olympus.png",
    "Kings Canyon": "https://apexlegendsstatus.com/assets/maps/Kings_Canyon.png",
    "E-District": "https://apexlegendsstatus.com/assets/maps/District.png"
}

# --- МЕНЮ ---
def get_main_menu():
    kb = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🗺 Карты")],
        [KeyboardButton(text="📊 Мета Легенд"), KeyboardButton(text="🏆 Рейтинг (RP)")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🚀 **Apex Syndicate на связи!**", reply_markup=get_main_menu())

@dp.message(F.text == "🗺 Карты", Command("map"))
async def show_maps(message: types.Message):
    url = f"https://api.mozambiquehe.re/maprotation?auth={APEX_API_KEY}&version=2"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                res_text = await response.text()
                data = json.loads(res_text)
                
                br = data.get('battle_royale', {}).get('current', {})
                rnk = data.get('ranked', {}).get('current', {})
                m_name = rnk.get('map', 'Unknown')
                
                caption = (f"🎮 **Паблик:** {MAP_TRANSLATION.get(br.get('map'), br.get('map'))}\n"
                           f"⏱ Смена через: `{br.get('remainingTimer')}`\n\n"
                           f"🏆 **Рейтинг:** {MAP_TRANSLATION.get(m_name, m_name)}\n"
                           f"⏱ До смены: `{rnk.get('remainingTimer')}`")
                
                img = MAP_IMAGES.get(m_name, "https://apexlegendsstatus.com/assets/maps/Worlds_Edge.png")
                try:
                    await message.answer_photo(photo=img, caption=caption, parse_mode="Markdown")
                except:
                    await message.answer(caption, parse_mode="Markdown")
        except:
            await message.answer("⚠️ Ошибка API. Подождите 10 секунд.")

@dp.message(F.text == "🏆 Рейтинг (RP)", Command("predator"))
async def show_pred(message: types.Message):
    url = f"https://api.mozambiquehe.re/predator?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                data = await response.json()
                pc = data.get('RP', {}).get('PC', {})
                caption = (f"🎖 **Лимиты Predator (PC):**\n\n🔴 Порог: `{pc.get('val', 'N/A')}` RP\n"
                           f"🟣 Мастеров/Хищников: `{pc.get('totalMastersAndPreds', 'N/A')}`")
                
                img = "https://apexlegendsstatus.com/assets/ranks/apex_predator.png"
                try:
                    await message.answer_photo(photo=img, caption=caption, parse_mode="Markdown")
                except:
                    await message.answer(caption, parse_mode="Markdown")
        except:
            await message.answer("⚠️ Не удалось загрузить рейтинг.")

@dp.message(F.text == "📊 Мета Легенд", Command("meta"))
async def show_meta(message: types.Message):
    text = "📊 **Мета:**\n🔥 S: Newcastle, Lifeline\n⚡️ A: Pathfinder, Horizon"
    img = "https://images.wallpapersden.com/image/download/apex-legends-all-characters_bWptZ2mUmZqaraWkpJRmbmdlrWZlbWU.jpg"
    try:
        await message.answer_photo(photo=img, caption=text, parse_mode="Markdown")
    except:
        await message.answer(text)

@dp.message(F.text == "📊 Статистика")
async def stats_info(message: types.Message):
    await message.answer("🔎 Введи: `/stat Ник` (например: `/stat ImperialHal`)")

@dp.message(Command("stat", "stats"))
async def get_stat(message: types.Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("❌ Формат: `/stat Ник`")
    
    nickname = args[1]
    url = f"https://api.mozambiquehe.re/bridge?auth={APEX_API_KEY}&player={nickname}&platform=PC"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                data = await response.json()
                if "Error" in data: return await message.answer("❌ Игрок не найден.")
                
                glob = data.get('global', {})
                rank = glob.get('rank', {})
                caption = (f"👤 **Профиль:** {glob.get('name')}\n🆙 **Уровень:** {glob.get('level')}\n"
                           f"🏆 **Ранг:** {rank.get('rankName')} {rank.get('rankDiv')}\n💎 **RP:** {rank.get('rankScore')}")
                try:
                    await message.answer_photo(photo=rank.get('rankImg'), caption=caption, parse_mode="Markdown")
                except:
                    await message.answer(caption, parse_mode="Markdown")
        except:
            await message.answer("⚠️ Ошибка поиска.")

# --- VERCEL ---
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        async def process():
            update = Update.model_validate(json.loads(post_data.decode('utf-8')), context={"bot": bot})
            await dp.feed_update(bot, update)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process())
        loop.close()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Online')