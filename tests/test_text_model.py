# Импорт базовой модели и классов-наследников.
from src.text_model import Text, UploadedText, ManualText


def test_uploaded_text():
    """
    Функция проверяет создание текста из загруженного файла.
    """

    text = UploadedText(
        content='Через базарную площадь идет полицейский надзиратель Очумелов в новой шинели и с узелком в руке. За ним шагает рыжий городовой с решетом, доверху наполненным конфискованным крыжовником. Кругом тишина...',
        source_name='chekhov.txt',
        title='Хамелеон',
        author='А.П. Чехов',
    )

    # Проверяем, что объект сохраняет данные файла и произведения.
    assert isinstance(text, Text)
    assert text.source_type == 'file_upload'
    assert text.source_name == 'chekhov.txt'
    assert text.title == 'Хамелеон'
    assert text.author == 'А.П. Чехов'


def test_manual_text():
    """
    Функция проверяет создание текста, введенного вручную.
    """

    text = ManualText(
        content='Какой-то тестовый текст, введенный вручную.',
        title='Мой текст',
        author='Неизвестный автор',
    )

    # Проверяем тип источника и сохранение метаданных.
    assert isinstance(text, Text)
    assert text.source_type == 'user_input'
    assert text.source_name is None
    assert text.title == 'Мой текст'
    assert text.author =='Неизвестный автор'


def test_uploaded_text_rejects_empty_content():
    """
    Функция для проверки наследование проверки пустого содержимого.
    """

    import pytest

    # Подкласс должен использовать проверку родительского класса Text.
    with pytest.raises(ValueError):
        UploadedText(content='   ', source_name='empty.txt')
