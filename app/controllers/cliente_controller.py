from fastapi import status, HTTPException, Response

from app.use_cases.cliente_use_case import ClienteUseCase
from app.adapters.presenters.cliente_presenter import ClienteResponse
from app.adapters.dto.cliente_dto import ClienteCreateSchema

class ClienteController:
    
    def __init__(self, db_session):
        self.db_session = db_session

    def criar_cliente(self, cliente_data : ClienteCreateSchema):
        try:
            result = ClienteUseCase(self.db_session).criar_cliente(cliente_data)

            return ClienteResponse(status = 'success', data = result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))