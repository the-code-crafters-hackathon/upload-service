from pydantic import BaseModel
from app.adapters.schemas.video import VideoResponseSchema

class VideoResponse(BaseModel):
    status: str
    data: VideoResponseSchema