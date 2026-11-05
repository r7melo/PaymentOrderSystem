-- Schema do banco de ordens (PostgreSQL): só estrutura, nenhum dado.
-- Executado pelo container do Postgres UMA vez, quando o volume está vazio
-- (via /docker-entrypoint-initdb.d). O serviço de ordens não conhece este arquivo.
-- Valores em CENTAVOS (BIGINT), igual ao banco de contas.

CREATE TABLE IF NOT EXISTS ordem (
    id             TEXT        PRIMARY KEY,   -- 8 caracteres gerados pelo serviço
    pagador        TEXT        NOT NULL,
    recebedor      TEXT        NOT NULL,
    valor_centavos BIGINT      NOT NULL,
    status         TEXT        NOT NULL,      -- CRIADA (a confirmação é controlada pelo serviço de confirmação)
    criada_em      TIMESTAMPTZ NOT NULL DEFAULT now()
);
