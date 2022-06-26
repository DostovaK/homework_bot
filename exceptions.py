class APIResponseError(Exception):
    """Исключение: запрос к эндпойнту сервиса не удался."""

    pass


class CheckResponseError(Exception):
    """Исключение: ответ API некорректный."""

    pass


class HomeWorkParseError(Exception):
    """Исключение: сообщение не отправилось."""

    pass


class ParseStatusError(Exception):
    """Исключение: неизвестный статус домашки."""

    pass


class MissingRequiredTokenError(Exception):
    """Исключение: отсутствует один из токенов."""

    pass


class APIIncorrectResponseError(Exception):
    """Исключение: ответ API некорректный."""

    pass


class HomeWorkTypeError(Exception):
    """Исключение: домашки приходят не в виде списка."""

    pass
