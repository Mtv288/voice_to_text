import os
import json
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputFile
from pydub import AudioSegment


from config import BOT_TOKEN
from services.speech_recognition import speech_to_text
from services.text_processing import extract_info


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def convert_to_wav(input_path: str, output_path: str):
    audio = AudioSegment.from_file(input_path)
    audio = (
        audio
        .set_channels(1)
        .set_sample_width(2)   # 16-bit
        .set_frame_rate(16000)
    )
    audio.export(output_path, format="wav")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Пришли голосовое сообщение.\n"
        "Я распознаю ФИО, дату и задачу."
    )


@dp.message()
async def voice_handler(message: types.Message):
    if not message.voice:
        return

    ogg_path = f"temp_{message.voice.file_id}.ogg"
    wav_path = f"temp_{message.voice.file_id}.wav"
    json_path = f"order_{message.voice.file_id}.json"

    try:
        # --- скачиваем файл ---
        file = await bot.get_file(message.voice.file_id)
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

        # --- сохраняем JSON ---
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        # --- отправка ---
        await message.answer(f"Распознанный текст:\n{text}")
        await message.answer_document(InputFile(json_path))

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

    finally:
        for p in (ogg_path, wav_path, json_path):
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    dp.run_polling(bot)










