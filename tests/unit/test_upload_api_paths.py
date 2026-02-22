from unittest.mock import Mock

import pytest
from fastapi import HTTPException

import app.api.upload as upload_module
from app.gateways.sqs_producer import SQSProducer
from app.gateways.video_processing_gateway import VideoProcessingGateway
from app.infrastructure.security.auth import AuthenticatedUser


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_get_processing_gateway_returns_gateway_instance():
    gateway = upload_module.get_processing_gateway()

    assert isinstance(gateway, VideoProcessingGateway)


def test_get_sqs_producer_returns_instance():
    producer = upload_module.get_sqs_producer()

    assert isinstance(producer, SQSProducer)


@pytest.mark.anyio
async def test_list_user_videos_raises_http_500_on_unexpected_error(monkeypatch):
    class BrokenController:
        def __init__(self, _video_dao):
            pass

        def list_user_videos(self, _user_id):
            raise Exception("boom")

    monkeypatch.setattr(upload_module, "ListVideosController", BrokenController)

    with pytest.raises(HTTPException) as exc_info:
        await upload_module.list_user_videos(
            user_id=1,
            db=Mock(),
            current_user=AuthenticatedUser(sub="1", claims={"user_id": "1"}),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "boom"


@pytest.mark.anyio
async def test_list_user_videos_success(monkeypatch):
    class OkController:
        def __init__(self, _video_dao):
            pass

        def list_user_videos(self, _user_id):
            return {"status": "success", "data": []}

    monkeypatch.setattr(upload_module, "ListVideosController", OkController)

    result = await upload_module.list_user_videos(
        user_id=1,
        db=Mock(),
        current_user=AuthenticatedUser(sub="1", claims={"user_id": "1"}),
    )

    assert result == {"status": "success", "data": []}


@pytest.mark.anyio
async def test_upload_and_process_video_enforces_user_and_validates_file(monkeypatch):
    class FakeController:
        def __init__(self, _use_case):
            pass

        def upload_video(self, user_id, title, upload_file):
            return {
                "status": "success",
                "data": {
                    "id": 1,
                    "user_id": user_id,
                    "title": title,
                    "file_path": f"/uploads/{upload_file.filename}",
                    "status": 0,
                },
            }

    monkeypatch.setattr(upload_module, "UploadController", FakeController)

    fake_file = Mock()
    fake_file.filename = "video.mp4"
    fake_file.content_type = "video/mp4"

    response = await upload_module.upload_and_process_video(
        user_id=10,
        title="Teste",
        file=fake_file,
        db=Mock(),
        processing_gateway=Mock(),
        sqs_producer=Mock(),
        current_user=AuthenticatedUser(sub="10", claims={"user_id": "10"}),
    )

    assert response["status"] == "success"
    assert response["data"]["user_id"] == 10

