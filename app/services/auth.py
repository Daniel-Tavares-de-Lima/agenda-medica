# Aqui fica a lógica de validação para saber se o login e senha existem no banco

import logging
import sqlite3

from werkzeug.security import check_password_hash

from app.db import get_connection

logger = logging.getLogger(__name__)


def authenticate(db_path, identifier, password):
    
    # Procura o usuário pelo username ou pelo e-mail
    # se a senha bater com o hash, devolve um dicionário com id/username/email.
    # se der errado, devolve None.
    
    identifier = (identifier or "").strip()
    if not identifier or password is None:
        return None

    try:
        conn = get_connection(db_path)
    except sqlite3.Error:
        # Mensagem dizendo que deu problema para abrir o banco
        logger.exception("Não consegui abrir o banco no login")
        raise

    try:
        # O ? é pra não montar SQL com texto cru (evita SQL injection).
        # passei o mesmo valor duas vezes: uma pro username, outra pro email
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM usuarios "
            "WHERE username = ? OR email = ?",
            (identifier, identifier),
        ).fetchone()

        if row is None:
            logger.warning("Login falhou: usuário não encontrado")
            return None

        # check_password_hash compara a senha digitada com o hash salvo
        if check_password_hash(row["password_hash"], password):
            logger.warning("Login falhou: senha inválida (user_id=%s)", row["id"])
            return None

        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
        }
    finally:
        conn.close()
