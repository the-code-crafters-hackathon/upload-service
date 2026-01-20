from fastapi import FastAPI, Depends

app = FastAPI(
    title="Sistema de processamento de videos",
    description="Documentacao automatica via Swagger e Redoc",
    version="1.0.0",
)