from app.infrastructure.api.fastapi import app, Depends

from app.api import check
from app.api import cliente

# declare
app.include_router(check.router)
app.include_router(cliente.router)