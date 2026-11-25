from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core import rpc_client

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "gateway"}


def test_login_sucesso(monkeypatch):
    monkeypatch.setattr(
        rpc_client.rpc_client,
        "call",
        AsyncMock(return_value={
            "status": 200,
            "data": {"access_token": "jwt-valido", "token_type": "bearer"},
        }),
    )
    resp = client.post("/auth/login", json={"email": "romario@ufc.br", "password": "1234"})
    assert resp.status_code == 200
    assert resp.json()["access_token"] == "jwt-valido"


def test_login_credenciais_invalidas(monkeypatch):
    monkeypatch.setattr(
        rpc_client.rpc_client,
        "call",
        AsyncMock(return_value={"status": 401, "error": "E-mail ou senha inválidos."}),
    )
    resp = client.post("/auth/login", json={"email": "romario@ufc.br", "password": "errada"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "E-mail ou senha inválidos."