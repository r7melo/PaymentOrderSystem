"""Regras de negócio reservadas ao usuário para a confirmação de ordens.
Retorne True para permitir a confirmação ou False para rejeitá-la."""
import logging


class TRA:
    @staticmethod
    def validar_confirmacao(order_data: dict) -> bool:
        # Espaço reservado para verificação se o usuário pode confirmar ou não
        logging.info(f"[TRA] Validando se o usuário pode confirmar a ordem {order_data.get('id')}")
        return True
