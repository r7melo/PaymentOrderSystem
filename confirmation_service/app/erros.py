"""Erros de domínio do serviço de confirmação. Cada um carrega o status HTTP que
deve ser devolvido; o handler registrado em main.py faz a conversão."""


class ErroDeNegocio(Exception):
    status_code = 400

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class OrdemNaoEncontradaError(ErroDeNegocio):
    status_code = 404


class OrdemJaConfirmadaError(ErroDeNegocio):
    status_code = 409


class OrdemRejeitadaError(ErroDeNegocio):
    status_code = 400


class ErroMensageriaError(ErroDeNegocio):
    status_code = 500
