import os
import json as json_lib
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from pydub import AudioSegment

from config import BOT_TOKEN
from src.services.speech_recognition import speech_to_text
from src.services.text_processing import extract_info


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def convert_to_wav(input_path: str, output_path: str):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
    audio.export(output_path, format="wav")


def save_txt_from_dict(info: dict, path: str):
    """Сохраняем словарь в TXT в формате ключ: значение"""
    with open(path, "w", encoding="utf-8") as f:
        for key, value in info.items():
            f.write(f"{key}: {value}\n")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎤 Пришли голосовое сообщение.\n"
        "Я распознаю ФИО, дату и задачу и пришлю TXT-файл."
    )


@dp.message()
async def voice_handler(message: types.Message):
    if not message.voice:
        return

    file_id = message.voice.file_id

    ogg_path = f"/tmp/{file_id}.ogg"
    wav_path = f"/tmp/{file_id}.wav"
    json_path = f"/tmp/{file_id}.json"  # пока оставляем для БД
    txt_path = f"/tmp/{file_id}.txt"

    try:
        # --- скачиваем файл ---
        file = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                with open(ogg_path, "wb") as f:
                    f.write(await resp.read())

        # --- конвертация ---
        convert_to_wav(ogg_path, wav_path)

        # --- распознавание ---
        text = speech_to_text(wav_path)
        info = extract_info(text)

        print("Распознанный текст:", text)
        print("Извлечённая информация:", info)

        # --- сохраняем JSON для БД ---
        with open(json_path, "w", encoding="utf-8") as f:
            json_lib.dump(info, f, ensure_ascii=False, indent=2)

        # --- сохраняем TXT для пользователя ---
        save_txt_from_dict(info, txt_path)

        # --- отправка пользователю только TXT ---
        await message.answer(f"📝 Распознанный текст:\n{text}")
        await message.answer_document(FSInputFile(txt_path))

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    finally:
        for path in (ogg_path, wav_path, txt_path):
            if os.path.exists(path):
                os.remove(path)
        # json_path оставляем, его потом будет использовать БД


if __name__ == "__main__":
    dp.run_polling(bot)
