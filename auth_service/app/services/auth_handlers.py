from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User


async def handle_register(session: AsyncSession, payload: dict) -> dict:
    name = payload.get("name", "").strip()
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    if not name or not email or not password:
        return {"status": 400, "error": "Nome, e-mail e senha são obrigatórios."}

    existing = await session.scalar(select(User).where(User.email == email))
    if existing:
        return {"status": 409, "error": "E-mail já cadastrado."}

    try:
        pwd_hash = hash_password(password)
    except ValueError as exc:
        return {"status": 400, "error": str(exc)}

    user = User(name=name, email=email, password_hash=pwd_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
        "status": 201,
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


async def handle_login(session: AsyncSession, payload: dict) -> dict:
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    user = await session.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        return {"status": 401, "error": "E-mail ou senha inválidos."}

    token = create_access_token(user_id=user.id, email=user.email, name=user.name)
    return {
        "status": 200,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
        },
    }


async def dispatch_action(session: AsyncSession, action: str, payload: dict) -> dict:
    if action == "register":
        return await handle_register(session, payload)
    if action == "login":
        return await handle_login(session, payload)
    return {"status": 400, "error": f"Ação desconhecida: {action}"}