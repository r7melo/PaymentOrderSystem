# API Gateway — PaymentOrderSystem

O **API Gateway** é a única borda HTTP/REST do sistema. Ele recebe requisições do frontend (NiceGUI), valida payloads e tokens JWT, e traduz cada operação em chamadas **RPC síncronas via RabbitMQ** para os microsserviços internos.

---

## 1. Arquitetura e Estrutura de Pastas

```text
gateway/
├── Dockerfile               # Multi-stage build com Quality Gate (executa pytest antes de gerar a imagem final)
├── pyproject.toml           # Configuração do pytest (pythonpath = ["."])
├── requirements.txt         # Dependências de produção
├── requirements-dev.txt     # Dependências de testes (pytest, httpx)
├── gateway.md
├── tests/
│   └── test_gateway.py      # Suíte de testes unitários e de integração com mocks
└── app/
    ├── __init__.py
    ├── main.py              # Ponto de entrada FastAPI + lifespan do cliente RPC
    ├── core/
    │   ├── config.py        # Configurações via Pydantic Settings
    │   ├── rpc_client.py    # Cliente AMQP assíncrono (correlation_id + reply_to)
    │   └── security.py      # Validação de Bearer Token JWT
    ├── schemas/
    │   └── auth.py          # Contratos de entrada/saída (Pydantic)
    └── entrypoints/
        ├── __init__.py
        └── api/
            ├── __init__.py
            └── auth_routes.py   # Rotas HTTP (/auth/*)
```

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672/` | URL de conexão com o broker AMQP |
| `JWT_SECRET` | `super-secret-jwt-key-payment-system` | Chave secreta compartilhada para validar tokens JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura do JWT |
| `RPC_TIMEOUT` | `5.0` | Tempo máximo (em segundos) aguardando resposta de um worker |

---

## 2. Como Iniciar o Serviço

### Modo 1: Via Docker Compose (Ambiente Completo + Quality Gate)

Durante o build (`--build`), o estágio `tester` do `Dockerfile` roda automaticamente `pytest -v`. Se qualquer teste falhar, o build é interrompido antes de subir os containers.

Sobe o **RabbitMQ**, o **Gateway** (porta `30000`) e o **Dozzle** (logs em tempo real na porta `8888`):

```bash
docker compose up -d --build
```

**Acessos rápidos:**
- **Swagger UI (API Docs):** `http://localhost:30000/docs`
- **Healthcheck:** `http://localhost:30000/health`
- **Dozzle (Logs dos containers):** `http://localhost:8888`
- **RabbitMQ Management:** `http://localhost:15672` (`guest` / `guest`)

**Derrubar containers:**
```bash
docker compose down --remove-orphans
```

---

### Modo 2: Ambiente de Desenvolvimento Local (`venv` + Hot-Reload)

Ideal para desenvolver rápido sem reconstruir imagens Docker. Deixe apenas o `rabbitmq` rodando no Docker e execute o Gateway diretamente na máquina local:

1. **Suba apenas o RabbitMQ no Docker:**
   ```bash
   docker compose up -d rabbitmq
   ```

2. **Crie e ative o ambiente virtual na raiz do projeto:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r gateway/requirements.txt -r gateway/requirements-dev.txt
   ```

3. **Inicie o servidor Uvicorn localmente:**
   ```bash
   cd gateway
   RABBITMQ_URL="amqp://guest:guest@localhost:5672/" uvicorn app.main:app --reload --port 8000
   ```
- **Swagger local:** `http://localhost:8000/docs`

---

## 3. Como Desenvolver Novas Rotas (Fluxo RPC)

Para conectar um novo microsserviço ao Gateway (ex: `accounts_service` ou `orders_service`):

1. **Contrato (`app/schemas/<dominio>.py`):** Crie os modelos `BaseModel` do Pydantic para validar o corpo da requisição HTTP.
2. **Rota (`app/entrypoints/api/<dominio>_routes.py`):**
   - Use `user: dict = Depends(get_current_user)` nas rotas protegidas para extrair os dados do JWT (`user["sub"]`, `user["email"]`).
   - Envie a chamada RPC para a fila do serviço correspondente:
     ```python
     res = await rpc_client.call("rpc.<servico>.requests", "<acao>", payload)
     if res["status"] >= 400:
         raise HTTPException(status_code=res["status"], detail=res["error"])
     return res["data"]
     ```
3. **Registro (`app/main.py`):** Importe o `router` criado e registre com `app.include_router(...)`.

### Protocolo de Mensagem RPC (Gateway <-> Workers)

- **Requisição publicada pelo Gateway na fila `rpc.<servico>.requests`:**
  ```json
  {
    "action": "login",
    "payload": { "email": "usuario@exemplo.com", "password": "****" }
  }
  ```
- **Resposta esperada na fila exclusiva de retorno (`reply_to`, ex: `amq_...`) com o mesmo `correlation_id`:**
  ```json
  {
    "status": 200,
    "data": { ... },
    "error": "Mensagem de erro (apenas quando status >= 400)"
  }
  ```

---

## 4. Como Testar o Serviço

### A. Testes Automatizados sem Docker (`pytest` + Mocks)

Valida rotas, validação de schemas Pydantic, repasse de status HTTP (`200`, `401`, `409`, `504`) e decodificação de JWT em milissegundos, **sem precisar de RabbitMQ ou workers no ar**:

1. **Instale as dependências de teste no `.venv` (caso ainda não tenha instalado):**
   ```bash
   pip install -r gateway/requirements-dev.txt
   ```

2. **Execute a suíte de testes:**
   ```bash
   cd gateway
   pytest -v
   ```

### B. Teste de Integração com RabbitMQ (Sem Workers)

Com o `rabbitmq` e o `gateway` rodando:
1. Acesse `http://localhost:30000/docs` (ou `:8000/docs` no modo local).
2. Execute `GET /health` -> Deve retornar `200 OK` (`{"status": "ok", "service": "gateway"}`).
3. Execute `POST /auth/login` ou `POST /auth/register` com um payload válido -> O Gateway publicará a mensagem no broker e retornará **`504 Gateway Timeout`** após `5.0s` (`Nenhum worker respondeu na fila 'rpc.auth.requests' dentro de 5.0s.`), confirmando que o roteamento HTTP -> AMQP RPC está operando corretamente.