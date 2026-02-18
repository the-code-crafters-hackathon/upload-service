from fastapi import FastAPI, Depends
from app.infrastructure.db.database import init_schema

app = FastAPI(
    title="Sistema de upload de videos",
    description="Documentacao automatica via Swagger e Redoc",
    version="1.0.0",
)


@app.on_event("startup")
def startup_init_schema() -> None:
    init_schema()