import pytest
from types import SimpleNamespace
from unittest.mock import Mock

from app.controllers.list_videos_controller import ListVideosController


def test_list_videos_controller_list_user_videos():
    video1 = SimpleNamespace(
        id=1, user_id=1, title="Video 1", file_path="/path/video1.zip", status=1
    )
    video2 = SimpleNamespace(
        id=2, user_id=1, title="Video 2", file_path="/path/video2.zip", status=0
    )
    mock_video_dao = Mock()
    mock_video_dao.list_videos_by_user.return_value = [video1, video2]

    controller = ListVideosController(video_dao=mock_video_dao)

    response = controller.list_user_videos(user_id=1)

    assert response.status == "success"
    assert len(response.data) == 2
    assert response.data[0].id == 1
    assert response.data[0].user_id == 1
    assert response.data[0].title == "Video 1"
    assert response.data[0].status == 1
    assert response.data[1].id == 2


def test_list_videos_controller_empty_list():
    mock_video_dao = Mock()
    mock_video_dao.list_videos_by_user.return_value = []

    controller = ListVideosController(video_dao=mock_video_dao)

    response = controller.list_user_videos(user_id=999)

    assert response.status == "success"
    assert len(response.data) == 0


def test_list_videos_controller_calls_dao_with_correct_user_id():
    mock_video_dao = Mock()
    mock_video_dao.list_videos_by_user.return_value = []

    controller = ListVideosController(video_dao=mock_video_dao)

    controller.list_user_videos(user_id=42)

    mock_video_dao.list_videos_by_user.assert_called_once_with(42)


def test_list_videos_controller_maps_video_fields():
    video = SimpleNamespace(
        id=10,
        user_id=5,
        title="Test Video",
        file_path="/outputs/frames_20260208.zip",
        status=1
    )

    mock_video_dao = Mock()
    mock_video_dao.list_videos_by_user.return_value = [video]

    controller = ListVideosController(video_dao=mock_video_dao)

    response = controller.list_user_videos(user_id=5)

    response_video = response.data[0]
    assert response_video.id == 10
    assert response_video.user_id == 5
    assert response_video.title == "Test Video"
    assert response_video.file_path == "/outputs/frames_20260208.zip"
    assert response_video.status == 1
