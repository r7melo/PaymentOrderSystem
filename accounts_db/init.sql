-- Schema do banco de contas (PostgreSQL): só estrutura, nenhum dado.
-- Executado pelo container do Postgres UMA vez, quando o volume está vazio
-- (via /docker-entrypoint-initdb.d, em ordem alfabética). O serviço de contas não conhece este arquivo.
-- Saldos em CENTAVOS (BIGINT) para evitar erro de arredondamento com dinheiro.

CREATE TABLE IF NOT EXISTS conta_master (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo         TEXT    NOT NULL UNIQUE,      -- identificador de negócio (o que o frontend usa)
    nome           TEXT    NOT NULL,
    saldo_centavos BIGINT  NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS conta_consumer (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo         TEXT    NOT NULL UNIQUE,
    nome           TEXT    NOT NULL,
    saldo_centavos BIGINT  NOT NULL DEFAULT 0
);

-- Relação N:N entre master e consumer.
CREATE TABLE IF NOT EXISTS vinculo_master_consumer (
    master_id   INTEGER NOT NULL REFERENCES conta_master(id)   ON DELETE CASCADE,
    consumer_id INTEGER NOT NULL REFERENCES conta_consumer(id) ON DELETE CASCADE,
    PRIMARY KEY (master_id, consumer_id)
);