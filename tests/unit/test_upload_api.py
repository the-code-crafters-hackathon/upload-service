import io
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from app.api.upload import (
    DEFAULT_MAX_UPLOAD_SIZE_MB,
    get_max_upload_size_bytes,
    is_valid_video_content_type,
    is_valid_video_file,
    is_valid_video_size,
)


class TestVideoValidation:
    def test_upload_video_valid_formats(self):
        valid_formats = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"]

        for fmt in valid_formats:
            assert is_valid_video_file(f"video{fmt}") is True

    def test_upload_video_invalid_formats(self):
        invalid_formats = [".txt", ".pdf", ".doc", ".jpg", ".png"]

        for fmt in invalid_formats:
            assert is_valid_video_file(f"video{fmt}") is False

    def test_upload_video_case_insensitive(self):
        assert is_valid_video_file("VIDEO.MP4") is True
        assert is_valid_video_file("Video.MoV") is True
        assert is_valid_video_file("file.WMV") is True

    def test_invalid_extension_uppercase(self):
        assert is_valid_video_file("file.TXT") is False

    def test_multiple_dots_in_filename(self):
        assert is_valid_video_file("my.video.file.mp4") is True

    def test_no_extension(self):
        assert is_valid_video_file("videofile") is False


class TestVideoContentTypeValidation:
    def test_valid_content_types(self):
        valid_types = [
            "video/mp4",
            "video/x-msvideo",
            "video/quicktime",
            "video/x-matroska",
            "video/x-ms-wmv",
            "video/x-flv",
            "video/webm",
        ]

        for content_type in valid_types:
            assert is_valid_video_content_type(content_type) is True

    def test_content_type_with_parameters(self):
        assert is_valid_video_content_type("video/mp4; charset=binary") is True

    def test_invalid_content_types(self):
        invalid_types = ["text/plain", "application/json", "image/png", "application/octet-stream", None, ""]

        for content_type in invalid_types:
            assert is_valid_video_content_type(content_type) is False


class TestVideoSizeValidation:
    def test_get_max_upload_size_bytes_default(self, monkeypatch):
        monkeypatch.delenv("MAX_UPLOAD_SIZE_MB", raising=False)
        assert get_max_upload_size_bytes() == DEFAULT_MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def test_get_max_upload_size_bytes_custom(self, monkeypatch):
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "12")
        assert get_max_upload_size_bytes() == 12 * 1024 * 1024

    def test_get_max_upload_size_bytes_invalid(self, monkeypatch):
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "abc")
        assert get_max_upload_size_bytes() == DEFAULT_MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def test_get_max_upload_size_bytes_zero_negative(self, monkeypatch):
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "0")
        assert get_max_upload_size_bytes() == DEFAULT_MAX_UPLOAD_SIZE_MB * 1024 * 1024
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "-5")
        assert get_max_upload_size_bytes() == DEFAULT_MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def test_is_valid_video_size_true(self):
        upload_file = Mock()
        upload_file.file = io.BytesIO(b"a" * 1024)

        assert is_valid_video_size(upload_file, max_size_bytes=2048) is True

    def test_is_valid_video_size_false(self):
        upload_file = Mock()
        upload_file.file = io.BytesIO(b"a" * 4096)

        assert is_valid_video_size(upload_file, max_size_bytes=1024) is False

    def test_is_valid_video_size_exception(self):
        upload_file = Mock()
        class BrokenStream:
            def tell(self):
                raise Exception("fail")
            def seek(self, *args):
                raise Exception("fail")
        upload_file.file = BrokenStream()
        # Deve retornar True em caso de erro
        assert is_valid_video_size(upload_file, max_size_bytes=1024) is True
