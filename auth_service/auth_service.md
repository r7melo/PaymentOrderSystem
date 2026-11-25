# Auth Service (`auth_service`)

Microsserviço responsável pela identidade dos usuários, persistência de credenciais com hash seguro (`bcrypt`) e emissão de tokens JWT (`HS256`).

## Arquitetura e Comunicação

* **Padrão de Comunicação:** Worker assíncrono (`aio-pika`) sem portas HTTP expostas, consumindo requisições RPC da fila durável `rpc.auth.requests`.
* **Persistência Isolada:** Banco PostgreSQL 16 (`auth-db`), inicializado explicitamente via `auth_db/init.sql`.
* **Quality Gate:** Build multi-stage no `Dockerfile` que executa a suíte `pytest` (com SQLite assíncrono em memória) antes de gerar a imagem final.

## Contrato RPC (`rpc.auth.requests`)

| Ação (`action`) | Payload Esperado | Retorno de Sucesso | Erros Tratados |
| :--- | :--- | :--- | :--- |
| `register` | `{"name", "email", "password"}` | `201` (`id`, `name`, `email`) | `400` (campos inválidos ou senha > 72 bytes), `409` (e-mail duplicado) |
| `login` | `{"email", "password"}` | `200` (`access_token`, `token_type`, `user`) | `401` (credenciais inválidas) |

## Schema do Banco (`auth_db/init.sql`)

* **Tabela `users`:**
  * `id` (`SERIAL PRIMARY KEY`)
  * `name` (`VARCHAR(120) NOT NULL`)
  * `email` (`VARCHAR(255) NOT NULL UNIQUE`, com índice `idx_users_email`)
  * `password_hash` (`VARCHAR(255) NOT NULL`)
  * `created_at` (`TIMESTAMPTZ NOT NULL DEFAULT NOW()`)