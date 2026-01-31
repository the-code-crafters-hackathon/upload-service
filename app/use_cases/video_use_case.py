from app.entities.video import VideoEntities
from app.models.video import Video
from app.adapters.schemas.video import VideoResponseSchema
from app.adapters.dto.video_dto import VideoCreateSchema

class VideoUseCase:
    def __init__(self, entity: VideoEntities):
        self.video_entity = entity

    def upload_video(self, videoRequest: VideoCreateSchema) -> VideoResponseSchema:       
        videoCreated: Video = self.video_entity.create_video(video=videoRequest)
        
        return VideoResponseSchema(
            id=videoCreated.id,
            title=videoCreated.title,
            file_path=videoCreated.file_path,
            status=videoCreated.status
        )