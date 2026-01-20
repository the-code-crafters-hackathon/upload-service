import pytest
from fastapi import HTTPException

from app.controllers.cliente_controller import ClienteController


def test_criar_cliente_success(monkeypatch):
    class FakeUseCase:
        def __init__(self, db_session):
            pass

        def criar_cliente(self, cliente_data):
            return {"id": 1, "nome": cliente_data.nome, "email": cliente_data.email, "telefone": None, "cpf": cliente_data.cpf}

    monkeypatch.setattr("app.controllers.cliente_controller.ClienteUseCase", FakeUseCase)

    controller = ClienteController(db_session=None)

    class Dummy:
        nome = "Fulano"
        email = "f@x.com"
        cpf = "123"

    res = controller.criar_cliente(Dummy)

    assert res.status == "success"
    assert res.data.id == 1


def test_buscar_cliente_por_cpf_not_found(monkeypatch):
    class FakeUseCase:
        def __init__(self, db_session):
            pass

        def buscar_cliente_por_cpf(self, cpf):
            raise ValueError("Cliente não encontrado")

    monkeypatch.setattr("app.controllers.cliente_controller.ClienteUseCase", FakeUseCase)

    controller = ClienteController(db_session=None)
    with pytest.raises(HTTPException) as exc:
        controller.buscar_cliente_por_cpf("000")

    assert exc.value.status_code == 404
