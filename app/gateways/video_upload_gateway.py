from sqlalchemy.orm import Session
from typing import Optional

from app.entities.categoria_produto.entities import CategoriaProdutoRepositoryPort
from app.entities.categoria_produto.models import CategoriaProduto
from app.models.categoria_produto import CategoriaProduto as CategoriaProdutoORM
from app.adapters.utils.debug import var_dump_die

class CategoriaProdutoRepository(CategoriaProdutoRepositoryPort):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def buscar_por_id(self, id: int) -> Optional[CategoriaProduto]:
        orm = self.db_session.query(CategoriaProdutoORM).filter_by(id=id).first()
        
        if not orm:
            raise ValueError("Categoria de produto não encontrada")
        
        return orm