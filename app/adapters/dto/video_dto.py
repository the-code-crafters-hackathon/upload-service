from pydantic import BaseModel

class VideoCreateSchema(BaseModel):
    user_id: int
    title: str
    file_path: str
    status: int

class VideoUploadSchema(BaseModel):
    user_id: int
    title: str
    file_path: str
    status: int