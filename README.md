# 🎬 Video Upload & Processing Service

Uma API moderna e escalável para upload, processamento e gerenciamento de vídeos. Implementada com **Clean Architecture**, suporte a **processamento assíncrono** e **múltiplos uploads simultâneos**.

---

## 📋 Descrição do Projeto

O **Video Upload & Processing Service** é um sistema que permite aos usuários:

- ✅ **Fazer upload de vídeos** em múltiplos formatos (MP4, AVI, MOV, MKV, WMV, FLV, WebM)
- ✅ **Processar vídeos automaticamente** em background, extraindo frames usando FFmpeg
- ✅ **Gerar arquivos ZIP** com os frames extraídos (1 frame por segundo)
- ✅ **Listar vídeos e status** de processamento de um usuário
- ✅ **Suporte a uploads simultâneos** - processar múltiplos vídeos em paralelo
- ✅ **Tracking de status** - 0 (Processando), 1 (Concluído), 2 (Erro)

### 🎯 Requisitos Cumpridos

1. ✅ **Adaptar funcionalidade de `projeto-fiapx/up.py`** para a arquitetura do `upload-service`
2. ✅ **Clean Architecture** - Separação clara entre Controller, UseCase, Gateway, Models e DAO
3. ✅ **Processamento de múltiplos vídeos simultâneos** com publicação em fila SQS + consumo pelo `worker-service`
4. ✅ **Listagem de status dos vídeos** por usuário
5. ✅ **80%+ cobertura de testes unitários** (**44 testes passando / 87% cobertura**)
6. ✅ **FFmpeg integrado** ao Docker para processamento

### ✅ Atualizações recentes (fev/2026)

- Cobertura unitária atual: **87%** (`pytest --cov=app`)
- Suíte unitária: **44 testes passando**
- SonarCloud atualizado para **`sonar.projectVersion=0.2.0`**
- Upload em produção validado com `file_path` em `s3://...` (quando `APP_ENV=production` e `AWS_S3_BUCKET` definido)
- Smoke local do upload disponível em `tests/smoke/smoke-upload-ci-local.sh`
- Smoke legado local (sem JWT) disponível em `tests/smoke/smoke-e2e-upload-worker.sh`
- Smoke E2E oficial com autenticação (evidência do projeto) em `infra/scripts/smoke-e2e-auth-full-flow.sh`

---

## 🏗️ Arquitetura

O `upload-service` segue uma variação de Clean Architecture e tem responsabilidade de **ingestão do vídeo** + **orquestração do processamento assíncrono**.

- Camada HTTP (`app/api`) expõe endpoints e valida request
- Controllers (`app/controllers`) montam respostas e delegam regras
- Use case (`app/use_cases/upload_use_case.py`) executa o caso de uso de upload
- Gateways (`app/gateways`) fazem I/O externo (filesystem/S3 e SQS)
- DAO (`app/dao/video_dao.py`) persiste e consulta dados
- Infra (`app/infrastructure`) concentra bootstrap do FastAPI, DB e autenticação

### 🔌 Diagrama de dependências (upload)

```
Cliente HTTP
  │
  ▼
FastAPI Route (app/api/upload.py)
  │  valida extensão/content-type/tamanho + JWT
  ▼
UploadController
  ▼
UploadUseCase
  ├── VideoProcessingGateway.save_upload()  -> uploads local ou S3
  ├── VideoDAO.create_video(status=0)       -> tabela video
  └── SQSProducer.send_message()            -> fila de processamento
```

### 🔄 Fluxo fim a fim

1. **Upload síncrono (neste serviço)**
  - `POST /upload/video` recebe `user_id`, `title` e arquivo
  - Valida extensão, MIME type e tamanho máximo (`MAX_UPLOAD_SIZE_MB`)
  - Persiste arquivo (local em dev ou S3 em produção)
  - Cria registro na tabela `video` com `status=0`
  - Publica mensagem na fila SQS com metadados do vídeo
  - Retorna `201` imediatamente

2. **Processamento assíncrono (worker-service)**
  - O worker consome a mensagem da fila
  - Processa vídeo (FFmpeg), gera artefatos e atualiza status no banco
  - `status` transita para `1` (concluído) ou `2` (erro)

