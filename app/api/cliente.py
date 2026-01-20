from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.db.database import get_db
from app.gateways.cliente_gateway import ClienteGateway
from app.adapters.presenters.cliente_presenter import ClienteResponse
from app.adapters.dto.cliente_dto import ClienteCreateSchema, ClienteUpdateSchema
from app.controllers.cliente_controller import ClienteController

router = APIRouter(prefix="/clientes", tags=["clientes"])

def get_cliente_gateway(database: Session = Depends(get_db)) -> ClienteGateway:
    
    return ClienteGateway(db_session=database)

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED, responses={
    400: {
        "description": "Erro de validação",
        "content": {
            "application/json": {
                "example": {
                    "message": "Erro de integridade ao criar cliente"
                }
            }
        }
    }
})
def criar_cliente(cliente_data: ClienteCreateSchema, gateway: ClienteGateway = Depends(get_cliente_gateway)):
    try:
        
        return (ClienteController(db_session=gateway)
                    .criar_cliente(cliente_data))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
