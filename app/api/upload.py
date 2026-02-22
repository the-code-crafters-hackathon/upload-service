import os

from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status, Path
from pathlib import Path as PathlibPath

from app.infrastructure.db.database import get_db
from app.dao.video_dao import VideoDAO
from app.gateways.video_processing_gateway import VideoProcessingGateway
from app.gateways.sqs_producer import SQSProducer
from app.use_cases.upload_use_case import UploadUseCase
from app.controllers.upload_controller import UploadController
from app.controllers.list_videos_controller import ListVideosController, VideoListResponse
from app.adapters.presenters.video_presenter import VideoResponse
from app.infrastructure.security.auth import get_current_user, enforce_same_user, AuthenticatedUser

router = APIRouter(prefix="/upload", tags=["upload"])

VALID_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
VALID_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
    "video/x-matroska",
    "video/x-ms-wmv",
    "video/x-flv",
    "video/webm",
}
DEFAULT_MAX_UPLOAD_SIZE_MB = 100


def is_valid_video_file(filename: str) -> bool:
    return PathlibPath(filename).suffix.lower() in VALID_VIDEO_EXTENSIONS


def is_valid_video_content_type(content_type: str | None) -> bool:
    if not content_type:
        return False

    normalized_type = content_type.split(";", 1)[0].strip().lower()

    return normalized_type in VALID_VIDEO_CONTENT_TYPES


def get_max_upload_size_bytes() -> int:
    raw_value = os.getenv("MAX_UPLOAD_SIZE_MB", str(DEFAULT_MAX_UPLOAD_SIZE_MB))
    try:
        max_mb = int(raw_value)
        if max_mb <= 0:
            raise ValueError()
        return max_mb * 1024 * 1024
    except (ValueError, TypeError):
        return DEFAULT_MAX_UPLOAD_SIZE_MB * 1024 * 1024


def is_valid_video_size(upload_file: UploadFile, max_size_bytes: int) -> bool:
    file_stream = getattr(upload_file, "file", None)
    if file_stream is None:
        return True

    try:
        current_position = file_stream.tell()
        file_stream.seek(0, 2)
        file_size = file_stream.tell()
        file_stream.seek(current_position)
        return file_size <= max_size_bytes
    except Exception:
        return True

def get_processing_gateway():
    base_dir = PathlibPath(__file__).resolve().parents[2]

    return VideoProcessingGateway(base_dir=base_dir)

def get_sqs_producer():
    return SQSProducer()


@router.post("/video", response_model=VideoResponse, status_code=status.HTTP_201_CREATED, responses={
    400: {
        "description": "Erro de validação",
        "content": {
            "application/json": {
                "example": {
                    "message": "Erro de integridade ao processar video"
                }
            }
        }
    }
})
async def upload_and_process_video(
    user_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db = Depends(get_db),
    processing_gateway: VideoProcessingGateway = Depends(get_processing_gateway),
    sqs_producer: SQSProducer = Depends(get_sqs_producer),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    enforce_same_user(user_id, current_user)

    if not is_valid_video_file(file.filename) or not is_valid_video_content_type(file.content_type):
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")

    max_size_bytes = get_max_upload_size_bytes()
    if not is_valid_video_size(file, max_size_bytes):
        max_size_mb = max_size_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo excede o limite de {max_size_mb}MB",
        )

    video_dao = VideoDAO(db)
    use_case = UploadUseCase(processing_gateway=processing_gateway, video_dao=video_dao, sqs_producer=sqs_producer)
    controller = UploadController(use_case)

    response = controller.upload_video(user_id=user_id, title=title, upload_file=file)

    return response

@router.get("/videos/{user_id}", response_model=VideoListResponse, status_code=status.HTTP_200_OK)
async def list_user_videos(
    user_id: int = Path(..., description="ID do usuário"),
    db = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        enforce_same_user(user_id, current_user)

        video_dao = VideoDAO(db)
        controller = ListVideosController(video_dao)
        
        return controller.list_user_videos(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )