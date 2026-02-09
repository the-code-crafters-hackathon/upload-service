import pytest
from types import SimpleNamespace
from sqlalchemy.exc import IntegrityError

from app.dao.video_dao import VideoDAO


def test_create_video_commits_and_refresh(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.added = None
            self.committed = False
            self.refreshed = None

        def add(self, obj):
            self.added = obj

        def commit(self):
            self.committed = True

        def refresh(self, obj):
            self.refreshed = obj

    fake_session = FakeSession()
    dao = VideoDAO(fake_session)

    video_dto = SimpleNamespace(
        user_id=1,
        title="Test Video",
        file_path="/path/to/video.mp4",
        status=0
    )
    
    result = dao.create_video(video_dto)

    assert fake_session.added is not None
    assert fake_session.committed is True
    assert result is not None


def test_create_video_rollback_on_integrity_error():
    class FakeSession:
        def add(self, obj):
            raise IntegrityError("Duplicate", "", "")

        def rollback(self):
            pass

    fake_session = FakeSession()
    dao = VideoDAO(fake_session)

    video_dto = SimpleNamespace(
        user_id=1,
        title="Test Video",
        file_path="/path/to/video.mp4",
        status=0
    )

    with pytest.raises(Exception) as exc_info:
        dao.create_video(video_dto)

    assert "Erro de integridade" in str(exc_info.value)


def test_update_video_status():
    class FakeVideo:
        def __init__(self):
            self.id = 1
            self.user_id = 1
            self.title = "Test"
            self.file_path = "/old/path.mp4"
            self.status = 0

    class FakeQuery:
        def filter(self, condition):
            return self

        def first(self):
            return FakeVideo()

    class FakeSession:
        def __init__(self):
            self.committed = False
            self.refreshed = None

        def query(self, model):
            return FakeQuery()

        def commit(self):
            self.committed = True

        def refresh(self, obj):
            self.refreshed = obj

    fake_session = FakeSession()
    dao = VideoDAO(fake_session)

    result = dao.update_video_status(1, status=1, file_path="/new/path.zip")

    assert fake_session.committed is True
    assert result.status == 1


def test_list_videos_by_user():
    class FakeVideo:
        def __init__(self, video_id):
            self.id = video_id
            self.user_id = 1
            self.title = f"Video {video_id}"
            self.file_path = f"/path/video{video_id}.zip"
            self.status = 1

    class FakeQuery:
        def filter(self, condition):
            return self

        def order_by(self, condition):
            return self

        def all(self):
            return [FakeVideo(1), FakeVideo(2), FakeVideo(3)]

    class FakeSession:
        def query(self, model):
            return FakeQuery()

    fake_session = FakeSession()
    dao = VideoDAO(fake_session)

    videos = dao.list_videos_by_user(1)

    assert len(videos) == 3
    assert all(v.user_id == 1 for v in videos)


def test_list_videos_empty():
    class FakeQuery:
        def filter(self, condition):
            return self

        def order_by(self, condition):
            return self

        def all(self):
            return []

    class FakeSession:
        def query(self, model):
            return FakeQuery()

    fake_session = FakeSession()
    dao = VideoDAO(fake_session)

    videos = dao.list_videos_by_user(999)

    assert len(videos) == 0
