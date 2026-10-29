import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.comparison import compare_texts
from src.processing import calculate_text_metrics, get_word_frequencies
from src.text_model import ManualText, UploadedText



st.set_page_config(
    page_title='Анализ литературных текстов',
    layout='wide',
)


# Единая палитра: используется для различения авторов на графиках.
CHART_COLORS = [
    '#98684f',
    '#c58d70',
    '#d5b98c',
    '#7f8b70',
    '#b47d83',
    '#6f8c8a',
]


def load_css() -> None:
    """Загружает оформление приложения из файла style.css."""
    css_path = Path(__file__).parent / 'style.css'

    if css_path.exists():
        css = css_path.read_text(encoding='utf-8')
        st.markdown(
            f'<style>{css}</style>',
            unsafe_allow_html=True,
        )


def style_figure(figure, title: str | None = None) -> None:
    """
    Применяет единый стиль ко всем графикам.

    Использует прозрачный фон, общий шрифт и минималистичные оси
    без сеток, нулевых линий и лишних рамок.
    """
    figure.update_layout(
        template='plotly_white',
        font={
            'family': 'Aptos, Segoe UI, Arial, sans-serif',
            'size': 13,
            'color': '#40352f',
        },
        title={
            'text': title or '',
            'x': 0,
            'xanchor': 'left',
            'font': {
                'size': 18,
                'color': '#40352f',
            },
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin={
            'l': 15,
            'r': 15,
            't': 65,
            'b': 55,
        },
        legend={
            'title_text': '',
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
        },
        hoverlabel={
            'bgcolor': '#fffdf9',
            'font': {
                'family': 'Aptos, Segoe UI, Arial, sans-serif',
                'size': 13,
                'color': '#40352f',
            },
            'bordercolor': '#e6dbcf',
        },
    )

    # Убираем сетки и линии осей, сохраняя подписи значений.
    figure.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks='',
        automargin=True,
    )

    figure.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks='',
        automargin=True,
    )

    # Убираем контуры столбцов и слегка смягчаем их внешний вид.
    figure.update_traces(
        marker_line_width=0,
        opacity=0.92,
    )




def parse_year(value: str, field_name: str) -> int | None:
    """Проверяет год и преобразует его в целое число."""
    value = value.strip()

    if not value:
        return None

    try:
        year = int(value)
    except ValueError as error:
        raise ValueError(
            f'Поле «{field_name}»: укажите год целым числом.'
        ) from error

    if not 1 <= year <= 3000:
        raise ValueError(
            f'Поле «{field_name}»: год должен быть от 1 до 3000.'
        )

    return year


def clear_analysis() -> None:
    """Сбрасывает результаты анализа после изменения коллекции."""
    st.session_state.analysis_results = None
    st.session_state.analysis_error = None


def add_text(text: ManualText | UploadedText) -> bool:
    """
    Добавляет произведение в коллекцию.

    Возвращает False, если произведение с тем же содержимым
    и источником уже существует.
    """
    for existing in st.session_state.texts:
        if (
            existing.content == text.content
            and existing.source_type == text.source_type
            and existing.source_name == text.source_name
        ):
            return False

    st.session_state.texts.append(text)
    clear_analysis()
    return True


def make_text(
    content: str,
    title: str,
    author: str,
    language_code: str,
    language_name: str,
    literary_form: str,
    genre: str,
    year_created: str,
    year_published: str,
    source_name: str | None = None,
) -> ManualText | UploadedText:
    """
    Создаёт объект произведения с индивидуальными метаданными.

    В зависимости от источника возвращает объект ручного ввода
    или объект загруженного файла.
    """
    if not content.strip():
        raise ValueError('Текст не должен быть пустым.')

    year_created_value = parse_year(year_created, 'Год создания')
    year_published_value = parse_year(
        year_published,
        'Год публикации',
    )

    # Для неизвестного языка сохраняем его код или введённое название.
    if language_code == 'other':
        resolved_language = language_name.strip() or 'other'
    else:
        resolved_language = language_code

    metadata = {
        'language_name': language_name.strip() or None,
    }

    common_fields = {
        'content': content,
        'title': title.strip() or None,
        'author': author.strip() or None,
        'language_code': resolved_language,
        'literary_form': (
            None if literary_form == 'Не указана' else literary_form
        ),
        'genre': genre.strip() or None,
        'year_created': year_created_value,
        'year_published': year_published_value,
        'metadata': metadata,
    }

    if source_name is not None:
        return UploadedText(
            **common_fields,
            source_name=source_name,
        )

    return ManualText(**common_fields)


