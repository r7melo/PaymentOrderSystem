"""Regras de negócio reservadas ao usuário para a criação de ordens.
Retorne True para aceitar ou False para rejeitar (a ação levanta a exceção)."""
import logging


class TRA:
    @staticmethod
    def validar_ordem(pagador: str, recebedor: str, valor: float) -> bool:
        # Espaço reservado para implementação de regras de negócio
        logging.info(f"[TRA] Validando ordem de {pagador} para {recebedor} no valor de {valor}")
        return True
