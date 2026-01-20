from sqlalchemy.exc import IntegrityError

from app.models.cliente import Cliente
from app.models.cliente import Cliente as ClienteModel

class ClienteDAO:
    
    def __init__(self, db_session):
        self.db_session = db_session

    def criar_cliente(self, cliente : Cliente):
        try:
            cliente_model = ClienteModel(
                nome=cliente.nome,
                email=cliente.email,
                telefone=cliente.telefone,
                cpf=cliente.cpf
            )
            self.db_session.add(cliente_model)
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            
            raise Exception(f"Erro de integridade ao criar cliente: {e}")
        
        self.db_session.refresh(cliente_model)

        return cliente_model