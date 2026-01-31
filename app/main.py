from app.infrastructure.api.fastapi import app
from app.api import check
from app.api import video

# declare
app.include_router(check.router)
app.include_router(video.router)