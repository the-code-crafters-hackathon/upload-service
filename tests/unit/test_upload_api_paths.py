from unittest.mock import Mock

import pytest
from fastapi import HTTPException

import app.api.upload as upload_module
from app.gateways.sqs_producer import SQSProducer
from app.gateways.video_processing_gateway import VideoProcessingGateway


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
        await upload_module.list_user_videos(user_id=1, db=Mock())

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "boom"
