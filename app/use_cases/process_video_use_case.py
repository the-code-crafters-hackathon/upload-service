import logging
from app.gateways.video_processing_gateway import VideoProcessingGateway
from app.dao.video_dao import VideoDAO

logger = logging.getLogger(__name__)


class ProcessVideoUseCase:
    def __init__(
        self,
        processing_gateway: VideoProcessingGateway,
        video_dao: VideoDAO,
    ):
        self.processing_gateway = processing_gateway
        self.video_dao = video_dao

    def execute(self, video_id: int, video_path: str, timestamp: str):
        try:
            logger.info(f"Iniciando processamento do vídeo {video_id}")

            zip_path, frame_count, images = self.processing_gateway.process_video(
                video_path, timestamp
            )
            logger.info(
                f"Vídeo {video_id} processado com sucesso. {frame_count} frames extraídos."
            )
            self.video_dao.update_video_status(
                video_id=video_id, status=1, file_path=str(zip_path)
            )

            logger.info(f"Vídeo {video_id} atualizado no banco com sucesso.")

        except Exception as e:
            logger.error(f"Erro ao processar vídeo {video_id}: {str(e)}")
            
            try:
                self.video_dao.update_video_status(video_id=video_id, status=2)
            except Exception as update_error:
                logger.error(f"Erro ao atualizar status do vídeo {video_id}: {str(update_error)}")
