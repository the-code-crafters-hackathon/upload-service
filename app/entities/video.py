from abc import ABC, abstractmethod
from app.models.video import Video

class VideoEntities(ABC):
    @abstractmethod
    def create_video(self, video: Video): pass