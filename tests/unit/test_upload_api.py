import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from app.api.upload import is_valid_video_file


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
