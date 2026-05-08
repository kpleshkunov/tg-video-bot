import os
import asyncio
import yt_dlp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

TOKEN = os.environ.get("TOKEN")

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Отправь ссылку на видео:\n"
        "YouTube / TikTok / Instagram / VK"
    )


@dp.message()
async def handler(message: types.Message):
    url = (message.text or "").strip()

    # 1. защита от мусора
    if not url.startswith("http"):
        await message.answer("Нужно отправить ссылку (http/https)")
        return

    await message.answer("Обрабатываю запрос...")

    file_path = None

    ydl_opts = {
        "outtmpl": f"{DOWNLOADS_DIR}/%(title).50s.%(ext)s",
        "format": "mp4/best",
        "noplaylist": True,
        "quiet": True,

        # стабильность
        "retries": 5,
        "socket_timeout": 30,
        "nocheckcertificate": True,
        "concurrent_fragment_downloads": 2,

        # помогает YouTube
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        }
    }

    try:
        loop = asyncio.get_event_loop()

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        file_path = await loop.run_in_executor(None, download)

        if not file_path or not os.path.exists(file_path):
            await message.answer("Не удалось скачать видео")
            return

        video = FSInputFile(file_path)

        try:
            await message.answer_video(video)
        except Exception:
            await message.answer_document(video)

    except Exception as e:
        await message.answer(f"Ошибка при обработке:\n{str(e)[:400]}")

    finally:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass


async def main():
    if not TOKEN:
        raise ValueError("TOKEN не задан в переменных среды")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
