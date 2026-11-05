"""Acesso aos dados: só SQL. Cada função recebe um cursor, então quem chama
(a camada de serviço) decide o que entra na mesma transação."""


def debitar_master(cur, codigo: str, centavos: int) -> bool:
    cur.execute(
        "UPDATE conta_master SET saldo_centavos = saldo_centavos - %s WHERE codigo = %s",
        (centavos, codigo),
    )
    return cur.rowcount == 1


def creditar_consumer(cur, codigo: str, centavos: int) -> bool:
    cur.execute(
        "UPDATE conta_consumer SET saldo_centavos = saldo_centavos + %s WHERE codigo = %s",
        (centavos, codigo),
    )
    return cur.rowcount == 1


def buscar_conta(cur, codigo: str):
    """Procura o código nas duas tabelas. Devolve None se não existir."""
    cur.execute(
        """
        SELECT 'master' AS tipo, saldo_centavos FROM conta_master WHERE codigo = %s
        UNION ALL
        SELECT 'consumer', saldo_centavos FROM conta_consumer WHERE codigo = %s
        """,
        (codigo, codigo),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {"tipo": row[0], "saldo_centavos": row[1]}


def listar_vinculos(cur) -> list:
    cur.execute(
        """
        SELECT m.codigo, c.codigo
        FROM vinculo_master_consumer v
        JOIN conta_master m   ON m.id = v.master_id
        JOIN conta_consumer c ON c.id = v.consumer_id
        ORDER BY m.codigo, c.codigo
        """
    )
    return [{"master": r[0], "consumer": r[1]} for r in cur.fetchall()]