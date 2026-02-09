from typing import List
from app.dao.video_dao import VideoDAO
from app.adapters.schemas.video import VideoResponseSchema
from pydantic import BaseModel


class VideoListResponse(BaseModel):
    status: str
    data: List[VideoResponseSchema]


class ListVideosController:
    def __init__(self, video_dao: VideoDAO):
        self.video_dao = video_dao

    def list_user_videos(self, user_id: int) -> VideoListResponse:
        videos = self.video_dao.list_videos_by_user(user_id)

        response_data = [
            VideoResponseSchema(
                id=video.id,
                user_id=video.user_id,
                title=video.title,
                file_path=video.file_path,
                status=video.status,
            )
            for video in videos
        ]

        return VideoListResponse(status="success", data=response_data)
