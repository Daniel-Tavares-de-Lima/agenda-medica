# Fixtures do pytest = preparação que roda antes dos testes
# Assim cada teste ganha um app e um banco limpinho

import os

import pytest

from app import create_app
from seed import seed_usuario_teste


@pytest.fixture()
def app(tmp_path):
    # tmp_path = pasta temporária que o pytest cria só pra esse teste
    # Assim não bagunça o data/agenda.db de verdade
    db_path = tmp_path / "test.db"

    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "DATABASE_PATH": str(db_path),
            "MOCK_API_URL": "http://mock.test",
            "API_TIMEOUT": 1,
        }
    )

    # O seed também lê essas variáveis de ambiente
    os.environ["DATABASE_PATH"] = str(db_path)
    os.environ["SEED_USERNAME"] = "admin"
    os.environ["SEED_EMAIL"] = "admin@example.com"
    os.environ["SEED_PASSWORD"] = "admin123"

    seed_usuario_teste(str(db_path))
    yield application


@pytest.fixture()
def client(app):
    # Cliente de teste do Flask: dá pra fazer GET/POST sem abrir o navegador
    return app.test_client()
