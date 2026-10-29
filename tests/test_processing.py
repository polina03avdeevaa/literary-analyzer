
import pytest

from src.processing import(
    normalize_text,
    tokenize,
    tokenize_words,
    count_sentences,
    calculate_average_sentence_length,
    calculate_ttr,
    get_word_frequencies,
    calculate_text_metrics
)


def test_normalize_text():

    """
    Функция для проверки нормализации пробелов и переносов строк
    """

    assert normalize_text(' Тестовый_текст_без_пробелов\r\n') == 'Тестовый_текст_без_пробелов'
    assert normalize_text('Тестовый   текст с пробелами') == 'Тестовый текст с пробелами'


def test_normalize_text_paragraphs_and_punctuation():

    """
    Функция для проверки нормализации абзацев и знаков препинания
    """

    text = 'Тестовый текст для первого абзаца... \n\n Ну и немного для второго абазаца!'

    assert normalize_text(text) == text


def test_normalize_text_without_outer_spaces():

    """
    Функция для проверки удаления пробелов по краям текста
    """

    assert normalize_text('   Текст с пробелами   ') == 'Текст с пробелами'


def test_tokenize():

    """
    Функция для проверки токенизации текста с сохранением знаков препинания
    """

    assert tokenize('Привет, мир!') == ['Привет', ',', 'мир', '!']


def test_tokenize_words():

    """
    Функция для проверки токенизации слов.

    Без учета регистра.
    """

    assert tokenize_words('Достоевский, БЕСЫ? Ну нет. No...') == [
        'достоевский', 'бесы', 'ну', 'нет', 'no'
    ]


def test_tokenize_words_without_punctuation():

    """
    Функция для проверки исключения знаков препинания из списка слов
    """

    assert tokenize_words('Слово!!! ... Еще слово?') == ['слово', 'еще', 'слово']


def test_count_sentences():

    """
    Функция для проверки корректного подсчета предложений.

    Базовая, если есть пунктуация и предложения действительно делятся.
    """

    assert count_sentences('Первое предложение! Второе предложение... Третье? Четвертое.') == 4


def test_count_sentences_without_punctuation():

    """
    Функция для проверки корректного подсчета предложений.

    В случаях, когда предложения по какой-то причине не содержат пунктуацию.
    """

    assert count_sentences('Одно длинное предложение без пунктуации в конце') == 1


def test_count_sentences_without_text():

    """
    Функция для проверки корректного подсчета предложений.

    В случаях, когда предложение по какой-то причине не содержит текст.

    То есть, пустая строка.
    """

    assert count_sentences('   ') == 0


def test_count_sentences_with_consecutive_punctuation():

    """
    Функция для проверки подсчета последовательностей знаков препинания.

    Несколько знаков подряд считаются одним завершением предложения.
    """

    assert count_sentences('Что?! Да... Конечно!!!') == 3


def test_calculate_average_sentence_length():

    """
    Функция для проверки расчета средней длины предложения
    """

    text = 'Мама мыла раму. Папа читал книгу.'

    assert calculate_average_sentence_length(text) == 3.0


def test_calculate_average_sentence_length_without_text():

    """
    Функция для проверки средней длины предложения без текста
    """

    assert calculate_average_sentence_length('') == 0.0


def test_calculate_ttr():

    """
    Функция для проверки расчета лексического разнообразия
    """

    assert calculate_ttr('кот кот пес пес') == 0.5


def test_calculate_ttr_without_text():

    """
    Функция для проверки лексического разнообразия без слов
    """

    assert calculate_ttr('') == 0.0


def test_get_word_frequencies():

    """
    Функция для проверки подсчета частотности слов
    """

    assert get_word_frequencies('кот пес кот кот пес', top_n=2) == [
        ('кот', 3), ('пес', 2)
    ]


def test_get_word_frequencies_default_limit():

    """
    Функция для проверки количества слов по умолчанию
    """

    assert get_word_frequencies('кот пес кот') == [
        ('кот', 2), ('пес', 1)
    ]


def test_get_word_frequencies_invalid_limit():

    """
    Функция для проверки обработки некорректного количества слов
    """

    with pytest.raises(ValueError):
        get_word_frequencies('кот пес', top_n=0)


def test_get_word_frequencies_non_integer_limit():

    """
    Функция для проверки, что количество слов должно быть целым числом
    """

    with pytest.raises(TypeError):
        get_word_frequencies('кот пес', top_n=1.5)


def test_calculate_empty_text_metrics():

    """
    Функция для проверки, будет ли анализироваться пустой текст.
    """

    with pytest.raises(ValueError):
        calculate_text_metrics('   ')


def test_calculate_line_without_words_metrics():

    """
    Функция для проверки, что будет, если не дать сам текст.

    Для эксперимента дается текст, состоящий из знаков препинания.
    """

    metrics_without_text = calculate_text_metrics('!?')

    assert metrics_without_text['Количество символов'] == 2
    assert metrics_without_text['Количество слов'] == 0
    assert metrics_without_text['Количество уникальных слов'] == 0
    assert metrics_without_text['Количество предложений'] == 1
    assert metrics_without_text['Средняя длина слова'] == 0.0
    assert metrics_without_text['Средняя длина предложения'] == 0.0
    assert metrics_without_text['Лексическое разнообразие (TTR)'] == 0.0


def test_calculate_text_metrics():

    """
    Функция для проверки корректного сбора всех указанных характеристик текста.

    Дается обычный текст (фрагмент произведения).
    """

    metrics = calculate_text_metrics(
        'Отца моего я не помню. Он умер, когда мне было два года. '
        'Мать моя вышла замуж в другой раз.'
    )

    assert metrics['Количество символов'] == 91
    assert metrics['Количество слов'] == 19
    assert metrics['Количество уникальных слов'] == 19
    assert metrics['Количество предложений'] == 3
    assert metrics['Средняя длина слова'] == 3.63
    assert metrics['Средняя длина предложения'] == 6.33
    assert metrics['Лексическое разнообразие (TTR)'] == 1.0
