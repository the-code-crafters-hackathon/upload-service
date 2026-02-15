import logging
from datetime import datetime
from app.gateways.video_processing_gateway import VideoProcessingGateway
from app.gateways.sqs_producer import SQSProducer
from app.dao.video_dao import VideoDAO
from app.adapters.dto.video_dto import VideoCreateSchema

logger = logging.getLogger(__name__)


class UploadUseCase:
    def __init__(self, processing_gateway: VideoProcessingGateway, video_dao: VideoDAO, sqs_producer: SQSProducer = None):
        self.processing_gateway = processing_gateway
        self.video_dao = video_dao
        self.sqs_producer = sqs_producer or SQSProducer()

    def execute(self, user_id: int, title: str, upload_file) -> tuple:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_path = self.processing_gateway.save_upload(upload_file, timestamp)

        dto = VideoCreateSchema(user_id=user_id, title=title, file_path=str(saved_path), status=0)
        created = self.video_dao.create_video(dto)
        
        message = {
            "video_id": created.id,
            "video_path": str(saved_path),
            "timestamp": timestamp,
            "user_id": user_id
        }
        
        success = self.sqs_producer.send_message(message)
        if not success:
            logger.warning(f"Falha ao enviar mensagem SQS para vídeo {created.id}, mas upload foi concluído")

        return created, str(saved_path), timestamp
