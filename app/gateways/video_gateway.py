from sqlalchemy.exc import IntegrityError

from app.entities.video import VideoEntities
from app.models.video import Video
from typing import List, Optional
from app.dao.video_dao import VideoDAO
from app.adapters.dto.video_dto import VideoCreateSchema

class VideoGateway(VideoEntities):
    def __init__(self, db_session):
        self.dao = VideoDAO(db_session)

    def create_video(self, video: VideoCreateSchema) -> Video:
        
        return self.dao.create_video(video)