def show_metadata_form(
    key_prefix: str,
    default_title: str,
    content: str,
    source_name: str | None = None,
) -> None:
    """
    Показывает отдельную форму метаданных для произведения.

    Каждая форма имеет уникальный ключ, поэтому данные разных
    загруженных файлов не смешиваются.
    """
    with st.form(f'{key_prefix}_metadata_form'):
        title = st.text_input(
            'Название произведения',
            value=default_title,
            key=f'{key_prefix}_title',
        )

        author = st.text_input(
            'Автор',
            key=f'{key_prefix}_author',
        )

        language_code = st.selectbox(
            'Язык',
            options=['und', 'ru', 'en', 'fr', 'de', 'other'],
            format_func=lambda value: {
                'und': 'Не указан',
                'ru': 'Русский',
                'en': 'Английский',
                'fr': 'Французский',
                'de': 'Немецкий',
                'other': 'Другой',
            }[value],
            key=f'{key_prefix}_language',
        )

        language_name = st.text_input(
            'Название языка, если выбран «Другой»',
            key=f'{key_prefix}_language_name',
        )

        literary_form = st.selectbox(
            'Литературная форма',
            options=[
                'Не указана',
                'Проза',
                'Поэзия',
                'Драматургия',
                'Другое',
            ],
            key=f'{key_prefix}_form',
        )

        genre = st.text_input(
            'Жанр',
            key=f'{key_prefix}_genre',
        )

        col1, col2 = st.columns(2)

        with col1:
            year_created = st.text_input(
                'Год создания',
                placeholder='Например, 1890',
                key=f'{key_prefix}_year_created',
            )

        with col2:
            year_published = st.text_input(
                'Год публикации',
                placeholder='Например, 1892',
                key=f'{key_prefix}_year_published',
            )

        submitted = st.form_submit_button(
            'Добавить в коллекцию',
            type='primary',
            use_container_width=True,
        )

    # Создаём объект только после отправки формы.
    if submitted:
        try:
            text = make_text(
                content=content,
                title=title,
                author=author,
                language_code=language_code,
                language_name=language_name,
                literary_form=literary_form,
                genre=genre,
                year_created=year_created,
                year_published=year_published,
                source_name=source_name,
            )

            if add_text(text):
                st.success(
                    f'«{text.title or "Без названия"}» '
                    'добавлено в коллекцию.'
                )
            else:
                st.warning('Это произведение уже есть в коллекции.')

        except (TypeError, ValueError) as error:
            st.error(str(error))


