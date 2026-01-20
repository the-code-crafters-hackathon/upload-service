from abc import ABC, abstractmethod
from typing import Optional

from app.models.categoria_produto import CategoriaProduto

class CategoriaProdutoRepositoryPort(ABC):
    
    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[CategoriaProduto]:
        pass