"""Ação: receber uma ordem criada e deixá-la aguardando confirmação.
Disparada pelo consumidor da fila payment_orders (evento ORDEM_CRIADA)."""
import logging

from app import repository
from app.database import transacao


def receber_ordem(data: dict):
    with transacao() as cur:
        inserida = repository.inserir_se_nao_existir(
            cur,
            ordem_id=data["id"],
            pagador=data["pagador"],
            recebedor=data["recebedor"],
            valor_centavos=round(float(data["valor"]) * 100),
            status=data.get("status", "CRIADA"),
        )
    if inserida:
        logging.info(f"Ordem {data['id']} recebida para aguardar confirmação.")
