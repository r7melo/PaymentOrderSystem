"""Camada HTTP: recebe a requisição, chama a ação e devolve a resposta.
Erros de domínio viram status HTTP no handler registrado em main.py."""
from fastapi import APIRouter
from pydantic import BaseModel

from app.acoes.criar_ordem import criar_ordem
from app.acoes.listar_ordens import listar_ordens

router = APIRouter()


class OrdemRequest(BaseModel):
    pagador: str
    recebedor: str
    valor: float


@router.post("/ordens")
def post_ordem(ordem: OrdemRequest):
    return criar_ordem(ordem.pagador, ordem.recebedor, ordem.valor)


@router.get("/ordens")
def get_ordens():
    return listar_ordens()
