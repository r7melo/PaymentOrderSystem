"""Acesso aos dados: só SQL. Cada função recebe um cursor, então quem chama
(as ações) decide o que entra na mesma transação. Valores ficam em centavos."""

COLUNAS_ORDEM = ("id", "pagador", "recebedor", "valor_centavos", "status")


def inserir_ordem(cur, ordem_id: str, pagador: str, recebedor: str, valor_centavos: int, status: str):
    cur.execute(
        """
        INSERT INTO ordem (id, pagador, recebedor, valor_centavos, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (ordem_id, pagador, recebedor, valor_centavos, status),
    )


def listar_ordens(cur) -> list:
    cur.execute(
        f"SELECT {', '.join(COLUNAS_ORDEM)} FROM ordem ORDER BY criada_em, id"
    )
    return [dict(zip(COLUNAS_ORDEM, linha)) for linha in cur.fetchall()]
