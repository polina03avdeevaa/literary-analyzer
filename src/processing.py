import re
from collections import Counter

from nltk.tokenize import word_tokenize


STOP_WORDS = {  
    'ru': set("""
        а без более бы был была были было быть в вам вас весь во вот
        все всего всех вы где да даже для до его ее если есть еще же за
        здесь и из или им их к как ко когда кто ли либо мне много мы на
        над надо наш не него нее нет ни них но ну о об однако он она они
        оно от очень по под при про раз с сам со так также такой там те
        тем то того той только том ты у уже хоть чего чем что чтобы эта
        эти это я меня тебе тебя собой себе свой свою свои своего 
    """.split()),
    'en': set("""
        a an and are as at be been being but by for from had has have he
        her hers him his i if in into is it its me my of on or our ours
        she so than that the their theirs them then there these they this
        those to too us was we were what when where which who why will
        with you your yours
    """.split()),
    'fr': set("""
        au aux avec ce ces dans de des du elle en et eux il ils je la le
        les leur lui ma mais me meme mes moi mon ne nos notre nous on ou
        par pas pour qu que quelle quelles qui sa se ses son sur ta te tes
        toi ton tu un une vos votre vous c est suis sont ete
    """.split()),
    'de': set("""
        aber als am an auch auf aus bei bin bis bist da dadurch daher
        darum das dass dein deine dem den der des die dies diese dieser
        doch dort du durch ein eine einem einen einer eines er es etwas
        für gegen gewesen hat hatte haben hier ich im in ist ja jede jeder
        jedes kann kein keine mit nach nicht nichts noch nun nur ob oder
        ohne sein seine sich sie sind so über um und uns unser unter vom
        von vor war waren was weil weiter welche wenn werden wie wieder
        wir wo zu zum zur
    """.split()),
}   # При необходимости список можно расширить


def normalize_text(text: str) -> str:
    """
    Функция нормализует пробелы и переносы строк, сохраняя содержание текста.
    Последующая обработка выполняется в других функциях.
    """
    if not isinstance(text, str):
        raise TypeError(
            'Содержимое текста должно быть строкой. Добавьте строку.'
        )

    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def tokenize(text: str) -> list[str]:
    """
    Функция разбивает текст на токены, сохраняя исходный регистр.
    """
    if not isinstance(text, str):
        raise TypeError(
            'Содержимое текста должно быть строкой. Добавьте строку.'
        )

    # Разбиваем текст на токены без отдельной модели для предложений.
    return word_tokenize(text, preserve_line=True)


def tokenize_words(text: str) -> list[str]:
    """
    Функция возвращает слова без пунктуации, не учитывая регистр.
    """
    tokens = tokenize(text)
    words = []

    for token in tokens:
        # Исключаем подчеркивания и знаки препинания.
        token_words = re.findall(
            r'[^\W_]+',
            token,
            flags=re.UNICODE,
        )
        words.extend(word.casefold() for word in token_words)

    return words


def get_stop_words(language_code: str = 'ru') -> set[str]:
    """
    Функция возвращает набор стоп-слов для поддерживаемого языка.
    """
    if not isinstance(language_code, str):
        raise TypeError('Код языка должен быть строкой.')

    return STOP_WORDS.get(language_code.casefold(), set()).copy()


def filter_stop_words(words: list[str], language_code: str = 'ru',) -> list[str]:
    """
    Функция исключает стоп-слова из списка токенов.
    """
    stop_words = get_stop_words(language_code)
    return [word for word in words if word not in stop_words]


def count_sentences(text: str) -> int:
    """
    Функция, которая приблизительно считает предложения по конечной пунктуации.
    Сокращения и некоторые нестандартные случаи могут учитываться неточно.
    """
    if not isinstance(text, str):
        raise TypeError(
            'Содержимое текста должно быть строкой. Добавьте строку.'
        )

    text = text.strip()

    if not text:
        return 0

    # Несколько знаков подряд считаются одним окончанием предложения.
    punctuation_chars = re.findall(r'[.!?…]+', text)

    return len(punctuation_chars) if punctuation_chars else 1


def calculate_average_sentence_length(text: str) -> float:
    """
    Функция, которая рассчитывает среднее количество слов в предложении.
    """
    words = tokenize_words(text)
    sentences = count_sentences(text)

    if sentences == 0:
        return 0.0

    return round(len(words) / sentences, 2)


def calculate_ttr(text: str) -> float:
    """
    Функция, которая рассчитывает отношение уникальных слов к общему числу слов.
    """
    words = tokenize_words(text)

    if not words:
        return 0.0

    return round(len(set(words)) / len(words), 4)


def calculate_msttr(text: str, segment_size: int = 100) -> float:
    """
    Функция рассчитывает среднее TTR последовательных сегментов фиксированного
    размера. Последний неполный сегмент не учитывается.
    """
    if not isinstance(segment_size, int) or isinstance(segment_size, bool):
        raise TypeError('Размер сегмента должен быть целым числом.')

    if segment_size < 1:
        raise ValueError('Размер сегмента должен быть положительным.')

    words = tokenize_words(text)

    if len(words) < segment_size:
        return 0.0

    segment_ttrs = []

    # Считаем TTR отдельно для каждого сегмента.
    for start in range(0, len(words) - segment_size + 1, segment_size):
        segment = words[start:start + segment_size]
        segment_ttrs.append(len(set(segment)) / len(segment))

    if not segment_ttrs:
        return 0.0

    return round(sum(segment_ttrs) / len(segment_ttrs), 4)


def get_word_frequencies(text: str, top_n: int = 10, remove_stop_words: bool = True, language_code: str = 'ru',) -> list[tuple[str, int]]:
    """
    Функция возвращает наиболее частотные слова.

    Стоп-слова исключаются по умолчанию. Для полного списка слов
    установите remove_stop_words=False.
    """
    if not isinstance(top_n, int) or isinstance(top_n, bool):
        raise TypeError('Количество слов должно быть целым числом.')

    if top_n < 1:
        raise ValueError('Количество слов должно быть положительным.')

    if not isinstance(remove_stop_words, bool):
        raise TypeError('Параметр фильтрации должен быть логическим.')

    words = tokenize_words(text)

    # Убираем стоп-слова только для частотного анализа.
    if remove_stop_words:
        words = filter_stop_words(words, language_code)

    return Counter(words).most_common(top_n)


def calculate_text_metrics(text: str) -> dict[str, int | float]:
    """
    Функция рассчитывает количественные характеристики текста.
    Все метрики, кроме специально фильтруемого частотного анализа,
    учитывают исходную лексику, включая стоп-слова.
    """
    normalized_text = normalize_text(text)

    if not normalized_text:
        raise ValueError(
            'Не добавлен текст. Нельзя анализировать пустой текст.'
        )

    words = tokenize_words(normalized_text)
    unique_words = set(words)

    word_count = len(words)
    unique_words_count = len(unique_words)
    total_word_length = sum(len(word) for word in words)

    return {
        'Количество символов': len(normalized_text),
        'Количество слов': word_count,
        'Количество уникальных слов': unique_words_count,
        'Количество предложений': count_sentences(normalized_text),
        'Средняя длина слова': (
            round(total_word_length / word_count, 2)
            if word_count > 0
            else 0.0
        ),
        'Средняя длина предложения': calculate_average_sentence_length(
            normalized_text
        ),
        'Лексическое разнообразие (TTR)': calculate_ttr(normalized_text),
        'Лексическое разнообразие (MSTTR)': calculate_msttr(
            normalized_text
        ),
    }
