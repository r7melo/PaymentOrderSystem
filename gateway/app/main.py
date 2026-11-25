from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.rpc_client import rpc_client
from app.entrypoints.api.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await rpc_client.connect()
    yield
    await rpc_client.close()


app = FastAPI(title="PaymentOrderSystem API Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}