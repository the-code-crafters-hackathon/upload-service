import pytest
from fastapi import HTTPException

from app.api import cliente as cliente_api
from app.adapters.dto.cliente_dto import ClienteCreateSchema


def test_criar_cliente_success(monkeypatch):
    class FakeController:
        def __init__(self, db_session):
            pass

        def criar_cliente(self, cliente_data):
            return {"status": "success", "data": {"id": 1, "nome": cliente_data.nome, "email": cliente_data.email, "telefone": None, "cpf": cliente_data.cpf}}

    monkeypatch.setattr(cliente_api, "ClienteController", FakeController)

    # CPF must be at least 11 chars per schema
    schema = ClienteCreateSchema(nome="Fulano", email="f@x.com", telefone=None, cpf="12345678901")
    res = cliente_api.criar_cliente(schema, gateway=None)

    assert res["status"] == "success"
    assert res["data"]["nome"] == "Fulano"


def test_buscar_cliente_por_cpf_not_found(monkeypatch):
    class FakeController:
        def __init__(self, db_session):
            pass

        def buscar_cliente_por_cpf(self, cpf):
            raise ValueError("Cliente não encontrado")

    monkeypatch.setattr(cliente_api, "ClienteController", FakeController)

    with pytest.raises(HTTPException) as exc:
        cliente_api.buscar_cliente_por_cpf("000", gateway=None)

    assert exc.value.status_code == 404
