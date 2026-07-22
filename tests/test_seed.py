# Teste do seed: cria o usuário e, se rodar de novo não duplica

from app.db import get_connection
from seed import seed_usuario_teste


def test_seed_cria_usuario(tmp_path):
    db = tmp_path / "a.db"

    seed_usuario_teste(str(db))
    seed_usuario_teste(str(db))  # segunda vez — tem que continuar com 1 usuário só

    conn = get_connection(str(db))
    rows = conn.execute("SELECT username, email FROM usuarios").fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0]["username"] == "admin"
    assert rows[0]["email"] == "admin@example.com"
