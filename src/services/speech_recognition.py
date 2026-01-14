import gigaam

# Глобальная модель (загружается 1 раз)
_model = None


def speech_to_text(wav_path: str) -> str:
    global _model

    if _model is None:
        # ЛУЧШАЯ модель для фамилий и дат
        _model = gigaam.load_model("e2e_rnnt")

    text = _model.transcribe(wav_path)
    return text
