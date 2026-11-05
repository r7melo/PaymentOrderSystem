"""Acesso aos dados: só SQL. Cada função recebe um cursor, então quem chama
(as ações) decide o que entra na mesma transação. Valores ficam em centavos."""

COLUNAS_ORDEM = ("id", "pagador", "recebedor", "valor_centavos", "status")
_SELECT_COLUNAS = f"SELECT {', '.join(COLUNAS_ORDEM)} FROM ordem_confirmacao"


def inserir_se_nao_existir(cur, ordem_id: str, pagador: str, recebedor: str,
                           valor_centavos: int, status: str) -> bool:
    """Grava a ordem recebida. Se o id já existir (evento reentregue), não altera nada:
    assim uma ordem já confirmada nunca volta para CRIADA. Devolve True se inseriu."""
    cur.execute(
        """
        INSERT INTO ordem_confirmacao (id, pagador, recebedor, valor_centavos, status)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (ordem_id, pagador, recebedor, valor_centavos, status),
    )
    return cur.rowcount == 1


def listar_ordens(cur) -> list:
    cur.execute(f"{_SELECT_COLUNAS} ORDER BY recebida_em, id")
    return [dict(zip(COLUNAS_ORDEM, linha)) for linha in cur.fetchall()]


def buscar_ordem_para_atualizar(cur, ordem_id: str):
    """Busca a ordem travando a linha (FOR UPDATE), para que dois cliques
    simultâneos em 'confirmar' não passem os dois pela checagem de status."""
    cur.execute(f"{_SELECT_COLUNAS} WHERE id = %s FOR UPDATE", (ordem_id,))
    linha = cur.fetchone()
    return None if linha is None else dict(zip(COLUNAS_ORDEM, linha))


def atualizar_status(cur, ordem_id: str, status: str):
    cur.execute("UPDATE ordem_confirmacao SET status = %s WHERE id = %s", (status, ordem_id))
