# Funções pra mexer com o SQLite (banco em arquivo).
# Ainda tô aprendendo: o sqlite3 já vem com o Python, não precisa instalar nada.

import sqlite3
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    # abre ou cria o arquivo do banco.
    # se a pasta "data/" não existir, cria pra não dar erro.
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))

    # Com isso, cada linha do SELECT vira tipo um dicionário:
    # row["username"] em vez de row[0]. 
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    # Cria a tabela de usuários se ela ainda não existir.
    # IF NOT EXISTS = se já tiver, não quebra nada (dá pra rodar de novo).
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
    # Sem o commit, a criação da tabela pode não gravar de verdade.
    conn.commit()
