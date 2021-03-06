from os import PathLike

from app.database import video_server
from app.filesystem import path
from app.video import parser


def set_full_path(video_path: PathLike) -> None:
    """
    Отправить все данные пути в базу данных
    Args:
        video_path (PathLike): Путь до видео
    Raises:
        ValueError: Ошибка возникает, если переданный путь оказался некорректным
    """
    try:
        parsed_path = path.split_path(video_path)

        set_server = video_server.set_or_get_new_server(server_dir=parsed_path.get('server'))
        set_camera = video_server.set_or_get_new_camera(camera_dir=parsed_path.get('camera'),
                                                        server=set_server)

        if video_server.get_video(video_path=parsed_path.get("video_path"), camera_id=set_camera.id) is None:
            video_server.set_or_get_new_video(**parser.get_video_data(video_path=video_path),
                                              camera_id=set_camera.id,
                                              video_path=parsed_path.get('video_path'),
                                              record_date=parsed_path.get('video_date'))
    except ValueError as err:
        raise err
