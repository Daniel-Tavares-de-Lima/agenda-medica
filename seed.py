# Script pra popular o banco com um usuário de teste
# Idempotente = se rodar duas vezes, não cria o usuário duplicado.
# Uso: python seed.py

import os
import sys

from dotenv import load_dotenv

# ferramenta de criptografia de senhas do Flask.
from werkzeug.security import generate_password_hash

from app.db import get_connection, init_schema

# Lê o .env (senha do usuário de teste, caminho do banco, etc.)
load_dotenv()


def seed_usuario_teste(db_path=None):
    # Se não passar o caminho, usa o do .env (ou o padrão data/agenda.db).
    db_path = db_path or os.getenv("DATABASE_PATH", "data/agenda.db")
    username = os.getenv("SEED_USERNAME", "admin")
    email = os.getenv("SEED_EMAIL", "admin@example.com")
    password = os.getenv("SEED_PASSWORD", "admin123")

    # Abre a conexão com o banco de dados
    conn = get_connection(db_path)
    try:
        # Garante que a tabela existe antes de inserir.
        init_schema(conn)

        # Já tem esse usuário? Então não faz nada.
        row = conn.execute(
            "SELECT id FROM usuarios WHERE username = ? OR email = ?",
            (username, email),
        ).fetchone() # retorna o primeiro resultado da consulta, tipo um [0] num array.
        if row:
            return

        # Nunca guardar senha em texto puro — o Werkzeug gera um hash.
        # (Ainda tô estudando hash)
        conn.execute(
            "INSERT INTO usuarios (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password)),
        )
        conn.commit()
    finally:
        # Sempre fecha a conexão, mesmo se der erro no meio.
        conn.close()


# Só roda o seed quando executar: python seed.py
# (se alguém importar este arquivo, não roda sozinho)
if __name__ == "__main__":
    try:
        seed_usuario_teste()
        print("Seed concluído.")
    except Exception as exc:
        print(f"Falha no seed: {exc}", file=sys.stderr)
        sys.exit(1)
