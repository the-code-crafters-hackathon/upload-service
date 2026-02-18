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


def is_valid_video_file(filename: str) -> bool:
    return PathlibPath(filename).suffix.lower() in VALID_VIDEO_EXTENSIONS


def is_valid_video_content_type(content_type: str | None) -> bool:
    if not content_type:
        return False

    normalized_type = content_type.split(";", 1)[0].strip().lower()

    return normalized_type in VALID_VIDEO_CONTENT_TYPES

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
):
    if not is_valid_video_file(file.filename) or not is_valid_video_content_type(file.content_type):
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")

    video_dao = VideoDAO(db)
    use_case = UploadUseCase(processing_gateway=processing_gateway, video_dao=video_dao, sqs_producer=sqs_producer)
    controller = UploadController(use_case)

    response = controller.upload_video(user_id=user_id, title=title, upload_file=file)

    return response

@router.get("/videos/{user_id}", response_model=VideoListResponse, status_code=status.HTTP_200_OK)
async def list_user_videos(
    user_id: int = Path(..., description="ID do usuário"),
    db = Depends(get_db),
):
    try:
        video_dao = VideoDAO(db)
        controller = ListVideosController(video_dao)
        
        return controller.list_user_videos(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )