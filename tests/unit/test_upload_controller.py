import pytest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock

from app.controllers.upload_controller import UploadController

def test_upload_controller_upload_video():
    mock_use_case = Mock()
    mock_created_video = SimpleNamespace(
        id=1,
        user_id=1,
        title="Test Video",
        file_path="/path/to/video.mp4",
        status=0
    )
    mock_use_case.execute.return_value = (
        mock_created_video,
        str(Path("/path/to/video.mp4")),
        "20260208_120000"
    )
    mock_upload_file = Mock()
    controller = UploadController(use_case=mock_use_case)

    response, background_info = controller.upload_video(
        user_id=1,
        title="Test Video",
        upload_file=mock_upload_file
    )

    assert response.status == "success"
    assert response.data.id == 1
    assert response.data.user_id == 1
    assert response.data.title == "Test Video"
    assert response.data.status == 0

    assert background_info[0] == 1
    assert background_info[2] == "20260208_120000"


def test_upload_controller_return_tuple():
    mock_use_case = Mock()
    mock_created_video = SimpleNamespace(
        id=5,
        user_id=2,
        title="Another Video",
        file_path="/path/to/another.mp4",
        status=0
    )
    mock_use_case.execute.return_value = (
        mock_created_video,
        "/path/to/another.mp4",
        "20260208_130000"
    )
    mock_upload_file = Mock()
    controller = UploadController(use_case=mock_use_case)

    response, background_info = controller.upload_video(
        user_id=2,
        title="Another Video",
        upload_file=mock_upload_file
    )
    
    assert isinstance(background_info, tuple)
    assert len(background_info) == 3
    assert background_info[0] == 5
    assert background_info[1] == "/path/to/another.mp4"
    assert background_info[2] == "20260208_130000"


def test_upload_controller_passes_user_id_to_use_case():
    mock_use_case = Mock()
    mock_created_video = SimpleNamespace(
        id=1, user_id=99, title="Test", file_path="/path", status=0
    )
    mock_use_case.execute.return_value = (mock_created_video, "/path", "20260208")

    mock_upload_file = Mock()
    controller = UploadController(use_case=mock_use_case)

    controller.upload_video(user_id=99, title="Test", upload_file=mock_upload_file)

    call_args = mock_use_case.execute.call_args
    assert call_args[0][0] == 99
