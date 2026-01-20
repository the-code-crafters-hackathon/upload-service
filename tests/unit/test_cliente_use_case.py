import pytest
from unittest.mock import Mock

from app.use_cases.cliente_use_case import ClienteUseCase
from app.entities.cliente.models import Cliente
from app.adapters.schemas.cliente import ClienteResponseSchema
from app.adapters.dto.cliente_dto import ClienteCreateSchema, ClienteUpdateSchema


@pytest.fixture
def mock_entity():
    return Mock()


@pytest.fixture
def use_case(mock_entity):
    return ClienteUseCase(mock_entity)


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


# ------------------------------------------------------
# criar_cliente
# ------------------------------------------------------
def test_criar_cliente(use_case, mock_entity, cliente_model):
    dto = ClienteCreateSchema(
        nome="João Silva",
        email="joao@example.com",
        telefone="11999999999",
        cpf="12345678901"
    )

    mock_entity.criar_cliente.return_value = cliente_model

    result = use_case.criar_cliente(dto)

    assert isinstance(result, ClienteResponseSchema)
    assert result.id == cliente_model.id
    mock_entity.criar_cliente.assert_called_once_with(cliente=dto)


# ------------------------------------------------------
# buscar_cliente_por_cpf
# ------------------------------------------------------
def test_buscar_cliente_por_cpf_sucesso(use_case, mock_entity, cliente_model):
    mock_entity.buscar_por_cpf.return_value = cliente_model

    result = use_case.buscar_cliente_por_cpf("12345678901")

    assert result.id == cliente_model.id
    mock_entity.buscar_por_cpf.assert_called_once_with(cpf_cliente="12345678901")


def test_buscar_cliente_por_cpf_nao_encontrado(use_case, mock_entity):
    mock_entity.buscar_por_cpf.return_value = None

    with pytest.raises(ValueError, match="Cliente não encontrado"):
        use_case.buscar_cliente_por_cpf("12345678901")


# ------------------------------------------------------
# buscar_cliente_por_id
# ------------------------------------------------------
def test_buscar_cliente_por_id_sucesso(use_case, mock_entity, cliente_model):
    mock_entity.buscar_por_id.return_value = cliente_model

    result = use_case.buscar_cliente_por_id(1)

    assert result.id == cliente_model.id
    mock_entity.buscar_por_id.assert_called_once_with(id=1)


def test_buscar_cliente_por_id_nao_encontrado(use_case, mock_entity):
    mock_entity.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Cliente não encontrado"):
        use_case.buscar_cliente_por_id(1)


# ------------------------------------------------------
# listar_clientes
# ------------------------------------------------------
def test_listar_clientes(use_case, mock_entity, cliente_model):
    mock_entity.listar_todos.return_value = [cliente_model]

    result = use_case.listar_clientes()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == cliente_model.id
    mock_entity.listar_todos.assert_called_once()


# ------------------------------------------------------
# atualizar_cliente
# ------------------------------------------------------
def test_atualizar_cliente_sucesso(use_case, mock_entity, cliente_model):
    # buscar_cliente_por_id first
    mock_entity.buscar_por_id.return_value = cliente_model

    updated = Cliente(
        nome="João Atualizado",
        email="joao2@example.com",
        telefone="11888888888",
        cpf="12345678901",
    )
    updated.id = 1

    mock_entity.atualizar_cliente.return_value = updated

    dto = ClienteUpdateSchema(nome="João Atualizado")

    result = use_case.atualizar_cliente(1, dto)

    assert result.nome == "João Atualizado"
    mock_entity.buscar_por_id.assert_called_once_with(id=1)
    mock_entity.atualizar_cliente.assert_called_once_with(id=1, cliente=dto)


def test_atualizar_cliente_nao_encontrado(use_case, mock_entity):
    mock_entity.buscar_por_id.return_value = None

    with pytest.raises(ValueError, match="Cliente não encontrado"):
        use_case.atualizar_cliente(1, ClienteUpdateSchema(nome="Teste"))


# ------------------------------------------------------
# deletar_cliente
# ------------------------------------------------------
def test_deletar_cliente(use_case, mock_entity):
    use_case.deletar_cliente(1)

    mock_entity.deletar_cliente.assert_called_once_with(id=1)
