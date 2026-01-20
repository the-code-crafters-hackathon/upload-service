from pydantic import BaseModel

class VideoUploadSchema(BaseModel):
    video: str
    