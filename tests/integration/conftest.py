import sys, os
from pathlib import Path
import pytest
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

_integration_db_path = Path(__file__).resolve().parents[1] / "temp" / "integration-tests.db"
_integration_db_path.parent.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_integration_db_path}")
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", os.environ["DATABASE_URL"])


@pytest.fixture(autouse=True)
def test_database_url(monkeypatch, tmp_path):
    db_file = tmp_path / "integration-tests.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URL", db_url)


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
