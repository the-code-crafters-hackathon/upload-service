from datetime import datetime
from app.gateways.video_processing_gateway import VideoProcessingGateway
from app.dao.video_dao import VideoDAO
from app.adapters.dto.video_dto import VideoCreateSchema


class UploadUseCase:
    def __init__(self, processing_gateway: VideoProcessingGateway, video_dao: VideoDAO):
        self.processing_gateway = processing_gateway
        self.video_dao = video_dao

    def execute(self, user_id: int, title: str, upload_file) -> tuple:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_path = self.processing_gateway.save_upload(upload_file, timestamp)

        dto = VideoCreateSchema(user_id=user_id, title=title, file_path=str(saved_path), status=0)
        created = self.video_dao.create_video(dto)

        return created, str(saved_path), timestamp
