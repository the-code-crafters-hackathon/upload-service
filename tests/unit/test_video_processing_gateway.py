import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

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
