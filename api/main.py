import asyncio
import os
import json
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from http.server import BaseHTTPRequestHandler

# --- 1. НАСТРОЙКИ ---

TELEGRAM_TOKEN = "8205546825:AAE_f2o4Flap-omNJK_6R61iHHZjEbbghsE"
APEX_API_KEY = "02bc8279638509d6997130e7fc25273f"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

MAP_TRANSLATION = {
    "World's Edge": "🌋 Край Света",
    "Storm Point": "⛈ Место Бури",
    "Broken Moon": "🌒 Расколотая Луна",
    "Olympus": "☁️ Олимп",
    "Kings Canyon": "🦖 Каньон Кингс",
    "E-District": "🌃 Квартал Электро",
}

MAP_IMAGES = {
    "World's Edge": "https://apexlegendsstatus.com/assets/maps/Worlds_Edge.png",
    "Storm Point": "https://apexlegendsstatus.com/assets/maps/Storm_Point.png",
    "Broken Moon": "https://apexlegendsstatus.com/assets/maps/Broken_Moon.png",
    "Olympus": "https://apexlegendsstatus.com/assets/maps/Olympus.png",
    "Kings Canyon": "https://apexlegendsstatus.com/assets/maps/Kings_Canyon.png",
    "E-District": "https://apexlegendsstatus.com/assets/maps/District.png"
}

# --- 2. МЕНЮ ---

def get_main_menu():
    kb = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🗺 Карты")],
        [KeyboardButton(text="📊 Мета Легенд"), KeyboardButton(text="🏆 Рейтинг (RP)")],
        [KeyboardButton(text="📰 Новости"), KeyboardButton(text="🛒 Магазин")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, 
        resize_keyboard=True, 
        input_field_placeholder="Выберите раздел..."
    )


# --- 3. ФУНКЦИИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 **Привет, {message.from_user.first_name}!**\n\n"
        "Я — Apex Tracker Bot. Я помогу тебе найти любую информацию.\n",
        parse_mode="Markdown",
        reply_markup=get_main_menu(),
    )


# --- КНОПКИ МЕНЮ ---

@dp.message(F.text == "🗺 Карты")
async def show_maps(message: types.Message):
    url = f"https://api.mozambiquehe.re/maprotation?auth={APEX_API_KEY}&version=2"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                
                pub = data['battle_royale']['current']
                pub_map = pub['map']
                pub_img = MAP_IMAGES.get(pub_map, "https://apexlegendsstatus.com/assets/maps/Worlds_Edge.png")
                pub_ru = MAP_TRANSLATION.get(pub_map, pub_map)
                
                rnk = data['ranked']['current']
                rnk_map = rnk['map']
                rnk_img = MAP_IMAGES.get(rnk_map, "https://apexlegendsstatus.com/assets/maps/Worlds_Edge.png")
                rnk_ru = MAP_TRANSLATION.get(rnk_map, rnk_map)

                caption = (
                    "🎮 **ОБЫЧНЫЕ МАТЧИ (Pubs):**\n"
                    f"📍 Сейчас: **{pub_ru}**\n"
                    f"⏱ До смены: `{pub['remainingTimer']}`\n"
                    f"🔜 След.: _{MAP_TRANSLATION.get(data['battle_royale']['next']['map'])}_\n\n"
                    "--- --- --- --- ---\n\n"
                    "🏆 **РЕЙТИНГОВЫЕ МАТЧИ (Ranked):**\n"
                    f"📍 Сейчас: **{rnk_ru}**\n"
                    f"⏱ До смены: `{rnk['remainingTimer']}`\n"
                )

                await message.answer_photo(
                    photo=rnk_img, 
                    caption=caption, 
                    parse_mode="Markdown"
                )
        except Exception as e:
            await message.answer("⚠️ Не удалось получить актуальную ротацию. Проверьте позже.")


@dp.message(F.text == "🏆 Рейтинг (RP)")
async def show_predator(message: types.Message):
    url = f"https://api.mozambiquehe.re/predator?auth={APEX_API_KEY}"
    pred_img = "https://apexlegendsstatus.com/assets/ranks/apex_predator.png"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    await message.answer(f"❌ Ошибка сервера API (Код: {response.status}). Попробуйте позже.")
                    return
                
                data = await response.json()
                
                rp_data = data.get('RP', {})
                pc = rp_data.get('PC', {})
                
                if not pc:
                    await message.answer("⚠️ Данные для PC временно недоступны в API. Попробуйте через 5 минут.")
                    return
                
                val = pc.get('val', 'N/A')
                total = pc.get('totalMastersAndPreds', 'N/A')
                
                caption = (
                    "🎖 **ЛИМИТЫ Predator (PC):**\n\n"
                    f"🔴 **Порог Predator:** `{val}` RP\n"
                    f"🟣 **Мастеров и Predator всего:** `{total}`\n\n"
                    " Чтобы попасть в топ-750, нужно набрать больше RP, чем у последнего Predatorа."
                )
                await message.answer_photo(photo=pred_img, caption=caption, parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"⚠️ Ошибка связи: {str(e)[:30]}...")
            
            
