"""Ação: listar as ordens criadas."""
from app import repository
from app.database import transacao


def listar_ordens() -> list:
    with transacao() as cur:
        linhas = repository.listar_ordens(cur)
    return [
        {
            "id": linha["id"],
            "pagador": linha["pagador"],
            "recebedor": linha["recebedor"],
            "valor": linha["valor_centavos"] / 100,
            "status": linha["status"],
        }
        for linha in linhas
    ]
