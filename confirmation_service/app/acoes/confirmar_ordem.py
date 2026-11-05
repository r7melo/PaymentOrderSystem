"""Ação: confirmar uma ordem pendente.

Trava a linha, valida a regra TRA, marca como CONFIRMADA e publica ORDEM_CONFIRMADA
na MESMA transação: se a publicação falhar, a confirmação é desfeita."""
import logging

from app import publisher, repository
from app.config import CONFIRMED_ORDERS_QUEUE
from app.database import transacao
from app.erros import (
    ErroMensageriaError,
    OrdemJaConfirmadaError,
    OrdemNaoEncontradaError,
    OrdemRejeitadaError,
)
from app.formatacao import linha_para_ordem
from app.tra import TRA


def confirmar_ordem(ordem_id: str) -> dict:
    with transacao() as cur:
        linha = repository.buscar_ordem_para_atualizar(cur, ordem_id)
        if linha is None:
            raise OrdemNaoEncontradaError("Ordem não encontrada")

        # Evita confirmar duas vezes: sem isso a conta seria debitada de novo.
        if linha["status"] == "CONFIRMADA":
            raise OrdemJaConfirmadaError("Ordem já confirmada")

        ordem = linha_para_ordem(linha)
        if not TRA.validar_confirmacao(ordem):
            raise OrdemRejeitadaError("Confirmação rejeitada pela regra TRA.")

        ordem["status"] = "CONFIRMADA"
        repository.atualizar_status(cur, ordem_id, "CONFIRMADA")

        try:
            publisher.publicar(CONFIRMED_ORDERS_QUEUE, "ORDEM_CONFIRMADA", ordem)
        except Exception as e:
            raise ErroMensageriaError("Erro de mensageria") from e  # desfaz a confirmação

    logging.info(f"Ordem {ordem_id} confirmada e enviada para atualização de saldo no RabbitMQ.")
    return {"status": "SUCESSO", "order": ordem}
