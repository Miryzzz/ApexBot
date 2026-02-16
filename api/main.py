import asyncio
import os
import json
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup

# --- 1. НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8205546825:AAE_f2o4Flap-omNJK_6R61iHHZjEbbghsE"
APEX_API_KEY = "02bc8279638509d6997130e7fc25273f"

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
    "District": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2024/07/apex-e-district-map-thumbnail.jpg.adapt.1920w.jpg",
}

DEFAULT_MAP_IMG = "https://images.wallpapersden.com/image/download/apex-legends-all-characters_bWptZ2mUmZqaraWkpJRmbmdlrWZlbWU.jpg"

# --- 2. МЕНЮ ---
def get_main_menu():
    kb = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🗺 Карты")],
        [KeyboardButton(text="📊 Мета Легенд"), KeyboardButton(text="🏆 Рейтинг (RP)")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите раздел..."
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


async def parse_tracker_meta():
    url = "https://apex.tracker.gg/apex/insights"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                
                legends_data = []
                rows = soup.select(".insight-bar") 
                
                for row in rows:
                    name = row.select_one(".name").text.strip()
                    value = row.select_one(".value").text.strip() 
                    legends_data.append(f"**{name}**: `{value}`")
                
                return legends_data[:10] 
        except Exception as e:
            print(f"Parsing error: {e}")
            return None



# --- КНОПКИ МЕНЮ ---
@dp.message(F.text == "🏆 Рейтинг (RP)")
@dp.message(Command("predator"))
async def show_pred(message: types.Message):
    url = f"https://api.mozambiquehe.re/predator?auth={APEX_API_KEY}"
    
    wait_msg = await message.answer("⏳ Проверяем RP...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    await wait_msg.edit_text(f"📡 Ошибка API: {response.status}")
                    return

                res_text = await response.text()
                data = json.loads(res_text)

                # Проверка на ошибки внутри JSON
                if "Error" in data:
                     await wait_msg.edit_text("⚠️ Ошибка данных от API.")
                     return

                rp_data = data.get("RP", {})
                pc = rp_data.get("PC", {})

                val = pc.get("val", "N/A")
                total = pc.get("totalMastersAndPreds", "N/A")

                caption = (
                    "🎖 **ЛИМИТЫ ХИЩНИКОВ (PC):**\n\n"
                    f"🔴 **Порог Predator:** `{val}` RP\n"
                    f"🟣 **Мастеров и Хищников:** `{total}`\n\n"
                    "ℹ️ *Данные обновляются раз в несколько минут.*"
                )

                img = "https://apexlegendsstatus.com/assets/ranks/apex_predator.png"
                
                await wait_msg.delete()
                
                try:
                    await message.answer_photo(photo=img, caption=caption, parse_mode="Markdown")
                except Exception:
                    await message.answer(caption, parse_mode="Markdown")

        except Exception as e:
            await wait_msg.edit_text(f"⚠️ Ошибка: `{e}`")


@dp.message(F.text == "🗺 Карты")
@dp.message(Command("map"))
async def show_maps(message: types.Message):
    url = f"https://api.mozambiquehe.re/maprotation?auth={APEX_API_KEY}&version=2"
    
    wait_msg = await message.answer("⏳ Получаю данные о картах...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                
                br = data.get("battle_royale", {}).get("current", {})
                rnk = data.get("ranked", {}).get("current", {})

                pub_map = br.get("map", "Unknown")
                rank_map = rnk.get("map", "Unknown")

                # --- ЛОГИКА ВЫБОРА КАРТИНКИ ---
                map_image = MAP_IMAGES.get(rank_map, DEFAULT_MAP_IMG)

                text = (
                    "🗺 **ТЕКУЩАЯ РОТАЦИЯ**\n\n"
                    "🎮 **Обычные матчи:**\n"
                    f"📍 Карта: **{MAP_TRANSLATION.get(pub_map, pub_map)}**\n"
                    f"⏱ Осталось: `{br.get('remainingTimer')}`\n\n"
                    "━━━━━━━━━━━━━━\n\n"
                    "🏆 **Рейтинговые матчи:**\n"
                    f"📍 Карта: **{MAP_TRANSLATION.get(rank_map, rank_map)}**\n"
                    f"⏱ До смены: `{rnk.get('remainingTimer')}`"
                )

                await wait_msg.delete()

                try:
                    await message.answer_photo(photo=map_image, caption=text, parse_mode="Markdown")
                except Exception:
                    await message.answer(text, parse_mode="Markdown")

        except Exception as e:
            await wait_msg.edit_text(f"⚠️ Ошибка API: {e}")


@dp.message(F.text == "📊 Мета Легенд")
async def show_meta(message: types.Message):
    msg_wait = await message.answer("🔍 Пытаюсь пробиться через защиту Tracker.gg...")
    
    try:
        scraper = cloudscraper.create_scraper(
            delay=10, 
            browser={
                'browser': 'chrome',
                'name': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        url = "https://apex.tracker.gg/apex/insights"
        response = scraper.get(url, timeout=20)
        
        if response.status_code == 403:
            await msg_wait.edit_text("🚫 Ошибка 403: Сайт заблокировал сервер Vercel. Пробую альтернативный метод...")

            return

        soup = BeautifulSoup(response.text, "html.parser")
        
        legends = []
        items = soup.select(".insight-bar")
        
        for item in items[:10]:
            try:
                name = item.select_one(".name").text.strip()
                rate = item.select_one(".value").text.strip()
                legends.append(f"**{name}** — `{rate}`")
            except:
                continue

        if not legends:
            await msg_wait.edit_text("⚠️ Не удалось найти данные. Возможно, сайт изменил дизайн.")
            return

        text = "📊 **МЕТА С TRACKER.GG (LIVE):**\n\n" + "\n".join(legends)
        await msg_wait.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        await msg_wait.edit_text(f"⚠️ Ошибка парсинга: `{str(e)[:50]}`")

# --- 1. ОБРАБОТКА КНОПКИ И КОМАНД-ПОДСКАЗОК ---
@dp.message(F.text == "📊 Статистика")
@dp.message(Command("stat_help"))
async def stats_help(message: types.Message):
    await message.answer(
        "🔎 Чтобы узнать статистику, введите команду и ник игрока.\n\n"
        "Пример: `/stats ImperialHal`",
        parse_mode="Markdown",
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
                res_text = await response.text()

                if "Slow down" in res_text or "Too many requests" in res_text:
                    await msg_wait.edit_text(
                        "⏳ **Лимит запросов!** Подождите 10 секунд."
                    )
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

                selected_legend = (
                    data.get("legends", {})
                    .get("selected", {})
                    .get("LegendName", "Unknown")
                )
                status = "🟢 В игре" if real_time.get("isOnline") == 1 else "🔴 Оффлайн"

                caption = (
                    f"👤 **Легенда:** `{name}`\n"
                    f"🆙 **Уровень:** {level} | {status}\n\n"
                    f"🏆 **Ранг:** {rank_name} {rank_div}\n"
                    f"💎 **Очки (RP):** {rank_score}\n"
                    f"🎭 **Герой:** {selected_legend}"
                )

                await msg_wait.delete()
                await message.answer_photo(
                    photo=rank_icon, caption=caption, parse_mode="Markdown"
                )

        except Exception as e:
            await msg_wait.edit_text(f"⚠️ Ошибка связи с API.")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        
        try:
            update_dict = json.loads(post_data.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        # 1. Создаем новый цикл для этого запроса
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 2. Создаем бота ВНУТРИ цикла
        bot = Bot(token=TELEGRAM_TOKEN)

        try:
            # 3. Валидируем апдейт
            update = Update.model_validate(update_dict, context={"bot": bot})
            
            # 4. Запускаем обработку
            loop.run_until_complete(dp.feed_update(bot, update))
            
        except Exception as e:
            print(f"Error handling update: {e}")
        finally:
            # 5. Обязательно закрываем сессию бота перед закрытием цикла
            loop.run_until_complete(bot.session.close())
            loop.close()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Бот работает исправно!".encode('utf-8'))