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
    "World's Edge": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2022/07/apex-map-v3-worlds-edge.png.adapt.1920w.png",
    "Storm Point": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2021/10/apex-media-news-storm-point-map-thumbnail.jpg.adapt.1920w.jpg",
    "Broken Moon": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2022/10/apex-new-map-broken-moon-thumbnail.jpg.adapt.1920w.jpg",
    "Olympus": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2020/11/apex-media-news-olympus-map-thumbnail.jpg.adapt.1920w.jpg",
    "Kings Canyon": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2020/06/apex-media-news-kings-canyon-map-thumbnail.jpg.adapt.1920w.jpg",
    "E-District": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2024/07/apex-e-district-map-thumbnail.jpg.adapt.1920w.jpg",
    "District": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2024/07/apex-e-district-map-thumbnail.jpg.adapt.1920w.jpg"
}

DEFAULT_MAP_IMG = "https://images.wallpapersden.com/image/download/apex-legends-all-characters_bWptZ2mUmZqaraWkpJRmbmdlrWZlbWU.jpg"

# --- 2. МЕНЮ ---

def get_main_menu():
    kb = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🗺 Карты")],
        [KeyboardButton(text="📊 Мета Легенд"), KeyboardButton(text="🏆 Рейтинг (RP)")],
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

@dp.message(F.text == "🏆 Рейтинг (RP)")
@dp.message(Command("predator"))
async def show_pred(message: types.Message):
    url = f"https://api.mozambiquehe.re/predator?auth={APEX_API_KEY}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                # 1. Проверяем статус ответа
                if response.status != 200:
                    await message.answer(f"📡 Сервер API ответил ошибкой (Код: {response.status}).")
                    return

                res_text = await response.text()
                
                # 2. Проверяем на лимиты (Rate Limit)
                if "Slow down" in res_text or "Too many requests" in res_text:
                    await message.answer("⏳ **Слишком много запросов!** Подождите 10-15 секунд.")
                    return

                # 3. Пытаемся распарсить JSON
                try:
                    data = json.loads(res_text)
                except json.JSONDecodeError:
                    await message.answer("⚠️ Не удалось прочитать данные от сервера (ошибка JSON).")
                    return

                # 4. Извлекаем данные для PC
                rp_data = data.get('RP', {})
                pc = rp_data.get('PC', {})
                
                if not pc:
                    await message.answer("❌ Данные о рангах временно отсутствуют в базе API.")
                    return

                val = pc.get('val', 'N/A')
                total = pc.get('totalMastersAndPreds', 'N/A')
                
                caption = (
                    "🎖 **ЛИМИТЫ ХИЩНИКОВ (PC):**\n\n"
                    f"🔴 **Порог Predator:** `{val}` RP\n"
                    f"🟣 **Мастеров и Хищников:** `{total}`\n\n"
                    "Данные обновляются раз в несколько минут."
                )
                
                img = "https://apexlegendsstatus.com/assets/ranks/apex_predator.png"
                try:
                    await message.answer_photo(photo=img, caption=caption, parse_mode="Markdown")
                except Exception:
                    await message.answer(caption, parse_mode="Markdown")

        except asyncio.TimeoutError:
            await message.answer("⏳ Время ожидания истекло. Сервер API слишком долго не отвечал.")
        except Exception as e:
            await message.answer(f"⚠️ Ошибка связи: `{str(e)[:50]}`")

@dp.message(F.text == "🗺 Карты")
@dp.message(Command("map"))
async def show_maps(message: types.Message):
    url = f"https://api.mozambiquehe.re/maprotation?auth={APEX_API_KEY}&version=2"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                # Читаем текст, чтобы поймать ошибку лимита
                res_text = await response.text()
                if "Slow down" in res_text:
                    await message.answer("⏳ Слишком много запросов! Подождите 10 секунд.")
                    return
                
                data = json.loads(res_text)
                br = data.get('battle_royale', {}).get('current', {})
                rnk = data.get('ranked', {}).get('current', {})
                
                current_ranked_map = rnk.get('map', 'Unknown')
                
                caption = (
                    f"🎮 **ОБЫЧНЫЕ:** {MAP_TRANSLATION.get(br.get('map'), br.get('map'))}\n"
                    f"⏳ Осталось: `{br.get('remainingTimer')}`\n\n"
                    f"🏆 **РЕЙТИНГ:** {MAP_TRANSLATION.get(current_ranked_map, current_ranked_map)}\n"
                    f"⏳ Смена через: `{rnk.get('remainingTimer')}`"
                )

                # Выбираем картинку из нашего словаря
                photo_url = MAP_IMAGES.get(current_ranked_map, "https://media.contentapi.ea.com/content/dam/apex-legends/common/apex-legends-logo-desktop.svg")

                try:
                    await message.answer_photo(photo=photo_url, caption=caption, parse_mode="Markdown")
                except Exception as e:
                    # Если фото всё равно не уходит, отправляем хотя бы текст
                    await message.answer(f"{caption}\n\n⚠️ (Картинка не загрузилась: {str(e)[:30]})", parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"⚠️ Ошибка API: `{str(e)[:50]}`")
            
            
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