def run_analysis() -> None:
    """
    Выполняет анализ всех произведений коллекции.

    Метрики каждого текста и результаты сравнения сохраняются
    в session_state, чтобы оставаться доступными после перерисовки.
    """
    texts = st.session_state.texts

    if not texts:
        st.warning(
            'Коллекция пуста. Сначала добавьте хотя бы одно произведение.'
        )
        return

    try:
        # Сравнительные показатели формируются отдельной функцией.
        comparison_df = pd.DataFrame(compare_texts(texts))

        # Рассчитываем количественные метрики каждого произведения.
        metrics_rows = []

        for text in texts:
            row = calculate_text_metrics(text.content)

            # Добавляем метаданные для фильтрации и интерпретации.
            row['Название произведения'] = (
                text.title or 'Без названия'
            )
            row['Автор'] = text.author or 'Не указан'
            row['Язык'] = text.language_code
            row['Литературная форма'] = (
                text.literary_form or 'Не указана'
            )
            row['Жанр'] = text.genre or 'Не указан'
            row['Год создания'] = text.year_created
            row['Год публикации'] = text.year_published

            metrics_rows.append(row)

        metrics_df = pd.DataFrame(metrics_rows)

        # Сохраняем таблицы для последующего отображения.
        st.session_state.analysis_results = {
            'comparison': comparison_df,
            'metrics': metrics_df,
        }
        st.session_state.analysis_error = None

    except Exception as error:
        # Показываем ошибку в интерфейсе вместо потери информации.
        st.session_state.analysis_results = None
        st.session_state.analysis_error = (
            f'Ошибка анализа: {type(error).__name__}: {error}'
        )




load_css()

# Создаём состояние сессии только при первом обращении.
if 'texts' not in st.session_state:
    st.session_state.texts = []

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

if 'analysis_error' not in st.session_state:
    st.session_state.analysis_error = None




st.title('Анализ литературных текстов')

st.write(
    'Приложение для количественного исследования литературных '
    'произведений, сравнения лексических характеристик и изучения '
    'особенностей авторского стиля.'
)

texts = st.session_state.texts

# Считаем уникальных авторов и общий объём коллекции.
authors = {
    text.author.strip()
    for text in texts
    if text.author and text.author.strip()
}
total_characters = sum(len(text.content) for text in texts)

col1, col2, col3 = st.columns(3)

col1.metric('Произведения', len(texts))
col2.metric('Авторы', len(authors))
col3.metric(
    'Количество символов',
    f'{total_characters:,}'.replace(',', ' '),
)

st.divider()



st.header('Добавление произведений')

upload_tab, manual_tab = st.tabs(
    ['Загрузка файлов', 'Ручной ввод']
)


# Загрузка TXT-файлов с отдельной формой для каждого произведения.
with upload_tab:
    st.write(
        'Загрузите TXT-файлы. У каждого файла будет собственная форма '
        'метаданных. Добавляйте произведения по одному.'
    )

    uploaded_files = st.file_uploader(
        'Выберите текстовые файлы',
        type=['txt'],
        accept_multiple_files=True,
        key='text_file_uploader',
    )

    if uploaded_files:
        st.caption(
            f'Выбрано файлов: {len(uploaded_files)}. '
            'Для каждого файла заполните отдельную форму.'
        )

        for index, uploaded_file in enumerate(uploaded_files):
            file_key = f'file_{index}_{uploaded_file.name}'

            with st.expander(
                f'Файл: {uploaded_file.name}',
                expanded=(index == 0),
            ):
                # Читаем файл как UTF-8, удаляя возможный BOM.
                try:
                    content = uploaded_file.getvalue().decode('utf-8-sig')
                except UnicodeDecodeError:
                    st.error(
                        'Не удалось прочитать файл в кодировке UTF-8. '
                        'Пересохраните файл в UTF-8 и загрузите снова.'
                    )
                    continue

                if not content.strip():
                    st.warning('Файл пуст.')
                    continue

                st.caption(
                    f'Размер текста: {len(content):,} символов. '
                    'Исходный текст будет сохранен без изменений.'
                )

                # Предпросмотр не изменяет содержимое загруженного файла.
                with st.popover('Просмотреть текст'):
                    st.text_area(
                        'Содержимое файла',
                        value=content,
                        height=220,
                        disabled=True,
                        key=f'{file_key}_preview',
                    )

                show_metadata_form(
                    key_prefix=file_key,
                    default_title=Path(uploaded_file.name).stem,
                    content=content,
                    source_name=uploaded_file.name,
                )
    else:
        st.info('Выберите TXT-файлы, чтобы начать загрузку.')


