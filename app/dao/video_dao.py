from sqlalchemy.exc import IntegrityError

from app.models.video import Video
from app.models.video import Video as VideoModel
from app.adapters.utils.debug import var_dump_die
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class VideoDAO:
    
    def __init__(self, db_session):
        self.db_session = db_session
        
    def create_video(self, video : Video):
        try:
            video_model = VideoModel(
                user_id=video.user_id,
                title=video.title,
                file_path=video.file_path,
                status=video.status
            )
            self.db_session.add(video_model)
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            
            raise Exception(f"Erro de integridade ao criar vídeo: {e}")
        
        self.db_session.refresh(video_model)

        return video_model
    
    def update_video_status(self, video_id: int, status: int, file_path: str = None):
        try:
            video = self.db_session.query(VideoModel).filter(VideoModel.id == video_id).first()

            if not video:
                raise Exception(f"Vídeo com ID {video_id} não encontrado")
            video.status = status

            if file_path:
                video.file_path = file_path
            
            self.db_session.commit()
            self.db_session.refresh(video)
            
            return video
        except IntegrityError as e:
            self.db_session.rollback()
            raise Exception(f"Erro ao atualizar vídeo: {e}")
    
    def list_videos_by_user(self, user_id: int):
        try:
            videos = self.db_session.query(VideoModel).filter(
                VideoModel.user_id == user_id
            ).order_by(VideoModel.id.desc()).all()
            
            return videos
        except Exception as e:
            raise Exception(f"Erro ao listar vídeos do usuário: {e}")