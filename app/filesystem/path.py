import pathlib
import re

from datetime import datetime
from typing import AnyStr
from os import PathLike


def split_path(path: [PathLike, AnyStr], regexp: str = None) -> dict:
    """
    Разделяет строку на директории для базы данныъх
    Args:
        path (PathLike, AnyStr): Путь для разделения
        regexp (str): Кастомное регулярное выражение для поиска путей

    Returns:
        dict: Возвращает словарь с ключами для базы данных

    Raises:
        ValueError: Вернет ошибку, если путь не соответсвует регулярному выражению
    """
    path = str(path).replace('\\', '/')  # Приведение к типу и нормальному формату пути
    regexp = r'(\/?.+)\/(\w+\-\d+)\/(\d{4}\-\d{2}\-\d{2})\/(.+\.mp4|avi)$' if regexp is None else regexp

    try:
        split_path_dict = re.findall(regexp, path)[0]
        return {
            'server': split_path_dict[0],
            'camera': split_path_dict[1],
            'video_date': split_path_dict[2],
            'video_path': split_path_dict[3]
        }

    except IndexError:
        raise ValueError(f"Путь {path} - не соотвествует регулярному выражению") from ValueError


def find_datestamp(path: [PathLike, AnyStr],
                   regexp: str = r'(\d{4}\-\d{2}\-\d{2})',
                   date_format: str = "%Y-%m-%d") -> [datetime, None]:
    """
    Ищет отметку даты записи видео в переданном пути
    Args:
        path (PathLike, AnyStr): Путь, который содержит дату
        regexp (str): Регулярное выражение, по которому необходимо искать дату
        date_format (str): Формат даты для datetime
    Returns:
        datetime: Объект datetime с найденной датой
        None: Если в переданном пути не было обнаружено даты
    """
    path = str(path)  # Если путь был передан через pathlib
    match_date = re.match(pattern=regexp, string=path)

    return datetime.strptime(path[match_date.start():match_date.end()], date_format) if match_date else match_date


def convert_to_pathlib(path: [PathLike, AnyStr], check_exist: bool = False) -> pathlib.Path:
    """
    Конвертация пути в pathlib.Path с проверкой существования файла
    Args:
        path (PathLike, AnyStr): Путь для конвертации
        check_exist (bool): Провести проверку на существование файла

    Returns:
        pathlib.Path: Pathlib путь до файла

    Raises:
        FileNotFoundError: Если файл не прошел проверку на существование
        TypeError: Если переданный путь невозможно конвертировать в pathlib.Path
    """
    try:
        converted_path = pathlib.Path(path)
        if not converted_path.exists() and check_exist:
            raise FileNotFoundError(f"Файла по пути {converted_path} не существует")

        return converted_path
    except TypeError as err:
        raise TypeError(f"Путь до файла {path} некорректен") from err
