from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status, BackgroundTasks, Path
from pathlib import Path as PathlibPath

from app.infrastructure.db.database import get_db
from app.dao.video_dao import VideoDAO
from app.gateways.video_processing_gateway import VideoProcessingGateway
from app.use_cases.upload_use_case import UploadUseCase
from app.use_cases.process_video_use_case import ProcessVideoUseCase
from app.controllers.upload_controller import UploadController
from app.controllers.list_videos_controller import ListVideosController, VideoListResponse
from app.adapters.presenters.video_presenter import VideoResponse

router = APIRouter(prefix="/upload", tags=["upload"])

def is_valid_video_file(filename: str) -> bool:
    valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}

    return PathlibPath(filename).suffix.lower() in valid_extensions

def get_processing_gateway():
    base_dir = PathlibPath(__file__).resolve().parents[2]

    return VideoProcessingGateway(base_dir=base_dir)


def process_video_background(video_id: int, video_path: str, timestamp: str, db, processing_gateway):
    video_dao = VideoDAO(db)
    use_case = ProcessVideoUseCase(
        processing_gateway=processing_gateway,
        video_dao=video_dao
    )
    use_case.execute(video_id, video_path, timestamp)


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
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    if not is_valid_video_file(file.filename):
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")

    video_dao = VideoDAO(db)
    use_case = UploadUseCase(processing_gateway=processing_gateway, video_dao=video_dao)
    controller = UploadController(use_case)

    response, (video_id, saved_path, timestamp) = controller.upload_video(user_id=user_id, title=title, upload_file=file)

    background_tasks.add_task(
        process_video_background,
        video_id=video_id,
        video_path=saved_path,
        timestamp=timestamp,
        db=db,
        processing_gateway=processing_gateway
    )

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