# Ручной ввод текста с теми же основными метаданными.
with manual_tab:
    st.write('Вставьте текст и заполните метаданные произведения.')

    with st.form('manual_text_form'):
        manual_title = st.text_input('Название произведения')
        manual_author = st.text_input('Автор')

        manual_language = st.selectbox(
            'Язык',
            options=['und', 'ru', 'en', 'fr', 'de', 'other'],
            format_func=lambda value: {
                'und': 'Не указан',
                'ru': 'Русский',
                'en': 'Английский',
                'fr': 'Французский',
                'de': 'Немецкий',
                'other': 'Другой',
            }[value],
        )

        manual_language_name = st.text_input(
            'Название языка, если выбран «Другой»'
        )

        manual_form_type = st.selectbox(
            'Литературная форма',
            options=[
                'Не указана',
                'Проза',
                'Поэзия',
                'Драматургия',
                'Другое',
            ],
        )

        manual_genre = st.text_input('Жанр')
        manual_year_created = st.text_input('Год создания')
        manual_year_published = st.text_input('Год публикации')

        manual_content = st.text_area(
            'Текст произведения',
            height=260,
            placeholder='Вставьте текст сюда...',
        )

        manual_submitted = st.form_submit_button(
            'Добавить произведение',
            type='primary',
            use_container_width=True,
        )

    # Проверяем данные и создаём объект после отправки формы.
    if manual_submitted:
        try:
            text = make_text(
                content=manual_content,
                title=manual_title,
                author=manual_author,
                language_code=manual_language,
                language_name=manual_language_name,
                literary_form=manual_form_type,
                genre=manual_genre,
                year_created=manual_year_created,
                year_published=manual_year_published,
            )

            if add_text(text):
                st.success('Произведение добавлено в коллекцию.')
            else:
                st.warning('Это произведение уже есть в коллекции.')

        except (TypeError, ValueError) as error:
            st.error(str(error))


st.divider()



st.header('Коллекция произведений')

texts = st.session_state.texts

if not texts:
    st.info(
        'Коллекция пуста. Добавьте произведение через одну из вкладок.'
    )
else:
    for index, text in enumerate(texts):
        title = text.title or f'Произведение {index + 1}'
        author = text.author or 'Автор не указан'

        with st.expander(f'{title} — {author}'):
            st.write(f'**Язык:** {text.language_code}')
            st.write(
                f'**Литературная форма:** '
                f'{text.literary_form or "Не указана"}'
            )
            st.write(f'**Жанр:** {text.genre or "Не указан"}')
            st.write(
                f'**Год создания:** {text.year_created or "Не указан"}'
            )
            st.write(
                f'**Год публикации:** '
                f'{text.year_published or "Не указан"}'
            )
            st.write(
                f'**Источник:** {text.source_name or "Ручной ввод"}'
            )
            st.write(
                f'**Символов:** {len(text.content):,}'.replace(',', ' ')
            )

            # Удаляем выбранный объект и сбрасываем устаревший анализ.
            if st.button(
                'Удалить произведение',
                key=f'delete_{index}',
            ):
                st.session_state.texts.pop(index)
                clear_analysis()
                st.rerun()

    # Полная очистка коллекции.
    if st.button('Очистить коллекцию'):
        st.session_state.texts = []
        clear_analysis()
        st.rerun()


st.divider()



st.header('Анализ и сравнение')

st.write(
    'Анализ выполняется для произведений, уже добавленных в коллекцию. '
    'Повторно искать файлы на диске не требуется.'
)

if st.button(
    'Выполнить анализ',
    type='primary',
    use_container_width=True,
    key='run_analysis',
):
    run_analysis()


# Отображаем сообщение об ошибке, если анализ завершился неудачно.
if st.session_state.analysis_error:
    st.error(st.session_state.analysis_error)


results = st.session_state.analysis_results

