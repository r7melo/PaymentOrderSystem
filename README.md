# PaymentOrderSystem

Sistema distribuído de ordens de pagamento baseado em microsserviços orientados a eventos e chamadas **RPC assíncronas via RabbitMQ**.

Atualmente, a camada de entrada (**API Gateway**), o serviço de autenticação (**Auth Service** com banco PostgreSQL isolado), a infraestrutura de mensageria (**RabbitMQ**), o monitoramento de logs (**Dozzle**) e a pipeline de testes automatizados (**Quality Gate no Docker Build**) estão implementados e validados.

## 📐 Arquitetura Atual

```
[ Cliente HTTP / Swagger UI ]
              │  HTTP / REST + JWT (Bearer Token / HTTPBearer)
              ▼
[ API Gateway (FastAPI - Porta 30000) ]
              │  AMQP RPC (correlation_id + reply_to)
              ▼
[ RabbitMQ Message Broker (Porta 5672 / UI 15672) ]
              │
              └──► Fila: rpc.auth.requests
                         │
                         ▼
             [ Auth Service (Worker RPC) ]
                         │
                         ▼
             [ PostgreSQL: auth-db (5432) ]

[ Dozzle (Porta 8888) ] ──► Monitoramento de logs dos containers em tempo real
```

### Componentes em Funcionamento

1. **API Gateway (`gateway/`)**:
   - Única borda HTTP/REST do sistema (`http://localhost:30000`).
   - Valida contratos de entrada/saída com **Pydantic v2** e verifica tokens **JWT** via **`HTTPBearer`** (`GET /auth/me`).
   - Traduz requisições HTTP (`POST /auth/register`, `POST /auth/login`) em chamadas **RPC assíncronas via RabbitMQ** (`aio-pika`), gerenciando `correlation_id`, fila de retorno exclusiva (`reply_to`), retentativas de conexão e timeout (`504 Gateway Timeout`).
   - Possui *Multi-stage Dockerfile* com **Quality Gate**: executa `pytest -v` automaticamente durante o build antes de gerar a imagem final.
   - Documentação detalhada em [`gateway/gateway.md`](gateway/gateway.md).

2. **Auth Service (`auth_service/` + `auth_db/`)**:
   - Worker assíncrono (`aio-pika`) sem portas HTTP expostas, consumindo a fila durável `rpc.auth.requests`.
   - Realiza cadastro (`register`) com hash seguro de senha (**`bcrypt`**) e autenticação (`login`) com emissão de tokens **JWT** (`HS256`, expiração de 60 minutos).
   - Banco de dados isolado **PostgreSQL 16** (`auth-db`), inicializado explicitamente via `auth_db/init.sql`.
   - Possui *Multi-stage Dockerfile* com **Quality Gate** (`pytest` com SQLite assíncrono em memória).
   - Documentação detalhada em [`auth_service/auth.md`](auth_service/auth.md).

3. **RabbitMQ (`rabbitmq`)**:
   - Broker AMQP (`5672`) com painel de gerenciamento web (`http://localhost:15672`) e *healthcheck* configurado no Docker Compose.

4. **Dozzle (`dozzle`)**:
   - Visualizador leve de logs em tempo real para todos os containers Docker (`http://localhost:8888`).

## 🛠️ Tecnologias Utilizadas

- **Python 3.12** + **FastAPI** + **Uvicorn** + **Pydantic v2**
- **SQLAlchemy (Async)** + **`asyncpg`** + **PostgreSQL 16**
- **RabbitMQ** + **`aio-pika`** (Cliente AMQP assíncrono / Padrão RPC)
- **PyJWT** & **`bcrypt`** (Autenticação JWT `HS256` e hash de credenciais)
- **`pytest`**, **`pytest-asyncio`**, **`aiosqlite`** & **`httpx`** (Testes automatizados e *Quality Gate* no Docker)
- **Docker** & **Docker Compose**
- **Dozzle** (Observabilidade de logs)

## 📂 Estrutura do Projeto

```
PaymentOrderSystem/
├── README.md
├── .gitignore
├── docker-compose.yml       # Orquestra gateway, auth_service, auth-db, rabbitmq e dozzle
├── auth_db/
│   └── init.sql             # Schema inicial do banco isolado de autenticação
├── auth_service/            # Worker RPC de autenticação (detalhes em auth_service/auth.md)
└── gateway/                 # Borda HTTP/REST (detalhes em gateway/gateway.md)
```

## 🚀 Como Executar Localmente via Docker
## 🚀 Como Executar Localmente via Docker
1. **Subir os containers (executa o `pytest` no build antes de iniciar)**:
   ```bash
   docker compose up -d --build
   ```

2. **URLs de Acesso**:
   - **API Gateway — Swagger UI:** `http://localhost:30000/docs`
   - **API Gateway — Healthcheck:** `http://localhost:30000/health`
   - **Dozzle (Logs em Tempo Real):** `http://localhost:8888`
   - **RabbitMQ Management UI:** `http://localhost:15672` *(usuário: `guest` / senha: `guest`)*

3. **Derrubar os containers**:
   ```bash
   docker compose down --remove-orphans
   ```
   *(Para resetar também o volume do banco `auth-db`, utilize `docker compose down -v --remove-orphans`).*

## 🧪 Como Testar o Que Já Está Implementado

### 1. Testes Automatizados
### 1. Testes Automatizados

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r gateway/requirements.txt -r gateway/requirements-dev.txt
pip install -r auth_service/requirements.txt -r auth_service/requirements-dev.txt
pytest gateway/tests auth_service/tests -v
```

### 2. Validação Ponta a Ponta via Swagger UI 
> URL: http://localhost:30000/docs

- **`GET /health`:** Retorna `200 OK` (`{"status": "ok", "service": "gateway"}`).
- **`POST /auth/register`:** Envia `name`, `email` e `password` via RPC para o `auth_service`, persiste no `auth-db` e retorna `201 Created` (ou `409 Conflict` se o e-mail já existir).
- **`POST /auth/login`:** Autentica credenciais no `auth_service` e retorna `200 OK` com `access_token` (JWT) e dados do usuário (ou `401 Unauthorized`).
- **`GET /auth/me`:** Clique no botão **Authorize** no topo do Swagger, cole o `access_token` gerado no login e execute a rota para validar o payload decodificado (`200 OK`).