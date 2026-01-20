from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    return {"status": "ok"}

@router.get("/db")
def health_db_check(db: Session = Depends(get_db)):
    return {"status": "connected"}