"""Camada HTTP: recebe a requisição, chama o serviço e devolve a resposta.
Erros de domínio viram status HTTP no handler registrado em main.py."""
from fastapi import APIRouter

from app import service

router = APIRouter()


@router.get("/contas/{codigo}")
def get_saldo(codigo: str):
    return service.consultar_saldo(codigo)


@router.get("/vinculos")
def list_vinculos():
    return service.listar_vinculos()