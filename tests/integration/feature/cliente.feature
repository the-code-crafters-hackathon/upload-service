Feature: Gestão de Clientes
  Como um sistema de controle de clientes
  Quero permitir criar, buscar, listar, atualizar e deletar clientes
  Para garantir o funcionamento correto da API de clientes

  # ---------------------------------------------------------
  # CENÁRIO: Criar Cliente
  # ---------------------------------------------------------
  Scenario: Criar um novo cliente com sucesso
    Given que eu possuo dados válidos de um cliente
    When eu envio uma requisição POST para "/clientes/"
    Then o sistema deve retornar status 201
    And o corpo deve conter os dados do cliente criado

  Scenario: Falha ao criar cliente por erro de integridade
    Given que eu envio dados inválidos para criação de cliente
    When eu envio uma requisição POST para "/clientes/"
    Then o sistema deve retornar status 400
    And a mensagem deve ser "Erro de integridade ao criar cliente"

  # ---------------------------------------------------------
  # CENÁRIO: Buscar Cliente por CPF
  # ---------------------------------------------------------
  Scenario: Buscar cliente existente pelo CPF
    Given que existe um cliente cadastrado com o CPF "12345678900"
    When eu envio uma requisição GET para "/clientes/cpf/12345678900"
    Then o sistema deve retornar status 200
    And o corpo deve conter os dados do cliente

  Scenario: Cliente não encontrado ao buscar por CPF
    Given que não existe cliente com o CPF "99999999999"
    When eu envio uma requisição GET para "/clientes/cpf/99999999999"
    Then o sistema deve retornar status 404
    And a mensagem deve ser "Cliente não encontrado"

  Scenario: Erro inesperado ao buscar por CPF
    Given que ocorre um erro inesperado ao consultar o CPF "11111111111"
    When eu envio uma requisição GET para "/clientes/cpf/11111111111"
    Then o sistema deve retornar status 400

  # ---------------------------------------------------------
  # CENÁRIO: Buscar Cliente por ID
  # ---------------------------------------------------------
  Scenario: Buscar cliente existente por ID
    Given que existe um cliente com ID 1
    When eu envio uma requisição GET para "/clientes/1"
    Then o sistema deve retornar status 200
    And os dados do cliente devem ser retornados

  Scenario: Cliente não encontrado ao buscar por ID
    Given que não existe cliente com ID 999
    When eu envio uma requisição GET para "/clientes/999"
    Then o sistema deve retornar status 404
    And a mensagem deve ser "Cliente não encontrado"

  Scenario: Erro inesperado ao buscar por ID
    Given que ocorre um erro inesperado ao consultar o ID 10
    When eu envio uma requisição GET para "/clientes/10"
    Then o sistema deve retornar status 400

  # ---------------------------------------------------------
  # CENÁRIO: Listar Clientes
  # ---------------------------------------------------------
  Scenario: Listar todos os clientes com sucesso
    When eu envio uma requisição GET para "/clientes/"
    Then o sistema deve retornar status 200
    And deve retornar uma lista de clientes

  Scenario: Erro inesperado ao listar clientes
    Given que ocorre um erro ao listar clientes
    When eu envio uma requisição GET para "/clientes/"
    Then o sistema deve retornar status 400

  # ---------------------------------------------------------
  # CENÁRIO: Atualizar Cliente
  # ---------------------------------------------------------
  Scenario: Atualizar cliente com sucesso
    Given que existe um cliente com ID 5
    And que eu forneço dados válidos para atualização
    When eu envio uma requisição PUT para "/clientes/5"
    Then o sistema deve retornar status 200
    And retornar os dados atualizados do cliente

  Scenario: Cliente não encontrado ao atualizar
    Given que não existe cliente com ID 777
    When eu envio uma requisição PUT para "/clientes/777"
    Then o sistema deve retornar status 404
    And a mensagem deve ser "Cliente não encontrado"

  Scenario: Erro ao atualizar cliente por integridade
    Given que envio dados inválidos ao atualizar o cliente 5
    When eu envio uma requisição PUT para "/clientes/5"
    Then o sistema deve retornar status 400
    And a mensagem deve ser "Erro de integridade ao atualizar o cliente"

  # ---------------------------------------------------------
  # CENÁRIO: Deletar Cliente
  # ---------------------------------------------------------
  Scenario: Deletar cliente com sucesso
    Given que existe um cliente com ID 3
    When eu envio uma requisição DELETE para "/clientes/3"
    Then o sistema deve retornar status 204

  Scenario: Cliente não encontrado ao deletar
    Given que não existe cliente com ID 999
    When eu envio uma requisição DELETE para "/clientes/999"
    Then o sistema deve retornar status 404
    And a mensagem deve ser "Cliente não encontrado"

  Scenario: Erro inesperado ao deletar cliente
    Given que ocorre um erro ao deletar o cliente de ID 10
    When eu envio uma requisição DELETE para "/clientes/10"
    Then o sistema deve retornar status 400
