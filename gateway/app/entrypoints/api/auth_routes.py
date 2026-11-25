from fastapi import APIRouter, Depends, HTTPException
from app.core.rpc_client import rpc_client
from app.core.security import get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    res = await rpc_client.call("rpc.auth.requests", "register", body.model_dump())
    if res["status"] >= 400:
        raise HTTPException(status_code=res["status"], detail=res["error"])
    return res["data"]


@router.post("/login")
async def login(body: LoginRequest):
    res = await rpc_client.call("rpc.auth.requests", "login", body.model_dump())
    if res["status"] >= 400:
        raise HTTPException(status_code=res["status"], detail=res["error"])
    return res["data"]


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": user}
