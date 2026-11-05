"""Ponto de entrada: monta a aplicação e liga as peças. Sem regra de negócio aqui."""
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import database
from app.consumer import start_accounts_consumer
from app.routes import router
from app.service import ContaNaoEncontradaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.iniciar_pool()  # antes do consumidor, que depende do banco
    threading.Thread(target=start_accounts_consumer, daemon=True).start()
    yield
    database.fechar_pool()


app = FastAPI(title="Serviço de Gestão de Contas", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(ContaNaoEncontradaError)
async def conta_nao_encontrada_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Conta não encontrada"})