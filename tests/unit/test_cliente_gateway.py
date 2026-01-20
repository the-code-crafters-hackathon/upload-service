import pytest
from unittest.mock import Mock

from app.gateways.cliente_gateway import ClienteGateway
from app.entities.cliente.models import Cliente


@pytest.fixture
def mock_dao():
    return Mock()


@pytest.fixture
def gateway(mock_dao, monkeypatch):
    from app.gateways import cliente_gateway

    monkeypatch.setattr(cliente_gateway, "ClienteDAO", lambda session: mock_dao)

    return ClienteGateway(db_session=Mock())


@pytest.fixture
def cliente_model():
    cliente = Cliente(
        nome="João Silva",
        email="joao@example.com",
        telefone="11999999999",
        cpf="12345678901"
    )
    cliente.id = 1
    return cliente


# --------------------------------------------------------------
# criar_cliente
# --------------------------------------------------------------
def test_criar_cliente(gateway, mock_dao, cliente_model):
    mock_dao.criar_cliente.return_value = cliente_model

    result = gateway.criar_cliente(cliente_model)

    assert result == cliente_model
    mock_dao.criar_cliente.assert_called_once_with(cliente_model)


# --------------------------------------------------------------
# buscar_por_cpf
# --------------------------------------------------------------
def test_buscar_por_cpf(gateway, mock_dao, cliente_model):
    mock_dao.buscar_por_cpf.return_value = cliente_model

    result = gateway.buscar_por_cpf("12345678901")

    assert result == cliente_model
    mock_dao.buscar_por_cpf.assert_called_once_with("12345678901")


def test_buscar_por_cpf_not_found(gateway, mock_dao):
    mock_dao.buscar_por_cpf.return_value = None

    result = gateway.buscar_por_cpf("12345678901")

    assert result is None
    mock_dao.buscar_por_cpf.assert_called_once_with("12345678901")


# --------------------------------------------------------------
# buscar_por_id
# --------------------------------------------------------------
def test_buscar_por_id(gateway, mock_dao, cliente_model):
    mock_dao.buscar_por_id.return_value = cliente_model

    result = gateway.buscar_por_id(1)

    assert result == cliente_model
    mock_dao.buscar_por_id.assert_called_once_with(1)


def test_buscar_por_id_not_found(gateway, mock_dao):
    mock_dao.buscar_por_id.return_value = None

    result = gateway.buscar_por_id(1)

    assert result is None
    mock_dao.buscar_por_id.assert_called_once_with(1)


# --------------------------------------------------------------
# listar_todos
# --------------------------------------------------------------
def test_listar_todos(gateway, mock_dao, cliente_model):
    mock_dao.listar_todos.return_value = [cliente_model]

    result = gateway.listar_todos()

    assert isinstance(result, list)
    assert result[0] == cliente_model
    mock_dao.listar_todos.assert_called_once()


# --------------------------------------------------------------
# atualizar_cliente
# --------------------------------------------------------------
def test_atualizar_cliente(gateway, mock_dao, cliente_model):
    mock_dao.atualizar_cliente.return_value = cliente_model

    result = gateway.atualizar_cliente(1, cliente_model)

    assert result == cliente_model
    mock_dao.atualizar_cliente.assert_called_once_with(1, cliente_model)


# --------------------------------------------------------------
# deletar_cliente
# --------------------------------------------------------------
def test_deletar_cliente(gateway, mock_dao):
    gateway.deletar_cliente(1)

    mock_dao.deletar_cliente.assert_called_once_with(1)
