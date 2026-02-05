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

# --- КАРТЫ (НАДЕЖНАЯ ВЕРСИЯ) ---
@dp.message(F.text == "🗺 Карты")
@dp.message(Command("map"))
async def show_maps(message: types.Message):
    url = f"https://api.mozambiquehe.re/maprotation?auth={APEX_API_KEY}&version=2"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                raw_text = await response.text()
                
                if response.status == 403:
                    await message.answer("❌ Ошибка: API Ключ неверный или заблокирован.")
                    return
                if "Slow down" in raw_text:
                    await message.answer("⏳ Слишком много запросов! Подождите 10-15 сек.")
                    return

                data = json.loads(raw_text)
                br = data.get('battle_royale', {}).get('current', {})
                rnk = data.get('ranked', {}).get('current', {})

                m_name = rnk.get('map', 'Unknown')
                img = MAP_IMAGES.get(m_name, "https://apexlegendsstatus.com/assets/maps/Worlds_Edge.png")
                
                caption = (
                    f"🎮 **Обычные:** {MAP_TRANSLATION.get(br.get('map'), br.get('map'))}\n"
                    f"⏱ Осталось: `{br.get('remainingTimer')}`\n\n"
                    f"🏆 **Рейтинг:** {MAP_TRANSLATION.get(m_name, m_name)}\n"
                    f"⏱ До смены: `{rnk.get('remainingTimer')}`"
                )
                await message.answer_photo(photo=img, caption=caption, parse_mode="Markdown")

        except Exception as e:
            await message.answer(f"⚠️ Ошибка API: `{str(e)[:50]}`")

# --- РЕЙТИНГ (НАДЕЖНАЯ ВЕРСИЯ) ---
@dp.message(F.text == "🏆 Рейтинг (RP)")
@dp.message(Command("predator"))
async def show_predator(message: types.Message):
    url = f"https://api.mozambiquehe.re/predator?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                raw_text = await response.text()
                
                if "Slow down" in raw_text:
                    await message.answer("⏳ Лимит запросов! Подожди немного.")
                    return
                
                data = json.loads(raw_text)
                pc = data.get('RP', {}).get('PC', {})
                
                caption = (
                    "🎖 **ЛИМИТЫ ХИЩНИКОВ (PC):**\n\n"
                    f"🔴 **Порог Predator:** `{pc.get('val', 'N/A')}` RP\n"
                    f"🟣 **Мастеров и Хищников:** `{pc.get('totalMastersAndPreds', 'N/A')}`"
                )
                await message.answer_photo(
                    photo="https://apexlegendsstatus.com/assets/ranks/apex_predator.png", 
                    caption=caption, 
                    parse_mode="Markdown"
                )
        except Exception as e:
            await message.answer(f"⚠️ Ошибка рейтинга: `{str(e)[:50]}`")
            
            
@dp.message(F.text == "📊 Мета Легенд")
@dp.message(Command("meta"))
async def show_meta(message: types.Message):
    meta_img = "https://images.wallpapersden.com/image/download/apex-legends-bloodhound-loba-and-caustic-skin_bmZuamWUmZqaraWkpJRmbmdlrWZlbWU.jpg"
    
    caption = (
        "📊 **АКТУАЛЬНАЯ МЕТА:**\n\n"
        "🔥 **S-Тир:** Lifeline, Newcastle, Revenant\n"
        "⚡️ **A-Тир:** Octane, Pathfinder, Horizon\n"
        "🛡 **B-Тир:** Bangalore, Wattson, Conduit\n\n"
        "📉 *Выбор игроков основывается на пикрейте в рейтинговых матчах.*"
    )
    await message.answer_photo(photo=meta_img, caption=caption, parse_mode="Markdown")


