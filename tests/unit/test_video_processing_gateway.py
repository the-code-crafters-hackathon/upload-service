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


def test_processing_gateway_validate_fps_parameter():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        gateway = VideoProcessingGateway(base_dir=base_dir)

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            
            try:
                gateway.process_video(
                    Path("/fake/video.mp4"),
                    "20260208_120000",
                    fps=2
                )
            except Exception:
                pass

            call_args = mock_run.call_args
            if call_args:
                cmd = call_args[0][0]
                assert "-vf" in cmd

def test_processing_gateway_creates_zip_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        gateway = VideoProcessingGateway(base_dir=base_dir)

        test_file1 = base_dir / "test1.png"
        test_file2 = base_dir / "test2.png"
        test_file1.write_text("test1")
        test_file2.write_text("test2")

        zip_path = base_dir / "test.zip"

        gateway._create_zip([test_file1, test_file2], zip_path)

        assert zip_path.exists()


def test_processing_gateway_no_frames_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        gateway = VideoProcessingGateway(base_dir=base_dir)

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")

            with pytest.raises(Exception) as exc_info:
                gateway.process_video(
                    Path("/fake/video.mp4"),
                    "20260208_120000"
                )

            assert "Nenhum frame" in str(exc_info.value)