3. **Consulta de status (neste serviço)**
  - `GET /upload/videos/{user_id}` consulta `VideoDAO.list_videos_by_user`
  - Retorna lista ordenada por `id` desc com `file_path` e `status`

---

## 📁 Estrutura do Projeto

```
upload-service/
├── app/
│   ├── main.py                         # Boot da aplicação e registro de rotas
│   ├── api/
│   │   ├── check.py                    # /health e /health/db
│   │   └── upload.py                   # Endpoints de upload e listagem
│   ├── controllers/
│   │   ├── upload_controller.py
│   │   └── list_videos_controller.py
│   ├── use_cases/
│   │   └── upload_use_case.py
│   ├── gateways/
│   │   ├── video_processing_gateway.py # Salvar upload (FS/S3)
│   │   └── sqs_producer.py             # Publicar evento para processamento
│   ├── dao/
│   │   └── video_dao.py
│   ├── models/
│   │   └── video.py
│   ├── adapters/
│   │   ├── dto/video_dto.py
│   │   ├── schemas/video.py
│   │   └── presenters/video_presenter.py
│   └── infrastructure/
│       ├── api/fastapi.py              # Instância FastAPI + startup
│       ├── db/database.py              # Engine, sessão e init_schema
│       └── security/auth.py            # JWT/Cognito e autorização por usuário
├── tests/
│   ├── unit/
│   ├── integration/
│   └── smoke/
├── uploads/                            # Upload local (dev)
├── temp/                               # Área temporária
├── outputs/
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos

- Docker & Docker Compose
- Ou Python 3.12+ com pip
- FFmpeg (instalado automaticamente no Docker)

### Com Docker (Recomendado)

```bash
cd /var/www/html/pos/hackthon/upload-service

# Build e inicia os containers
docker-compose build
docker-compose up -d

# API estará disponível em http://localhost:8000
# Docs em http://localhost:8000/docs
```

### Sem Docker (Local)

```bash
cd /var/www/html/pos/hackthon/upload-service

# Instalar dependências
pip install -r .docker/bin/config/requirements.txt

# Instalar FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS

# Configurar variáveis de ambiente
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
# ou usar:
export SQLALCHEMY_DATABASE_URL="sqlite:///./test.db"
# Limite máximo de upload em MB (opcional; padrão: 100)
export MAX_UPLOAD_SIZE_MB="100"

# Rodar aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 Endpoints da API

### 1. Upload de Vídeo

**POST** `/upload/video`

**Body (form-data):**
```
user_id: 1 (integer)
title: "Meu vídeo" (string)
file: [arquivo .mp4]
```

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "Meu vídeo",
    "file_path": "/outputs/frames_20260208_150530.zip",
    "status": 0
  }
}
```

**Status codes:**
- `201`: Upload iniciado (processamento em background)
- `400`: Formato inválido
- `500`: Erro de servidor

---

### 2. Listar Vídeos do Usuário

**GET** `/upload/videos/{user_id}`

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Vídeo 1",
      "file_path": "/outputs/frames_20260208_150530.zip",
      "status": 1
    },
    {
      "id": 2,
      "user_id": 1,
      "title": "Vídeo 2",
      "file_path": "/uploads/video_20260208.mp4",
      "status": 0
    }
  ]
}
```

**Status codes:**
- `200`: Lista retornada
- `500`: Erro de servidor

---

## 🧪 Testes

### Rodar Testes Unitários

```bash
cd /var/www/html/pos/hackthon/upload-service

# Todos os testes
pytest tests/unit/ -v

# Com cobertura
DATABASE_URL=sqlite:///./coverage.db pytest tests/unit/ --cov=app --cov-report=term --cov-report=xml:coverage.xml

# Testes específicos
pytest tests/unit/test_video_dao.py -v
pytest tests/unit/test_upload_use_case.py -v
```

### Rodar Testes de Integração

```bash
pytest tests/integration/ -v
```

### Cobertura

**44 testes passando ✅** com **87% de cobertura**:

- ✅ Cobertura total do pacote `app`: **87%**
- ✅ Relatório Sonar/CI gerado em `coverage.xml`
- ✅ Meta mínima de cobertura (**80%**) atendida

### SonarCloud

