from src.text_model import Text
from src.processing import calculate_text_metrics

def compare_texts(texts: list[Text]) -> list[dict]:
    """
    Функция, которая анализирует список произведений, а затем объединяет результаты в общую таблицу. 

    На вход принимается список объектов Text. 
    1. Для каждого произведения вычисляются основные заданные раннее характеристики. 
    2. Добавляются метададные, чтобы результаты можно было сопоставлять. 

    На выходе выдается список словарей. Один словарь на произведение.
    """

    if not isinstance(texts, list):
        raise TypeError('Необходимо добавить список объектов Text!')

    for text in texts:
        if not isinstance(text, Text):
            raise TypeError('Внимание! Все элементы списка должны быть объектами Text!')



    comparison_results = []

    # Каждое произведение анализируется по отдельности: 
    for text in texts:
        metrics = calculate_text_metrics(text.content)

        result = {
            'Название произведения': text.title or 'Название произведение неизвестно',
            'Автор': text.author or 'Автор неизвестен',
            'Язык написания': text.language_code, 
            'Литературная форма': text.literary_form or 'Литературная форма не указана', 
            'Жанр': text.genre or 'Жанр не указан', 
            'Год создания': text.year_created,
            'Год публикации': text.year_published,
            'Источник текста': text.source_type, 
            **metrics   # Распаковка вычисленных метрик текста в итоговый словарь
        }

        comparison_results.append(result)

    return comparison_results
        