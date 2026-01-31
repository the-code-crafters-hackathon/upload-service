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
                title=video.title,
                file_path=video.file_path,
                status=video.status
            )
            self.db_session.add(video_model)
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            
            raise Exception(f"Erro de integridade ao criar cliente: {e}")
        
        self.db_session.refresh(video_model)

        return video_model