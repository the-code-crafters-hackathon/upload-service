import sys, os
from pathlib import Path
import pytest
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@pytest.fixture
def mock_db_session():
    return Mock()


@pytest.fixture
def mock_gateway():
    gateway = Mock()
    gateway.save_upload.return_value = Path("/fake/uploads/video_20260208.mp4")
    gateway.process_video.return_value = (
        Path("/fake/outputs/frames_20260208.zip"),
        24,
        ["frame_0001.png", "frame_0002.png"]
    )
    
    return gateway


@pytest.fixture
def mock_video_dao():
    dao = Mock()
    dao.create_video.return_value = Mock(
        id=1, user_id=1, title="Test", file_path="/path", status=0
    )
    dao.list_videos_by_user.return_value = []

    return dao
