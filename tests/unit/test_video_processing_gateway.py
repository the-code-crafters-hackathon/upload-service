import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from fastapi import HTTPException

from app.gateways.video_processing_gateway import VideoProcessingGateway


def test_processing_gateway_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        
        gateway = VideoProcessingGateway(base_dir=base_dir)

        assert gateway.uploads_dir == base_dir / "uploads"
        assert gateway.outputs_dir == base_dir / "outputs"
        assert gateway.temp_dir == base_dir / "temp"


def test_processing_gateway_save_upload():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        gateway = VideoProcessingGateway(base_dir=base_dir)

        mock_file = Mock()
        mock_file.file = Mock()

        with patch('shutil.copyfileobj') as mock_copyfileobj:
            result = gateway.save_upload(mock_file, "20260208_120000")

        assert "20260208_120000" in str(result)
        assert result.exists() or result.parent == gateway.uploads_dir


def test_processing_gateway_creates_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        gateway = VideoProcessingGateway(base_dir=base_dir)

        assert gateway.uploads_dir.exists()
        assert gateway.outputs_dir.exists()
        assert gateway.temp_dir.exists()


def test_processing_gateway_production_requires_bucket(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = VideoProcessingGateway(base_dir=Path(tmpdir))
        mock_upload = Mock()
        mock_upload.filename = "video.mp4"
        mock_upload.file = Mock()

        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.delenv("AWS_S3_BUCKET", raising=False)

        with pytest.raises(HTTPException) as exc_info:
            gateway.save_upload(mock_upload, "20260218_220000")

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "S3 bucket not configured"
        mock_upload.file.close.assert_called_once()


def test_processing_gateway_production_upload_to_s3(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = VideoProcessingGateway(base_dir=Path(tmpdir))
        mock_upload = Mock()
        mock_upload.filename = "video.mp4"
        mock_upload.file = Mock()

        mock_s3 = Mock()

        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("AWS_S3_BUCKET", "bucket-test")

        with patch("app.gateways.video_processing_gateway.boto3.client", return_value=mock_s3):
            result = gateway.save_upload(mock_upload, "20260218_220001")

        assert result == "s3://bucket-test/uploads/20260218_220001_video.mp4"
        mock_upload.file.seek.assert_called_once_with(0)
        mock_s3.upload_fileobj.assert_called_once()
        mock_upload.file.close.assert_called_once()


def test_processing_gateway_production_upload_to_s3_handles_client_error(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = VideoProcessingGateway(base_dir=Path(tmpdir))
        mock_upload = Mock()
        mock_upload.filename = "video.mp4"
        mock_upload.file = Mock()

        mock_s3 = Mock()
        mock_s3.upload_fileobj.side_effect = Exception("upload failed")

        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("AWS_S3_BUCKET", "bucket-test")

        with patch("app.gateways.video_processing_gateway.boto3.client", return_value=mock_s3):
            with pytest.raises(HTTPException) as exc_info:
                gateway.save_upload(mock_upload, "20260218_220002")

        assert exc_info.value.status_code == 500
        assert "Erro ao enviar arquivo para S3" in exc_info.value.detail
        mock_upload.file.close.assert_called()
