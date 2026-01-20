from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app
from app.api.cliente import get_cliente_gateway
from decimal import Decimal


class MockClienteGateway:
    def __init__(self):
        self.obj = SimpleNamespace(id=1, nome="João Silva", email="joao@example.com", telefone="11999999999", cpf="12345678901")

    def criar_cliente(self, cliente):
        return self.obj

    def buscar_por_cpf(self, cpf_cliente: str):
        return self.obj if cpf_cliente == self.obj.cpf else None

    def buscar_por_id(self, id: int):
        return self.obj if id == self.obj.id else None

    def listar_todos(self):
        return [self.obj]

    def atualizar_cliente(self, id: int, cliente):
        # Accept pydantic models or dicts
        data = None
        if hasattr(cliente, "model_dump"):
            data = cliente.model_dump()
        elif hasattr(cliente, "dict"):
            data = cliente.dict()
        elif isinstance(cliente, dict):
            data = cliente
        else:
            data = {}

        return SimpleNamespace(id=id, nome=data.get("nome", self.obj.nome), email=data.get("email", self.obj.email), telefone=data.get("telefone", self.obj.telefone), cpf=data.get("cpf", self.obj.cpf))

    def deletar_cliente(self, id: int):
        return None


def setup_module(module):
    app.dependency_overrides[get_cliente_gateway] = lambda: MockClienteGateway()


def teardown_module(module):
    app.dependency_overrides.clear()


client = TestClient(app)


def test_criar_e_buscar_cliente_por_cpf():
    payload = {
        "nome": "João Silva",
        "email": "joao@example.com",
        "telefone": "11999999999",
        "cpf": "12345678901"
    }

    r = client.post("/clientes/", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "success"
    assert body["data"]["cpf"] == "12345678901"

    r2 = client.get(f"/clientes/cpf/{payload['cpf']}")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["data"]["email"] == "joao@example.com"


def test_listar_atualizar_e_deletar_cliente():
    r = client.get("/clientes/")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body["data"], list)

    update_payload = {"nome": "João Atualizado"}
    r2 = client.put("/clientes/1", json=update_payload)
    assert r2.status_code == 200
    assert r2.json()["data"]["nome"] == "João Atualizado"

    r3 = client.delete("/clientes/1")
    assert r3.status_code == 204
