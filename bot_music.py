import requests
import random
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = ""
YOUTUBE_API_KEY = ""

CHAT_IDS = [-1234567890, -1234567890]

QUERIES = [
    "official music video",
    "hip hop music video",
    "rap music video",
    "pop music video"
]


def get_random_videos():
    query = random.choice(QUERIES)

    print(f"[DEBUG] Запрос: {query}")

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }

    r = requests.get(url, params=params).json()

    items = r.get("items", [])

    if not items:
        return [("Ошибка API", "dQw4w9WgXcQ")]

    videos = []

    for item in items:
        try:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            videos.append((title, video_id))
        except:
            pass

    return random.sample(videos, min(3, len(videos)))


async def send_random_music(context: ContextTypes.DEFAULT_TYPE):
    print("[DEBUG] send_random_music")

    try:
        videos = get_random_videos()

        text = "🎵 Случайные клипы:\n\n"

        for title, vid in videos:
            text += f"{title}\nhttps://youtube.com/watch?v={vid}\n\n"

        # ✅ ОТПРАВКА В НЕСКОЛЬКО ЧАТОВ
        for chat_id in CHAT_IDS:
            try:
                await context.bot.send_message(chat_id=chat_id, text=text)
                print(f"[OK] отправлено в {chat_id}")
            except Exception as e:
                print(f"[ERROR] чат {chat_id}:", e)

    except Exception as e:
        print("[ERROR]:", e)


async def startmusic(update, context):
    print("[DEBUG] START")

    await update.message.reply_text("Бот запущен 🎧")

    # сразу отправка
    await send_random_music(context)

    # каждые 5 минут (300 сек)
    context.job_queue.run_repeating(
        send_random_music,
        interval=300,
        first=10
    )


def error_handler(update, context):
    print(f"[CRASH]: {context.error}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("startmusic", startmusic))
app.add_error_handler(error_handler)

print("🚀 Бот запущен...")

app.run_polling()