"""Regras de negócio do serviço de contas. Não sabe de HTTP nem de RabbitMQ:
só orquestra o repositório e levanta exceções de domínio."""
from app import repository
from app.database import transacao


class ContaNaoEncontradaError(Exception):
    pass


def aplicar_ordem(pagador: str, recebedor: str, valor: float):
    """Debita o master e credita o consumer na MESMA transação:
    ou os dois acontecem, ou nenhum."""
    centavos = round(valor * 100)
    with transacao() as cur:
        if not repository.debitar_master(cur, pagador, centavos):
            raise ContaNaoEncontradaError(f"conta master '{pagador}' não existe")
        if not repository.creditar_consumer(cur, recebedor, centavos):
            raise ContaNaoEncontradaError(f"conta consumer '{recebedor}' não existe")


def consultar_saldo(codigo: str) -> dict:
    with transacao() as cur:
        conta = repository.buscar_conta(cur, codigo)
    if conta is None:
        raise ContaNaoEncontradaError(f"conta '{codigo}' não existe")
    return {"usuario": codigo, "tipo": conta["tipo"], "saldo": conta["saldo_centavos"] / 100}


def listar_vinculos() -> list:
    with transacao() as cur:
        return repository.listar_vinculos(cur)