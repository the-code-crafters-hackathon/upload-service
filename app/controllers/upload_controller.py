from app.use_cases.upload_use_case import UploadUseCase
from app.adapters.presenters.video_presenter import VideoResponse
from app.adapters.schemas.video import VideoResponseSchema


class UploadController:
    def __init__(self, use_case: UploadUseCase):
        self.use_case = use_case

    def upload_video(self, user_id: int, title: str, upload_file) -> tuple:
        created_video, saved_path, timestamp = self.use_case.execute(user_id, title, upload_file)

        response_data = VideoResponseSchema(
            id=created_video.id,
            user_id=created_video.user_id,
            title=created_video.title,
            file_path=created_video.file_path,
            status=created_video.status,
        )

        return VideoResponse(status="success", data=response_data), (created_video.id, saved_path, timestamp)
