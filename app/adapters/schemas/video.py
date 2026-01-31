from pydantic import BaseModel

class VideoResponseSchema(BaseModel):
    id: int
    title: str
    file_path: str
    status: int