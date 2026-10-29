class Text:
    """
    На данном этапе представляется литературный текст с его библиографическими метаданными.
    """

    def __init__(
        self,
        content: str,  # Содержимое произведения
        text_id: str | None = None,  # Идентификатор
        title: str | None = None,  # Название произведения
        author: str | None = None,  # Автор произведения
        language_code: str = "und",  # Язык произведения ('und' — язык неизвестен)
        literary_form: str | None = None,  # Форма произведения
        genre: str | None = None,  # Жанр произведения
        year_created: int | None = None,  # Год создания
        year_published: int | None = None,  # Год публикации
        source_type: str = "user_input",  # Тип источника
        source_name: str | None = None,  # Название источника
        metadata: dict | None = None,  # Дополнительные метаданные
    ) -> None:
        """
        Создает объект текста и проверяет его содержимое.
        """

        if not isinstance(content, str):
            raise TypeError(
                "Содержимое текста должно быть строкой. Добавьте строку."
            )

        if not content.strip():
            raise ValueError(
                "Не добавлено содержание. Текст не должен быть пустым."
            )

        self.content = content
        self.text_id = text_id

        self.title = title
        self.author = author
        self.language_code = language_code
        self.literary_form = literary_form
        self.genre = genre

        # Год создания и год публикации отдельно
        self.year_created = year_created
        self.year_published = year_published

        # На данном этапе источник — ручной ввод или загрузка файла.
        # В дальнейшем здесь можно будет учитывать и другие источники.
        self.source_type = source_type
        self.source_name = source_name

        # Копируем словарь, чтобы случайно не изменить исходные метаданные.
        self.metadata = metadata.copy() if metadata is not None else {}

    @property
    def character_count(self) -> int:
        """
        Функция возвращает количество символов в анализируемом произведении.
        """
        return len(self.content)

    def __len__(self) -> int:
        """
        Функция позволяет узнать длину произведения в символах.
        """
        return self.character_count

    def __str__(self) -> str:
        """
        Функция возвращает название произведения или его идентификатор.
        """
        return self.title or self.text_id or "Нет названия"


class UploadedText(Text):
    """
    Класс представляет произведение, загруженное из текстового файла пользователем.
    """

    def __init__(
        self,
        content: str,
        text_id: str | None = None,
        title: str | None = None,
        author: str | None = None,
        language_code: str = "und",
        literary_form: str | None = None,
        genre: str | None = None,
        year_created: int | None = None,
        year_published: int | None = None,
        source_type: str = "user_input",
        source_name: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """
        Создается текст. При создании сохраняется название исходного файла.
        """

        super().__init__(  # Обращение к родительскому классу
            content=content,
            text_id=text_id,
            title=title,
            author=author,
            language_code=language_code,
            literary_form=literary_form,
            genre=genre,
            year_created=year_created,
            year_published=year_published,
            source_type="file_upload",  # Источник определяется типом класса
            source_name=source_name,
            metadata=metadata,
        )


class ManualText(Text):
    """
    Класс представляет произведение, введенное пользователем вручную.
    """

    def __init__(
        self,
        content: str,
        text_id: str | None = None,
        title: str | None = None,
        author: str | None = None,
        language_code: str = "und",
        literary_form: str | None = None,
        genre: str | None = None,
        year_created: int | None = None,
        year_published: int | None = None,
        source_type: str = "user_input",
        source_name: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """
        Создается текст, введенный вручную.
        """

        super().__init__(  # Обращение к родительскому классу
            content=content,
            text_id=text_id,
            title=title,
            author=author,
            language_code=language_code,
            literary_form=literary_form,
            genre=genre,
            year_created=year_created,
            year_published=year_published,
            source_type="user_input",  # Источник определяется типом класса
            source_name=source_name,
            metadata=metadata,
        )
