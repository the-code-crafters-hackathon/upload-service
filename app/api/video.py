from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.db.database import get_db

from app.gateways.video_gateway import VideoGateway
from app.adapters.presenters.video_presenter import VideoResponse
from app.adapters.dto.video_dto import VideoCreateSchema
from app.controllers.video_controller import VideoController
from app.adapters.utils.debug import var_dump_die

router = APIRouter(prefix="/video-uploader", tags=["videos"])

def get_video_gateway(database: Session = Depends(get_db)) -> VideoGateway:

    return VideoGateway(db_session=database)

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED, responses={
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
def criar_video(video_data: VideoCreateSchema, gateway: VideoGateway = Depends(get_video_gateway)):
    try:
        
        return (VideoController(db_session=gateway)
                    .upload_video(video_data))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
