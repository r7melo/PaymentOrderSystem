# PaymentOrderSystem

Sistema distribuído de ordens de pagamento baseado em microsserviços orientados a eventos e chamadas **RPC assíncronas via RabbitMQ**.

Atualmente, a camada de entrada (**API Gateway**), a infraestrutura de mensageria (**RabbitMQ**), o monitoramento de logs (**Dozzle**) e a pipeline de testes automatizados (**Quality Gate no Docker Build**) estão implementados e validados.

## 📐 Arquitetura Atual

```
[ Cliente HTTP / Swagger UI ]
              │  HTTP / REST + JWT (Bearer Token)
              ▼
[ API Gateway (FastAPI - Porta 30000) ]
              │  AMQP RPC (correlation_id + reply_to)
              ▼
[ RabbitMQ Message Broker (Porta 5672 / UI 15672) ]
              │
              └──► Fila: rpc.auth.requests

[ Dozzle (Porta 8888) ] ──► Monitoramento de logs dos containers em tempo real
```

### Componentes em Funcionamento

1. **API Gateway (`gateway/`)**:
   * Única borda HTTP/REST do sistema (`http://localhost:30000`).
   * Valida contratos de entrada/saída com **Pydantic v2** e verifica tokens **JWT** (`GET /auth/me`).
   * Traduz requisições HTTP (`POST /auth/register`, `POST /auth/login`) em chamadas **RPC assíncronas via RabbitMQ** (`aio-pika`), gerenciando `correlation_id`, fila de retorno exclusiva (`reply_to`) e timeout (`504 Gateway Timeout` após `5.0s` sem worker ativo).
   * Possui *Multi-stage Dockerfile* com **Quality Gate**: executa `pytest -v` automaticamente durante o build antes de gerar a imagem final.
   * Documentação detalhada em [`gateway/gateway.md`](gateway/gateway.md).

2. **RabbitMQ (`rabbitmq`)**:
   * Broker AMQP (`5672`) com painel de gerenciamento web (`http://localhost:15672`) e *healthcheck* configurado no Docker Compose.

3. **Dozzle (`dozzle`)**:
   * Visualizador leve de logs em tempo real para todos os containers Docker (`http://localhost:8888`).

## 🛠️ Tecnologias Utilizadas

* **Python 3.12** + **FastAPI** + **Uvicorn** + **Pydantic v2**
* **RabbitMQ** + **`aio-pika`** (Cliente AMQP assíncrono / Padrão RPC)
* **PyJWT** (Validação de tokens Bearer JWT)
* **`pytest`** & **`httpx`** (Testes automatizados e *Quality Gate* no Docker)
* **Docker** & **Docker Compose**
* **Dozzle** (Observabilidade de logs)

## 📂 Estrutura do Projeto

```
PaymentOrderSystem/
├── README.md
├── .gitignore
├── docker-compose.yml       # Orquestra gateway, rabbitmq e dozzle
└── gateway/                 # Borda HTTP/REST (detalhes em gateway/gateway.md)
```

## 🚀 Como Executar Localmente via Docker
1. **Subir os containers (executa o `pytest` no build antes de iniciar)**:
   ```bash
   docker compose up -d --build
   ```

2. **URLs de Acesso**:
   * **API Gateway — Swagger UI:** `http://localhost:30000/docs`
   * **API Gateway — Healthcheck:** `http://localhost:30000/health`
   * **Dozzle (Logs em Tempo Real):** `http://localhost:8888`
   * **RabbitMQ Management UI:** `http://localhost:15672` *(usuário: `guest` / senha: `guest`)*

3. **Derrubar os containers**:
   ```bash
   docker compose down --remove-orphans
   ```

## 🧪 Como Testar o Que Já Está Implementado

### 1. Testes Automatizados

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r gateway/requirements.txt -r gateway/requirements-dev.txt
cd gateway && pytest -v
```

### 2. Validação Ponta a Ponta via Swagger UI 
> URL: http://localhost:30000/docs

* **`GET /health`:** Retorna `200 OK` (`{"status": "ok", "service": "gateway"}`).
* **`POST /auth/register` e `POST /auth/login`:** Validam o JSON de entrada, publicam a mensagem RPC na fila `rpc.auth.requests` do RabbitMQ e retornam `504 Gateway Timeout` após `5.0s` (comportamento esperado enquanto não houver worker ativo na fila).
* **`GET /auth/me`:** Valida a presença e assinatura do cabeçalho `Authorization: Bearer <token>` (`401`/`403` sem token válido).
