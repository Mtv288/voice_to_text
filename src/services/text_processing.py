from natasha import MorphVocab, NamesExtractor, DatesExtractor

morph_vocab = MorphVocab()
names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)


def extract_info(text: str) -> dict:
    fio = ""
    date = ""
    task = text

    # --- ФИО ---
    names = list(names_extractor(text))
    if names:
        f = names[0].fact
        fio = " ".join(filter(None, [f.last, f.first, f.middle]))
        task = task.replace(names[0].text, "").strip()

    # --- ДАТА ---
    dates = list(dates_extractor(text))
    if dates:
        d = dates[0].fact
        date = f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
        task = task.replace(dates[0].text, "").strip()

    return {
        "заказчик": fio,
        "дата": date,
        "задача": task
    }