if results is not None:
    comparison_df = results['comparison']
    metrics_df = results['metrics']

    # Таблица сравнительных характеристик.
    st.subheader('Таблица сравнения')

    if comparison_df.empty:
        st.info(
            'Таблица сравнения пуста. Проверьте функцию '
            'compare_texts() в src/comparison.py.'
        )
    else:
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
        )

        # Экспортируем таблицу в CSV с поддержкой кириллицы.
        st.download_button(
            'Скачать сравнение в CSV',
            data=comparison_df.to_csv(
                index=False
            ).encode('utf-8-sig'),
            file_name='comparison_results.csv',
            mime='text/csv',
        )

    # Таблица всех количественных метрик и метаданных.
    st.subheader('Метрики произведений')

    st.dataframe(
        metrics_df,
        use_container_width=True,
        hide_index=True,
    )

    # График 1: сравнение объёма произведений.
    if 'Количество слов' in metrics_df.columns:
        figure = px.bar(
            metrics_df,
            x='Название произведения',
            y='Количество слов',
            color='Автор',
            color_discrete_sequence=CHART_COLORS,
            labels={
                'Название произведения': 'Произведение',
                'Количество слов': 'Количество слов',
                'Автор': 'Автор',
            },
        )

        style_figure(
            figure,
            'Количество слов в произведениях',
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={'displayModeBar': False},
        )

    # График 2: сравнение средней длины слова.
    if 'Средняя длина слова' in metrics_df.columns:
        figure = px.bar(
            metrics_df,
            x='Название произведения',
            y='Средняя длина слова',
            color='Автор',
            color_discrete_sequence=CHART_COLORS,
            labels={
                'Название произведения': 'Произведение',
                'Средняя длина слова': 'Средняя длина слова',
                'Автор': 'Автор',
            },
        )

        style_figure(
            figure,
            'Средняя длина слова',
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={'displayModeBar': False},
        )



    st.subheader('Частотный анализ')

    current_texts = st.session_state.texts

    # Пользователь выбирает произведение для анализа лексики.
    selected_index = st.selectbox(
        'Произведение для частотного анализа',
        options=list(range(len(current_texts))),
        format_func=lambda index: (
            f'{current_texts[index].title or "Без названия"} — '
            f'{current_texts[index].author or "Автор не указан"}'
        ),
    )

    # Определяем размер списка наиболее частотных слов.
    top_n = st.slider(
        'Количество слов в таблице',
        min_value=5,
        max_value=30,
        value=10,
    )

    selected_text = current_texts[selected_index]

    # Передаём язык произведения, чтобы применялся правильный
    # набор стоп-слов. Исходное содержимое при этом не меняется.
    frequencies = get_word_frequencies(
        selected_text.content,
        top_n=top_n,
        remove_stop_words=True,
        language_code=selected_text.language_code,
    )

    if frequencies:
        frequency_df = pd.DataFrame(
            frequencies,
            columns=['Слово', 'Частота'],
        )

        st.dataframe(
            frequency_df,
            use_container_width=True,
            hide_index=True,
        )

        # График 3: частотность слов после фильтрации стоп-слов.
        figure = px.bar(
            frequency_df,
            x='Слово',
            y='Частота',
            color_discrete_sequence=[CHART_COLORS[0]],
            labels={
                'Слово': 'Слово',
                'Частота': 'Количество употреблений',
            },
        )

        style_figure(
            figure,
            'Наиболее частотные слова',
        )

        # Для одной серии легенда не нужна; поворачиваем подписи,
        # чтобы длинные слова не накладывались друг на друга.
        figure.update_layout(showlegend=False)
        figure.update_xaxes(tickangle=-30)

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={'displayModeBar': False},
        )
    else:
        st.info('В тексте нет слов для частотного анализа.')



st.divider()

st.caption(
    'Количественные характеристики описывают текст, но не доказывают '
    'авторство или литературное влияние. При сравнении следует учитывать '
    'объём произведения, язык, жанр и литературную форму.'
)
