from fastapi import status, HTTPException, Response

from app.use_cases.video_use_case import VideoUseCase
from app.adapters.presenters.video_presenter import VideoResponse
from app.adapters.dto.video_dto import VideoCreateSchema
from app.adapters.utils.debug import var_dump_die

class VideoController:
    
    def __init__(self, db_session):
        self.db_session = db_session

    def upload_video(self, video_data : VideoCreateSchema):
        try:
            result = VideoUseCase(self.db_session).upload_video(video_data)

            return VideoResponse(status = 'success', data = result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))