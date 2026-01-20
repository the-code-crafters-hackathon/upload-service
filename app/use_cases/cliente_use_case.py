from app.entities.cliente.entities import ClienteEntities
from app.entities.cliente.models import Cliente
from app.adapters.schemas.cliente import ClienteResponseSchema
from app.adapters.dto.cliente_dto import ClienteCreateSchema, ClienteUpdateSchema

class ClienteUseCase:
    def __init__(self, entity: ClienteEntities):
        self.cliente_entities = entity

    def criar_cliente(self, clienteRequest: ClienteCreateSchema) -> ClienteResponseSchema:       
        clienteCriado: Cliente = self.cliente_entities.criar_cliente(cliente=clienteRequest)
        
        return self._create_response_schema(clienteCriado)