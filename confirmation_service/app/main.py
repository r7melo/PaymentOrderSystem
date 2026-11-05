"""Ponto de entrada: monta a aplicação e liga as peças. Sem regra de negócio aqui."""
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import database
from app.consumer import start_confirmation_consumer
from app.erros import ErroDeNegocio
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.iniciar_pool()  # antes do consumidor, que grava no banco
    threading.Thread(target=start_confirmation_consumer, daemon=True).start()
    yield
    database.fechar_pool()


app = FastAPI(title="Serviço de Confirmação de Ordens", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(ErroDeNegocio)
async def erro_de_negocio_handler(request, exc: ErroDeNegocio):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensagem})
