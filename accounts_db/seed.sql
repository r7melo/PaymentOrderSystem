-- Dados padrão SÓ PARA TESTES (mesmos códigos que o frontend já usa).
-- Depende do 01_schema.sql, por isso o prefixo 02 (o Postgres executa em ordem alfabética).
-- Não monte este arquivo em produção.

INSERT INTO conta_master (codigo, nome, saldo_centavos)
VALUES ('PAGADOR_1', 'Conta Master de Teste', 100000)       -- R$ 1000,00
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO conta_consumer (codigo, nome, saldo_centavos)
VALUES ('RECEBEDOR_1', 'Conta Consumer de Teste', 10000)    -- R$ 100,00
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO vinculo_master_consumer (master_id, consumer_id)
SELECT m.id, c.id
FROM conta_master m, conta_consumer c
WHERE m.codigo = 'PAGADOR_1' AND c.codigo = 'RECEBEDOR_1'
ON CONFLICT DO NOTHING;