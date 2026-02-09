Feature: Upload e Processamento de Vídeos
  Como um sistema de processamento de vídeos
  Quero permitir upload, processamento e listagem de vídeos
  Para garantir o funcionamento correto da API de vídeos

  # ---------------------------------------------------------
  # CENÁRIO: Upload de Vídeo
  # ---------------------------------------------------------
  Scenario: Fazer upload de vídeo válido
    Given que eu possuo um arquivo de vídeo válido
    And o arquivo tem um dos formatos suportados (mp4, avi, mov, mkv, wmv, flv, webm)
    When eu envio uma requisição POST para "/upload/video"
    With user_id = 1 e title = "Meu vídeo"
    Then o sistema deve retornar status 201
    And o corpo deve conter os dados do vídeo criado
    And o status deve ser 0 (processando)

  Scenario: Falha ao fazer upload de arquivo inválido
    Given que eu envio um arquivo com formato não suportado
    When eu envio uma requisição POST para "/upload/video"
    Then o sistema deve retornar status 400
    And a mensagem deve ser "Formato de arquivo não suportado"

  # ---------------------------------------------------------
  # CENÁRIO: Listar Vídeos do Usuário
  # ---------------------------------------------------------
  Scenario: Listar vídeos de um usuário existente
    Given que existe um usuário com ID 1
    And esse usuário tem 3 vídeos cadastrados
    When eu envio uma requisição GET para "/upload/videos/1"
    Then o sistema deve retornar status 200
    And o corpo deve conter lista com 3 vídeos
    And cada vídeo deve ter id, user_id, title, file_path, status

  Scenario: Usuário sem vídeos
    Given que existe um usuário com ID 999
    And esse usuário não tem vídeos cadastrados
    When eu envio uma requisição GET para "/upload/videos/999"
    Then o sistema deve retornar status 200
    And o corpo deve conter lista vazia

  # ---------------------------------------------------------
  # CENÁRIO: Processamento em Background
  # ---------------------------------------------------------
  Scenario: Vídeo é processado em background após upload
    Given que fiz upload de um vídeo
    And recebi a resposta com status 0 (processando)
    When aguardo alguns segundos
    Then o status do vídeo deve ser atualizado para 1 (concluído)
    And o file_path deve apontar para o ZIP com frames
