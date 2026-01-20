from sqlalchemy import Column, Integer, String

from app.infrastructure.db.database import Base

class CategoriaProduto(Base):
    __tablename__ = "categoria_produto"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)

    class Config:
        orm_mode = True