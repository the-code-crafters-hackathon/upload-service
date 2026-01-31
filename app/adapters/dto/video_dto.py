from pydantic import BaseModel

class VideoCreateSchema(BaseModel):
    title: str
    file_path: str
    status: int

class VideoUploadSchema(BaseModel):
    title: str
    file_path: str
    status: int