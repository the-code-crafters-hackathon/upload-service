import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, status

from app.controllers.cliente_controller import ClienteController
from app.adapters.dto.cliente_dto import ClienteCreateSchema, ClienteUpdateSchema
from app.adapters.presenters.cliente_presenter import ClienteResponse, ClienteResponseList
from app.adapters.utils.debug import var_dump_die

@pytest.fixture
def mock_db_session():
    
    return Mock()


@pytest.fixture
def controller(mock_db_session):
    
    return ClienteController(mock_db_session)


@pytest.fixture
def sample_cliente_create():
    
    return ClienteCreateSchema(
        nome="João Silva",
        cpf="12345678901",
        email="joao@example.com",
        telefone="11999999999"
    )


@pytest.fixture
def sample_cliente_update():
    
    return ClienteUpdateSchema(
        nome="João Silva Atualizado",
        email="joao.novo@example.com",
        telefone="11988888888"
    )


@pytest.fixture
def sample_cliente_data():
    
    return {
        "id": 1,
        "nome": "João Silva",
        "cpf": "12345678901",
        "email": "joao@example.com",
        "telefone": "11999999999"
    }


class TestCriarCliente:
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_criar_cliente_sucesso(self, mock_use_case, controller, mock_db_session, 
                                   sample_cliente_create, sample_cliente_data):

        # Arrange
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.criar_cliente.return_value = sample_cliente_data
        
        # Act
        result = controller.criar_cliente(sample_cliente_create)
        
        # Assert
        mock_use_case.assert_called_once_with(mock_db_session)
        mock_use_case_instance.criar_cliente.assert_called_once_with(sample_cliente_create)
        assert result.status == 'success'

        #assert result.data == sample_cliente_data['id']
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_criar_cliente_erro_generico(self, mock_use_case, controller, sample_cliente_create):
        
        # Arrange
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.criar_cliente.side_effect = Exception("Erro ao criar cliente")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.criar_cliente(sample_cliente_create)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro ao criar cliente" in str(exc_info.value.detail)


class TestBuscarClientePorCpf:
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_buscar_cliente_por_cpf_sucesso(self, mock_use_case, controller, 
                                           mock_db_session, sample_cliente_data):

        # Arrange
        cpf = "12345678901"
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.buscar_cliente_por_cpf.return_value = sample_cliente_data
        
        # Act
        result = controller.buscar_cliente_por_cpf(cpf)
        
        # Assert
        mock_use_case.assert_called_once_with(mock_db_session)
        mock_use_case_instance.buscar_cliente_por_cpf.assert_called_once_with(cpf)
        assert result.status == 'success'
        #assert result.data == sample_cliente_data
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_buscar_cliente_por_cpf_nao_encontrado(self, mock_use_case, controller):
        
        # Arrange
        cpf = "99999999999"
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.buscar_cliente_por_cpf.side_effect = ValueError("Cliente não encontrado")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.buscar_cliente_por_cpf(cpf)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Cliente não encontrado" in str(exc_info.value.detail)
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_buscar_cliente_por_cpf_erro_generico(self, mock_use_case, controller):
        
        # Arrange
        cpf = "12345678901"
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.buscar_cliente_por_cpf.side_effect = Exception("Erro no banco de dados")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.buscar_cliente_por_cpf(cpf)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro no banco de dados" in str(exc_info.value.detail)


