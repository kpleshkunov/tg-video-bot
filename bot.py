
import os
import asyncio
import yt_dlp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

TOKEN = "8662790197:AAHTyhi1dG_s1M35MMFa2GCSBhKQ9760Znc"

bot = Bot(token=TOKEN)
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
async def download_video(message: types.Message):
    url = message.text.strip()

    await message.answer("Скачиваю видео...")

    file_path = None

    ydl_opts = {
        "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        "format": "mp4/best",
        "noplaylist": True,
        "quiet": True,

        # ВАЖНЫЕ СТАБИЛИЗАЦИИ
        "retries": 10,
        "socket_timeout": 30,
        "nocheckcertificate": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        video_file = FSInputFile(file_path)

        try:
            await message.answer_video(video_file)
        except:
            await message.answer_document(video_file)

    except Exception as e:
        await message.answer(f"Ошибка:\n{e}")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
