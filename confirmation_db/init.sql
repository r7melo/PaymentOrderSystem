-- Schema do banco de confirmações (PostgreSQL): só estrutura, nenhum dado.
-- Executado pelo container do Postgres UMA vez, quando o volume está vazio
-- (via /docker-entrypoint-initdb.d). O serviço de confirmação não conhece este arquivo.
-- Valores em CENTAVOS (BIGINT), igual ao banco de contas.

CREATE TABLE IF NOT EXISTS ordem_confirmacao (
    id             TEXT        PRIMARY KEY,   -- mesmo id da ordem recebida no evento ORDEM_CRIADA
    pagador        TEXT        NOT NULL,
    recebedor      TEXT        NOT NULL,
    valor_centavos BIGINT      NOT NULL,
    status         TEXT        NOT NULL,      -- CRIADA -> CONFIRMADA
    recebida_em    TIMESTAMPTZ NOT NULL DEFAULT now()
);
