import sys, os
from pathlib import Path
import pytest
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def mock_upload_file():
    mock_file = Mock()
    mock_file.filename = "test_video.mp4"
    mock_file.file = Mock()

    return mock_file


@pytest.fixture
def mock_video_object():
    return Mock(
        id=1,
        user_id=1,
        title="Test Video",
        file_path="/path/to/video.mp4",
        status=0
    )
