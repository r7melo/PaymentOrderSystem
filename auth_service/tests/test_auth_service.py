import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.database import Base
from app.services.auth_handlers import dispatch_action


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


async def test_register_e_login_sucesso(db_session):
    res_reg = await dispatch_action(
        db_session,
        "register",
        {"name": "Antônio Romário", "email": "romario@ufc.br", "password": "Senha123!"},
    )
    assert res_reg["status"] == 201
    assert res_reg["data"]["email"] == "romario@ufc.br"
    assert "password" not in res_reg["data"]

    res_login = await dispatch_action(
        db_session,
        "login",
        {"email": "romario@ufc.br", "password": "Senha123!"},
    )
    assert res_login["status"] == 200
    assert "access_token" in res_login["data"]


async def test_register_email_duplicado(db_session):
    payload = {"name": "Romário", "email": "dup@ufc.br", "password": "Senha123!"}
    await dispatch_action(db_session, "register", payload)
    res_dup = await dispatch_action(db_session, "register", payload)
    assert res_dup["status"] == 409


async def test_login_senha_incorreta(db_session):
    await dispatch_action(
        db_session,
        "register",
        {"name": "Romário", "email": "teste@ufc.br", "password": "Senha123!"},
    )
    res = await dispatch_action(
        db_session,
        "login",
        {"email": "teste@ufc.br", "password": "Errada!"},
    )
    assert res["status"] == 401