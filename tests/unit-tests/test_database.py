import pytest
from datetime import datetime
from app.database import video_server
from tests.common_fixtures import preload_database


def test_set_video_server(preload_database):
    server_path = '/dev/archive/test_server'

    set_video_server = video_server.set_or_get_new_server(server_dir=server_path)

    assert isinstance(set_video_server, video_server.VideoServer)


@pytest.mark.parametrize('invalid_server', [None, 'long' * 65])
def test_set_invalid_video_server(preload_database, invalid_server):
    with pytest.raises(ValueError):
        video_server.set_or_get_new_server(invalid_server)


def test_set_cam(preload_database):
    cam_path = 'cam1'
    set_video_server = video_server.set_or_get_new_server('/dev/archive/test_server')

    set_cam = video_server.set_or_get_new_camera(camera_dir=cam_path, server=set_video_server)

    assert isinstance(set_cam, video_server.Camera)


def test_set_video_path(preload_database):
    set_video_server = video_server.set_or_get_new_server('/dev/archive/test_server')
    set_cam = video_server.set_or_get_new_camera(camera_dir='cam1', server=set_video_server)
    video_path = "03-06-2020/62241721"
    time_stamp = datetime.strptime('03-06-2020', "%d-%m-%Y")

    set_video_path = video_server.set_or_get_new_video_path(camera=set_cam,
                                                            video_path=video_path,
                                                            datestamp=time_stamp)

    assert isinstance(set_video_path, video_server.VideoPath)


def test_set_video(preload_database):
    set_video_server = video_server.set_or_get_new_server('/dev/archive/test_server')
    set_cam = video_server.set_or_get_new_camera(camera_dir='cam1', server=set_video_server)
    set_video_path = video_server.set_or_get_new_video_path(camera=set_cam,
                                                            video_path="03-06-2020/62241721",
                                                            datestamp=datetime.strptime('03-06-2020', "%d-%m-%Y"))

    video_data = {
        'name': "test_video",
        'video_path_id': set_video_path.id,
        'time': datetime.now().strftime('%H:%M:%S'),
        'extension': 'mp4',
        'duration': 10 * 60 * 60,
        'bitrate': 8340,
        'codec': 'h264',
    }

    set_video = video_server.set_or_get_new_video(**video_data)

    assert isinstance(set_video, video_server.Video)


def test_set_incomplete_video(preload_database):
    video_data = {
        'name': "test_video_a",
        'time': datetime.now().strftime('%H:%M:%S'),
        'stream_count': 2,
        'codec_main': 'h264',
    }
    with pytest.raises(KeyError):
        video_server.set_or_get_new_video(**video_data)


def test_get_video_server(preload_database):
    server_path = '/dev/archive/test_server'
    set_video_server = video_server.set_or_get_new_server(server_dir=server_path)

    get_video_server = video_server.get_server(server_dir=server_path)

    assert set_video_server == get_video_server


def test_get_camera(preload_database):
    server = video_server.set_or_get_new_server(server_dir='/dev/archive/test_server')
    camera_dir = 'cam99'
    set_camera = video_server.set_or_get_new_camera(server=server, camera_dir=camera_dir)

    get_camera = video_server.get_camera(camera_dir=camera_dir)

    assert set_camera == get_camera


def test_video_pool_by_date(preload_database):
    set_video_server = video_server.set_or_get_new_server('/dev/archive/test_server')
    set_cam = video_server.set_or_get_new_camera(camera_dir='cam1', server=set_video_server)
    set_video_path = video_server.set_or_get_new_video_path(camera=set_cam,
                                                            video_path="03-06-2020/62241721",
                                                            datestamp=datetime.strptime('03-06-2020', "%d-%m-%Y"))
    time_start = datetime.strptime('03-06-2020 10:20:30', '%d-%m-%Y %H:%M:%S')
    time_end = datetime.strptime('03-06-2020 10:20:40', '%d-%m-%Y %H:%M:%S')
    default_video_payload = {
        'name': "test_video",
        'video_path_id': set_video_path.id,
        'time': time_start,
        'extension': 'mp4',
        'duration': 10 * 60 * 60,
        'bitrate': 8340,
        'codec': 'h264',
    }
    set_video_start = video_server.set_or_get_new_video(**default_video_payload)
    default_video_payload['time'] = time_end
    set_video_end = video_server.set_or_get_new_video(**default_video_payload)

    get_video_pool = video_server.get_video_pool_by_datetime(time_start=time_start, time_end=time_end)

    assert get_video_pool == [{
        'video_path': set_video_path,
        'videos': [set_video_start, set_video_end]
    }]


def test_video_pool_by_incorrect_date(preload_database):
    empty_video_list = video_server.get_video_pool_by_datetime(time_start=datetime.now(), time_end=datetime.now())
    assert not empty_video_list
