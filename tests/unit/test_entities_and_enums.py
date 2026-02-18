import pytest

from app.adapters.enums.upload import VideoUpload
from app.entities.video import VideoEntities


def test_video_upload_enum_has_expected_member():
    assert issubclass(VideoUpload, str)
    assert list(VideoUpload) == []


def test_video_entities_is_abstract():
    with pytest.raises(TypeError):
        VideoEntities()


def test_video_entities_concrete_implementation():
    class ConcreteVideoEntity(VideoEntities):
        def create_video(self, video):
            return video

    entity = ConcreteVideoEntity()
    assert entity.create_video("payload") == "payload"