class TestBuscarCliente:
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_buscar_cliente_sucesso(self, mock_use_case, controller, 
                                    mock_db_session, sample_cliente_data):
    
        # Arrange
        cliente_id = 1
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.buscar_cliente_por_id.return_value = sample_cliente_data
        
        # Act
        result = controller.buscar_cliente(cliente_id)
        
        # Assert
        mock_use_case.assert_called_once_with(mock_db_session)
        mock_use_case_instance.buscar_cliente_por_id.assert_called_once_with(cliente_id)
        assert result.status == 'success'
        #assert result.data == sample_cliente_data
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_buscar_cliente_nao_encontrado(self, mock_use_case, controller):
    
        # Arrange
        cliente_id = 999
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.buscar_cliente_por_id.side_effect = ValueError("Cliente não encontrado")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.buscar_cliente(cliente_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Cliente não encontrado" in str(exc_info.value.detail)
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_buscar_cliente_erro_generico(self, mock_use_case, controller):
    
        # Arrange
        cliente_id = 1
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.buscar_cliente_por_id.side_effect = Exception("Erro de conexão")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.buscar_cliente(cliente_id)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro de conexão" in str(exc_info.value.detail)


class TestListarClientes:
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_listar_clientes_vazio(self, mock_use_case, controller, mock_db_session):

        # Arrange
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.listar_clientes.return_value = []
        
        # Act
        result = controller.listar_clientes()
        
        # Assert
        assert result.status == 'success'
        assert result.data == []
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_listar_clientes_erro(self, mock_use_case, controller):

        # Arrange
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.listar_clientes.side_effect = Exception("Erro ao listar")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.listar_clientes()
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro ao listar" in str(exc_info.value.detail)


class TestAtualizarCliente:
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_atualizar_cliente_sucesso(self, mock_use_case, controller, mock_db_session,
                                       sample_cliente_update, sample_cliente_data):
    
        # Arrange
        cliente_id = 1
        updated_data = {**sample_cliente_data, "nome": "João Silva Atualizado"}
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.atualizar_cliente.return_value = updated_data
        
        # Act
        result = controller.atualizar_cliente(cliente_id, sample_cliente_update)
        
        # Assert
        mock_use_case.assert_called_once_with(mock_db_session)
        mock_use_case_instance.atualizar_cliente.assert_called_once_with(
            id=cliente_id, 
            clienteRequest=sample_cliente_update
        )
        assert result.status == 'success'
        #assert result.data == updated_data
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_atualizar_cliente_nao_encontrado(self, mock_use_case, controller, sample_cliente_update):
    
        # Arrange
        cliente_id = 999
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.atualizar_cliente.side_effect = ValueError("Cliente não encontrado")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.atualizar_cliente(cliente_id, sample_cliente_update)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Cliente não encontrado" in str(exc_info.value.detail)
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_atualizar_cliente_erro_generico(self, mock_use_case, controller, sample_cliente_update):
    
        # Arrange
        cliente_id = 1
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.atualizar_cliente.side_effect = Exception("Erro de validação")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.atualizar_cliente(cliente_id, sample_cliente_update)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro de validação" in str(exc_info.value.detail)


class TestDeletarCliente:
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_deletar_cliente_sucesso(self, mock_use_case, controller, mock_db_session):

        # Arrange
        cliente_id = 1
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.deletar_cliente.return_value = None
        
        # Act
        result = controller.deletar_cliente(cliente_id)
        
        # Assert
        mock_use_case.assert_called_once_with(mock_db_session)
        mock_use_case_instance.deletar_cliente.assert_called_once_with(id=cliente_id)
        assert result.status_code == status.HTTP_204_NO_CONTENT
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_deletar_cliente_nao_encontrado(self, mock_use_case, controller):
    
        # Arrange
        cliente_id = 999
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.deletar_cliente.side_effect = ValueError("Cliente não encontrado")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.deletar_cliente(cliente_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Cliente não encontrado" in str(exc_info.value.detail)
    
    @patch('app.controllers.cliente_controller.ClienteUseCase')
    def test_deletar_cliente_erro_generico(self, mock_use_case, controller):
    
        # Arrange
        cliente_id = 1
        mock_use_case_instance = mock_use_case.return_value
        mock_use_case_instance.deletar_cliente.side_effect = Exception("Erro ao deletar")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.deletar_cliente(cliente_id)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro ao deletar" in str(exc_info.value.detail)


class TestClienteControllerIntegration:
    
    def test_controller_inicializacao(self, mock_db_session):
        """Testa inicialização do controller."""
        # Act
        controller = ClienteController(mock_db_session)
        
        # Assert
        assert controller.db_session == mock_db_session
        assert isinstance(controller, ClienteController)