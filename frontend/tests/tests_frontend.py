from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirects_to_login_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Entrar" in response.text


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200
    assert "login-form" in response.text


def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200
    assert "register-form" in response.text


def test_dashboard_page():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "saldo-valor" in response.text
    assert "logout-btn" in response.text