Configuração no arquivo `sonar-project.properties`:

- `sonar.projectKey=the-code-crafters-hackathon_upload-service`
- `sonar.projectVersion=0.2.0`
- `sonar.python.coverage.reportPaths=coverage.xml`

Fluxo recomendado antes do scan:

```bash
DATABASE_URL=sqlite:///./coverage.db pytest tests/unit/ --cov=app --cov-report=xml:coverage.xml
```

---

## 🔄 Status dos Vídeos

| Status | Valor | Significado |
|--------|-------|-------------|
| Processando | `0` | Video foi enviado e está sendo processado em background |
| Concluído | `1` | Frames extraídos e ZIP criado com sucesso |
| Erro | `2` | Houve erro durante o processamento |

---

## 🛠️ Stack Tecnológico

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic v2
- Python 3.12

**Banco de Dados:**
- PostgreSQL (produção)
- SQLite (desenvolvimento)

**Processamento:**
- FFmpeg
- Amazon SQS (desacoplamento entre upload e processamento)

**Testing:**
- pytest
- pytest-cov
- unittest.mock

**DevOps:**
- Docker
- Docker Compose

---

## 📝 Padrões de Design

### Clean Architecture

```
API → Controllers → UseCases → Gateways → DAOs → DB
```

- **Controllers**: Orquestram requisições HTTP
- **UseCases**: Lógica de negócio pura
- **Gateways**: Abstrações de persistência/processamento
- **DAOs**: Acesso direto ao banco
- **DTOs/Schemas**: Transferência de dados

### Assincronismo

- Upload é **síncrono** (salva arquivo + registra no banco)
- Processamento é **assíncrono** (evento em SQS + execução no `worker-service`)
- Permite múltiplos uploads simultâneos

### Injeção de Dependências

Usa dependências do FastAPI para injetar:
- Sessão do banco de dados
- Gateways de processamento
- Controladores

---

## 🚨 Tratamento de Erros

### Validação de Arquivo

```python
valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}

# Retorna 400 se extensão inválida
```

### Tratamento de Exceptions

```python
try:
    # Processamento
except IntegrityError:
    # Erro de integridade no banco
    raise Exception("Erro de integridade ao criar vídeo")
except Exception as e:
    # Status 2 (erro) + log
    update_status(video_id, status=2)
```

---

## 📊 Diagrama de Classes

```mermaid
classDiagram
  class UploadRoute {
    +POST /upload/video
    +GET /upload/videos/{user_id}
  }

    class VideoDAO {
        -db_session
        +create_video(dto)
        +update_video_status(id, status)
        +list_videos_by_user(user_id)
    }

    class UploadUseCase {
        -processing_gateway
        -video_dao
      -sqs_producer
        +execute(user_id, title, file)
    }

    class VideoProcessingGateway {
        -base_dir
        +save_upload(file, timestamp)
    }

    class SQSProducer {
      -queue_url
      +send_message(payload)
    }

    class UploadController {
        -use_case
        +upload_video(user_id, title, file)
    }

    class ListVideosController {
        -video_dao
        +list_user_videos(user_id)
    }

    UploadRoute --> UploadController
    UploadRoute --> ListVideosController
    VideoDAO --> Video
    UploadUseCase --> VideoDAO
    UploadUseCase --> VideoProcessingGateway
    UploadUseCase --> SQSProducer
    UploadController --> UploadUseCase
    ListVideosController --> VideoDAO
```

---

## 🔐 Segurança

- ✅ Validação de extensão de arquivo
- ✅ Timestamps únicos no nome dos arquivos
- ✅ Isolamento por `user_id`
- ✅ Transações ACID no banco
- ✅ Tratamento de exceções robusto

---

## 📈 Performance

- **Uploads simultâneos**: `POST /upload/video` responde rápido após persistir arquivo + evento
- **Listagem**: O(n) com ordenação por ID descendente
- **Processamento**: executado fora da API (`worker-service`), reduzindo latência no upload
- **Banco**: Índices em `user_id` para queries rápidas

---

## 🤝 Como Contribuir

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📜 Licença

Este projeto é parte de um hackathon FIAP.

---

## 📞 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com ❤️ usando Clean Architecture e FastAPI**
