# Testes do login — ainda sem as rotas, estes testes devem falhar (404).
# Depois que a gente criar o login, aí eles passam.

def test_login_valido_redireciona(client):
    # Usuário e senha certos → Flask manda pra /agenda (código 302 = redirect)
    resp = client.post(
        "/login",
        data={"identifier": "admin", "password": "admin123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/agenda" in resp.headers["Location"]


def test_login_valido_com_email(client):
    # O formulário aceita e-mail também (mesmo campo)
    resp = client.post(
        "/login",
        data={"identifier": "admin@example.com", "password": "admin123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_login_invalido_permanece_200(client):
    # Senha errada → fica na tela de login (200) com mensagem de erro
    resp = client.post(
        "/login",
        data={"identifier": "admin", "password": "errada"},
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert b"inv" in resp.data.lower() or b"incorret" in resp.data.lower()
