"""Conversão entre o formato do banco (centavos) e o formato da API (reais)."""


def linha_para_ordem(linha: dict) -> dict:
    return {
        "id": linha["id"],
        "pagador": linha["pagador"],
        "recebedor": linha["recebedor"],
        "valor": linha["valor_centavos"] / 100,
        "status": linha["status"],
    }
