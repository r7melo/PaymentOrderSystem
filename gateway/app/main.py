from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.rpc_client import rpc_client
from app.entrypoints.api.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rpc_client.connect()
    yield
    await rpc_client.close()


app = FastAPI(title="PaymentOrderSystem API Gateway", lifespan=lifespan)
app.include_router(auth_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}