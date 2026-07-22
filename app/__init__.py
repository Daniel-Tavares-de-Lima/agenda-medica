# cria o app Flask.
# vi em vários tutoriais essa ideia de create_app() — facilita testar depois.

import logging
import os

from dotenv import load_dotenv
from flask import Flask


def create_app(test_config=None):
    # Carrega o arquivo .env  pra pegar SECRET_KEY, caminhos, etc.
    load_dotenv()

    app = Flask(__name__)

    # Configurações básicas. getenv = le variável de ambiente;
    # o segundo valor é o padrão se a variável não existir.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-inseguro")
    app.config["DATABASE_PATH"] = os.getenv("DATABASE_PATH", "data/agenda.db")
    app.config["MOCK_API_URL"] = os.getenv("MOCK_API_URL", "http://127.0.0.1:5001")
    app.config["API_TIMEOUT"] = float(os.getenv("API_TIMEOUT", "3"))

    # nos testes a gente passa um dicionário e sobrescreve essas configs.
    if test_config:
        app.config.update(test_config)

    # Logs no terminal, ajuda quando algo der errado.
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    return app
