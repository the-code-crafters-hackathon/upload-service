import pytest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock, MagicMock

from app.use_cases.upload_use_case import UploadUseCase


def test_upload_use_case_execute():
    mock_processing_gateway = Mock()
    mock_processing_gateway.save_upload.return_value = Path("/path/to/saved_video.mp4")

    mock_video_dao = Mock()
    mock_created_video = SimpleNamespace(
        id=1,
        user_id=1,
        title="Test Video",
        file_path="/path/to/saved_video.mp4",
        status=0
    )
    mock_video_dao.create_video.return_value = mock_created_video

    mock_upload_file = Mock()

    use_case = UploadUseCase(
        processing_gateway=mock_processing_gateway,
        video_dao=mock_video_dao
    )

    created, saved_path, timestamp = use_case.execute(
        user_id=1,
        title="Test Video",
        upload_file=mock_upload_file
    )

    assert created.id == 1
    assert created.user_id == 1
    assert created.status == 0
    assert saved_path == "/path/to/saved_video.mp4"
    assert timestamp is not None
    
    mock_processing_gateway.save_upload.assert_called_once()
    mock_video_dao.create_video.assert_called_once()


def test_upload_use_case_calls_dao_with_correct_dto():
    mock_processing_gateway = Mock()
    mock_processing_gateway.save_upload.return_value = Path("/path/to/video.mp4")

    mock_video_dao = Mock()
    mock_created_video = SimpleNamespace(
        id=1,
        user_id=1,
        title="Test Video",
        file_path="/path/to/video.mp4",
        status=0
    )
    mock_video_dao.create_video.return_value = mock_created_video

    mock_upload_file = Mock()

    use_case = UploadUseCase(
        processing_gateway=mock_processing_gateway,
        video_dao=mock_video_dao
    )

    use_case.execute(user_id=1, title="Test Video", upload_file=mock_upload_file)

    call_args = mock_video_dao.create_video.call_args
    dto = call_args[0][0]
    
    assert dto.user_id == 1
    assert dto.title == "Test Video"
    assert dto.status == 0
