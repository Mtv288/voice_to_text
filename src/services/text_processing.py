from natasha import MorphVocab, NamesExtractor
from pymorphy2 import MorphAnalyzer
from dateparser.search import search_dates
import re

# --- Настройка ---
morph_vocab = MorphVocab()
names_extractor = NamesExtractor(morph_vocab)
morph_analyzer = MorphAnalyzer()

NUMBERS = {
    'первого': '1', 'второго': '2', 'третьего': '3', 'четвёртого': '4',
    'пятого': '5', 'шестого': '6', 'седьмого': '7', 'восьмого': '8',
    'девятого': '9', 'десятого': '10', 'одиннадцатого': '11', 'двенадцатого': '12',
    'тринадцатого': '13', 'четырнадцатого': '14', 'пятнадцатого': '15',
    'шестнадцатого': '16', 'семнадцатого': '17', 'восемнадцатого': '18',
    'девятнадцатого': '19', 'двадцатого': '20', 'двадцать первого': '21',
    'двадцать второго': '22', 'двадцать третьего': '23', 'двадцать четвёртого': '24',
    'двадцать пятого': '25', 'двадцать шестого': '26', 'двадцать седьмого': '27',
    'двадцать восьмого': '28', 'двадцать девятого': '29', 'тридцатого': '30',
    'тридцать первого': '31'
}

KEYWORDS = ['надо', 'сделать', 'организовать', 'проверить', 'выполнить', 'составить', 'провести', 'задача']

# --- нормализация слов в именительном падеже ---
def normalize_word(word: str, tag: str = 'nomn') -> str:
    p = morph_analyzer.parse(word)[0]
    inflected = p.inflect({tag})
    return inflected.word if inflected else p.word

# --- числа в цифры для корректного парсинга даты ---
def words_to_digits(text: str) -> str:
    for word, digit in NUMBERS.items():
        text = re.sub(r'\b{}\b'.format(re.escape(word)), digit, text, flags=re.IGNORECASE)
    return text

# --- извлечение ФИО, даты и задачи ---
def extract_info(text: str) -> dict:
    task_text = text
    fio = ""
    date_str = ""

    # --- ФИО ---
    words = text.split()
    if len(words) >= 3:
        fio_words = words[:3]
        fio = " ".join(normalize_word(w) for w in fio_words)
        task_text = " ".join(words[3:]).strip()

    # --- Дата ---
    task_text_for_dates = words_to_digits(task_text.lower())
    dates_found = search_dates(task_text_for_dates, languages=['ru'])
    if dates_found:
        date_text, dt = dates_found[0]
        date_str = dt.strftime("%Y-%m-%d")

        # Убираем слова даты и месяца из текста задачи
        task_text = task_text.replace(date_text, "")
        months = ['января','февраля','марта','апреля','мая','июня',
                  'июля','августа','сентября','октября','ноября','декабря']
        for m in months:
            task_text = re.sub(r'\b{}\b'.format(m), '', task_text, flags=re.IGNORECASE)

        task_text = re.sub(r'\s+', ' ', task_text).strip()

    # --- Задача по ключевым словам (первое вхождение) ---
    task_lower = task_text.lower()
    positions = [task_lower.find(k) for k in KEYWORDS if k in task_lower]
    if positions:
        start = min([pos for pos in positions if pos != -1])
        task_text = task_text[start:].strip()

    return {
        "заказчик": fio,
        "дата": date_str,
        "задача": task_text
    }

