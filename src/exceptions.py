class DataNotFoundError(Exception):
    """
    Исключение, если запрос к представлению не возвращает ни одной строки данных.
    """
    pass