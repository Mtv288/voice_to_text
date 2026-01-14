import gigaam

_model = None


def speech_to_text(wav_path: str) -> str:
    global _model

    if _model is None:
        print(">>> Загружаю GigaAM модель v2_rnnt")
        _model = gigaam.load_model("v2_rnnt")
        print(">>> Модель загружена")

    print(">>> Распознаю файл:", wav_path)
    text = _model.transcribe(wav_path)
    print(">>> Результат распознавания:", text)

    return text
