from pydantic import BaseModel

class VideoResponseSchema(BaseModel):
    id: int
    user_id: int
    title: str
    file_path: str
    status: int