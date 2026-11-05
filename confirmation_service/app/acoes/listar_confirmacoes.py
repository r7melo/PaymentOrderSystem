"""Ação: listar as ordens aguardando confirmação (inclui as já confirmadas,
para a tela mostrar o status de cada uma)."""
from app import repository
from app.database import transacao
from app.formatacao import linha_para_ordem


def listar_confirmacoes() -> list:
    with transacao() as cur:
        linhas = repository.listar_ordens(cur)
    return [linha_para_ordem(linha) for linha in linhas]
