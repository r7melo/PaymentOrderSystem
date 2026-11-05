"""Camada HTTP: recebe a requisição, chama a ação e devolve a resposta.
Erros de domínio viram status HTTP no handler registrado em main.py."""
from fastapi import APIRouter

from app.acoes.confirmar_ordem import confirmar_ordem
from app.acoes.listar_confirmacoes import listar_confirmacoes

router = APIRouter()


@router.get("/confirmacoes")
def get_confirmacoes():
    return listar_confirmacoes()


@router.post("/confirmacoes/{order_id}/confirmar")
def post_confirmar(order_id: str):
    return confirmar_ordem(order_id)
