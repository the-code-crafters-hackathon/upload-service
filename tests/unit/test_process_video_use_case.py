import pytest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock

from app.use_cases.process_video_use_case import ProcessVideoUseCase


def test_process_video_use_case_execute_success():
    mock_processing_gateway = Mock()
    mock_processing_gateway.process_video.return_value = (
        Path("/path/to/frames.zip"),
        24,
        ["frame_0001.png", "frame_0002.png"]  # images
    )
    mock_video_dao = Mock()
    mock_updated_video = SimpleNamespace(
        id=1,
        user_id=1,
        title="Test Video",
        file_path="/path/to/frames.zip",
        status=1
    )
    mock_video_dao.update_video_status.return_value = mock_updated_video

    use_case = ProcessVideoUseCase(
        processing_gateway=mock_processing_gateway,
        video_dao=mock_video_dao
    )

    use_case.execute(video_id=1, video_path="/path/video.mp4", timestamp="20260208_120000")

    mock_processing_gateway.process_video.assert_called_once_with(
        "/path/video.mp4", "20260208_120000"
    )
    
    mock_video_dao.update_video_status.assert_called_once_with(
        video_id=1,
        status=1,
        file_path="/path/to/frames.zip"
    )


def test_process_video_use_case_execute_error():
    mock_processing_gateway = Mock()
    mock_processing_gateway.process_video.side_effect = Exception("ffmpeg not found")

    mock_video_dao = Mock()

    use_case = ProcessVideoUseCase(
        processing_gateway=mock_processing_gateway,
        video_dao=mock_video_dao
    )
    use_case.execute(video_id=1, video_path="/path/video.mp4", timestamp="20260208_120000")

    mock_video_dao.update_video_status.assert_called_once_with(
        video_id=1,
        status=2
    )


def test_process_video_use_case_update_with_zip_path():
    mock_processing_gateway = Mock()
    zip_path = Path("/outputs/frames_20260208_120000.zip")
    mock_processing_gateway.process_video.return_value = (zip_path, 30, [])

    mock_video_dao = Mock()
    mock_video_dao.update_video_status.return_value = SimpleNamespace(
        id=1, user_id=1, title="Test", file_path=str(zip_path), status=1
    )

    use_case = ProcessVideoUseCase(
        processing_gateway=mock_processing_gateway,
        video_dao=mock_video_dao
    )
    use_case.execute(video_id=1, video_path="/uploads/video.mp4", timestamp="20260208_120000")
    args = mock_video_dao.update_video_status.call_args

    assert args[1]["file_path"] == str(zip_path)
