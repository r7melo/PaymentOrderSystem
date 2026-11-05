"""Ação: criar uma ordem de pagamento.

Grava a ordem e publica ORDEM_CRIADA na MESMA transação: se a publicação
falhar, a ordem não fica gravada (ou o banco e a fila ficam de acordo, ou nada acontece)."""
import logging
import uuid

from app import publisher, repository
from app.config import PAYMENT_ORDERS_QUEUE
from app.database import transacao
from app.erros import ErroMensageriaError, OrdemRejeitadaError
from app.tra import TRA


def criar_ordem(pagador: str, recebedor: str, valor: float) -> dict:
    if not TRA.validar_ordem(pagador, recebedor, valor):
        raise OrdemRejeitadaError("Ordem rejeitada pela classe TRA.")

    ordem = {
        "id": str(uuid.uuid4())[:8],
        "pagador": pagador,
        "recebedor": recebedor,
        "valor": valor,
        "status": "CRIADA",
    }

    with transacao() as cur:
        repository.inserir_ordem(
            cur,
            ordem_id=ordem["id"],
            pagador=pagador,
            recebedor=recebedor,
            valor_centavos=round(valor * 100),
            status=ordem["status"],
        )
        try:
            publisher.publicar(PAYMENT_ORDERS_QUEUE, "ORDEM_CRIADA", ordem)
        except Exception as e:
            raise ErroMensageriaError("Erro de mensageria") from e  # desfaz o INSERT

    logging.info(f"Ordem {ordem['id']} criada e enviada ao RabbitMQ: {ordem}")
    return ordem
