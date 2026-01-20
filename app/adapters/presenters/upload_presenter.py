from pydantic import BaseModel

class VideoUploadResponse(BaseModel):
    status: str
    data: list[str]