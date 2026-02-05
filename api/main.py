import asyncio
import os
import json
import aiohttp
import ssl
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from http.server import BaseHTTPRequestHandler

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8205546825:AAE_f2o4Flap-omNJK_6R61iHHZjEbbghsE"
APEX_API_KEY = "02bc8279638509d6997130e7fc25273f"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


MAP_TRANSLATION = {
    "World's Edge": "Край Света",
    "Storm Point": "Место Бури",
    "Broken Moon": "Разрушенная Луна",
    "Olympus": "Олимп",
    "Kings Canyon": "Каньон Кингс",
    "District": "Район",
    "E-District": "Квартал Э", 
    
    "Wraith": "Рэйф",
    "Octane": "Октейн",
    "Pathfinder": "Патфайндер",
    "Conduit": "Кондуит", 
    "Horizon": "Хорайзон",
    "Bloodhound": "Бладхаунд"
}

# --- КОМАНДЫ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я твой личный помощник.\nДоступные команды: /map, /predator, /news, /legends, /store")

@dp.message(Command("map"))
async def cmd_map(message: types.Message):
    url = f"https://api.mozambiquehe.re/maprotation?auth={APEX_API_KEY}&version=2"
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    res = await response.json()
                    pubs_en = res['battle_royale']['current']['map']
                    rank_en = res['ranked']['current']['map']
                    time_rank = res['ranked']['current']['remainingTimer']
                    
                    pubs_ru = MAP_TRANSLATION.get(pubs_en, pubs_en)
                    rank_ru = MAP_TRANSLATION.get(rank_en, rank_en)

                    text = (f"🎮 **Нерейтинг:** {pubs_ru}\n"
                            f"🏆 **Рейтинг:** {rank_ru}\n"
                            f"⏳ До смены: {time_rank}")
                    await message.answer(text, parse_mode="Markdown")
        except Exception as e:
            await message.answer("⚠️ Не удалось получить карты.")

@dp.message(Command("predator"))
async def cmd_predator(message: types.Message):
    url = f"https://api.mozambiquehe.re/predator?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                data = await response.json(content_type=None)
                pc = data.get('RP', {}).get('PC', {}).get('val', 0)
                masters = data.get('RP', {}).get('PC', {}).get('totalMastersAndPreds', 0)
                msg = (f"🎖 **Порог Predator (PC):** `{pc}` RP\n"
                       f"👥 Всего мастеров: `{masters}`")
                await message.answer(msg, parse_mode="Markdown")
        except:
            await message.answer("⚠️ Ошибка API Predator.")

@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    url = f"https://api.mozambiquehe.re/news?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                data = await response.json(content_type=None)
                msg = "📰 **Новости Apex:**\n\n"
                for item in data[:3]:
                    msg += f"🔥 {item.get('title')}\n🔗 [Читать]({item.get('link')})\n\n"
                await message.answer(msg, parse_mode="Markdown", disable_web_page_preview=False)
        except:
            await message.answer("⚠️ Ошибка новостей.")

@dp.message(Command("legends"))
async def cmd_legends(message: types.Message):
    text = ("📊 **Популярность легенд (Мета):**\n"
            "1. **Октейн** — `16.7%` \n"
            "2. **Бангалор** — `8.3%` \n"
            "3. **Валькирия** — `7.5%` \n"
            "4. **Лайфлайн** — `6.0%` \n"
            "💡 _Данные обновляются раз в сутки._")
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("store"))
async def cmd_store(message: types.Message):
    url = f"https://api.mozambiquehe.re/store?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                data = await response.json(content_type=None)
                msg = "🛒 **Магазин:**\n\n"
                for item in data[:3]:
                    msg += f"🎁 {item.get('title')} — `{item.get('pricing')[0].get('price')}` монет\n"
                await message.answer(msg, parse_mode="Markdown")
        except:
            await message.answer("🏪 Магазин временно недоступен.")

# --- VERCEL ---
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_dict = json.loads(post_data.decode('utf-8'))
        
        async def process_update():
            update = Update.model_validate(update_dict, context={"bot": bot})
            await dp.feed_update(bot, update)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(process_update())
        finally:
            loop.close()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Apex Bot is Running!')