@dp.message(F.text == "📊 Мета Легенд")
async def show_meta(message: types.Message):
    meta_img = "https://images.wallpapersden.com/image/download/apex-legends-bloodhound-loba-and-caustic-skin_bmZuamWUmZqaraWkpJRmbmdlrWZlbWU.jpg"
    
    caption = (
        "📊 **АКТУАЛЬНАЯ МЕТА (Сезон 23):**\n\n"
        "🔥 **S-Тир:** Lifeline, Newcastle, Revenant\n"
        "⚡️ **A-Тир:** Octane, Pathfinder, Horizon\n"
        "🛡 **B-Тир:** Bangalore, Wattson, Conduit\n\n"
        "📉 *Выбор игроков основывается на пикрейте в рейтинговых матчах.*"
    )
    await message.answer_photo(photo=meta_img, caption=caption, parse_mode="Markdown")


@dp.message(F.text == "📰 Новости")
async def show_news(message: types.Message):
    url = f"https://api.mozambiquehe.re/news?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                latest = data[0] # Берем самую свежую новость
                
                img = latest.get('img', "https://top-mmorpg.ru/uploads/posts/2023-02/apex-legends-reveal-trailer.jpg")
                caption = (
                    f"🔥 **ПОСЛЕДНИЕ НОВОСТИ:**\n\n"
                    f"📌 **{latest['title']}**\n\n"
                    f"📖 {latest.get('short_desc', '')[:150]}...\n\n"
                    f"🔗 [Читать полностью]({latest['link']})"
                )
                await message.answer_photo(photo=img, caption=caption, parse_mode="Markdown")
        except:
            await message.answer("⚠️ Не удалось загрузить новости.")


@dp.message(F.text == "🛒 Магазин")
async def show_store(message: types.Message):
    await message.answer(
        "🛒 Полный ассортимент доступен только в игре.\nПроверяй ротацию бандлов каждый вторник!"
    )

# --- 1. ОБРАБОТКА КНОПКИ В МЕНЮ ---
@dp.message(F.text == "📊 Статистика")
async def stats_help(message: types.Message):
    await message.answer(
        "Чтобы узнать статистику, введите команду и ник игрока через пробел.\n\n"
        "Пример: `/stats ImperialHal`",
        parse_mode="Markdown"
    )

# --- 2. КОМАНДА /stats ---
@dp.message(Command("stats"))
async def get_player_stats(message: types.Message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("❌ Введите ник! Пример: `/stats ImperialHal`")
        return

    nickname = args[1]
    msg_wait = await message.answer(f"🔎 Сканирую базу данных для **{nickname}**...")

    url = f"https://api.mozambiquehe.re/bridge?auth={APEX_API_KEY}&player={nickname}&platform=PC"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                data = await response.json()

                if "Error" in data or response.status != 200:
                    await msg_wait.edit_text("❌ Игрок не найден. Убедись, что ник верный и это PC версия.")
                    return

                glob = data.get("global", {})
                rank = glob.get("rank", {})
                real_time = data.get("realtime", {})
                
                name = glob.get("name", nickname)
                level = glob.get("level", 0)
                rank_name = rank.get("rankName", "Unranked")
                rank_div = rank.get("rankDiv", "")
                rank_score = rank.get("rankScore", 0)

                rank_icon = rank.get("rankImg")
                selected_legend = data.get("legends", {}).get("selected", {})
                legend_name = selected_legend.get("LegendName", "Unknown")
                
                status = "🟢 В игре" if real_time.get("isOnline") == 1 else "🔴 Оффлайн"

                caption = (
                    f"👤 **Легенда:** `{name}`\n"
                    f"🆙 **Уровень:** {level} | {status}\n\n"
                    f"🏆 **Ранг:** {rank_name} {rank_div}\n"
                    f"💎 **Очки (RP):** {rank_score}\n"
                    f"🎭 **Активный герой:** {legend_name}\n\n"
                    f"📈 _Статистика обновлена из API Синдиката_"
                )

                await msg_wait.delete()
                
                if rank_icon:
                    await message.answer_photo(photo=rank_icon, caption=caption, parse_mode="Markdown")
                else:
                    await message.answer(caption, parse_mode="Markdown")

        except Exception as e:
            await msg_wait.edit_text(f"⚠️ Ошибка API. Возможно, сервер перегружен.")


# --- VERCEL ---
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        try:
            update_dict = json.loads(post_data.decode("utf-8"))
        except:
            return

        async def process():
            async with bot.context():
                update = Update.model_validate(update_dict, context={"bot": bot})
                await dp.feed_update(bot, update)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process())
        loop.close()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Online")
