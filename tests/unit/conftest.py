import sys, os
from pathlib import Path
import pytest
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

_unit_db_path = Path(__file__).resolve().parents[1] / "temp" / "unit-tests.db"
_unit_db_path.parent.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_unit_db_path}")
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", os.environ["DATABASE_URL"])


@pytest.fixture(autouse=True)
def test_database_url(monkeypatch, tmp_path):
    db_file = tmp_path / "unit-tests.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URL", db_url)


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