@dp.message(F.text == "📰 Новости")
@dp.message(Command("news"))
async def show_news(message: types.Message):
    url = f"https://api.mozambiquehe.re/news?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    await message.answer("📡 Сервер новостей временно недоступен.")
                    return
                
                data = await response.json()
                
                # Проверяем, что пришел список и он не пустой
                if not isinstance(data, list) or len(data) == 0:
                    await message.answer("📭 Свежих новостей пока нет. Заходите позже!")
                    return

                # Берем самую свежую новость (первую в списке)
                latest = data[0]
                title = latest.get('title', 'Заголовок отсутствует')
                link = latest.get('link', 'https://www.ea.com/games/apex-legends/news')
                img = latest.get('img', "https://top-mmorpg.ru/uploads/posts/2023-02/apex-legends-reveal-trailer.jpg")
                desc = latest.get('short_desc', 'Нажмите "Читать", чтобы узнать подробности.')

                # Ограничиваем длину описания, чтобы сообщение не было слишком длинным
                if len(desc) > 200:
                    desc = desc[:197] + "..."

                caption = (
                    f"🔥 **ПОСЛЕДНИЕ НОВОСТИ:**\n\n"
                    f"📌 **{title}**\n\n"
                    f"📝 {desc}\n\n"
                    f"🔗 [Читать полностью]({link})"
                )

                await message.answer_photo(
                    photo=img, 
                    caption=caption, 
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"News Error: {e}")
            await message.answer("⚠️ Не удалось загрузить новости. Попробуйте использовать команду `/news` еще раз.")


@dp.message(F.text == "🛒 Магазин")
@dp.message(Command("store"))
async def show_store(message: types.Message):
    await message.answer(
        "🛒 Полный ассортимент доступен только в игре.\nПроверяй ротацию бандлов каждый вторник!"
    )

# --- 1. ОБРАБОТКА КНОПКИ И КОМАНД-ПОДСКАЗОК ---
@dp.message(F.text == "📊 Статистика")
@dp.message(Command("stat_help"))
async def stats_help(message: types.Message):
    await message.answer(
        "🔎 Чтобы узнать статистику, введите команду и ник игрока.\n\n"
        "Пример: `/stats ImperialHal`",
        parse_mode="Markdown"
    )

# --- 2. ОСНОВНАЯ КОМАНДА (ПОНИМАЕТ И /stat И /stats) ---
@dp.message(Command("stat", "stats"))
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
                # Читаем как текст для проверки на ошибки лимита
                res_text = await response.text()
                
                if "Slow down" in res_text or "Too many requests" in res_text:
                    await msg_wait.edit_text("⏳ **Лимит запросов!** Подождите 10 секунд.")
                    return

                try:
                    data = json.loads(res_text)
                except json.JSONDecodeError:
                    await msg_wait.edit_text("⚠️ Ошибка API. Попробуйте позже.")
                    return

                if "Error" in data:
                    await msg_wait.edit_text("❌ Игрок не найден или профиль скрыт.")
                    return

                # Собираем данные
                glob = data.get("global", {})
                rank = glob.get("rank", {})
                real_time = data.get("realtime", {})
                
                name = glob.get("name", nickname)
                level = glob.get("level", 0)
                rank_name = rank.get("rankName", "Unranked")
                rank_div = rank.get("rankDiv", "")
                rank_score = rank.get("rankScore", 0)
                rank_icon = rank.get("rankImg")
                
                selected_legend = data.get("legends", {}).get("selected", {}).get("LegendName", "Unknown")
                status = "🟢 В игре" if real_time.get("isOnline") == 1 else "🔴 Оффлайн"

                caption = (
                    f"👤 **Легенда:** `{name}`\n"
                    f"🆙 **Уровень:** {level} | {status}\n\n"
                    f"🏆 **Ранг:** {rank_name} {rank_div}\n"
                    f"💎 **Очки (RP):** {rank_score}\n"
                    f"🎭 **Герой:** {selected_legend}"
                )

                await msg_wait.delete()
                await message.answer_photo(photo=rank_icon, caption=caption, parse_mode="Markdown")

        except Exception as e:
            await msg_wait.edit_text(f"⚠️ Ошибка связи с API.")


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
