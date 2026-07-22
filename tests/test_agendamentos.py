# Testes da rota /api/agendamentos
# usei patch pra fingir a resposta da mock_api sem precisar subir o servidor

from unittest.mock import patch

import requests


# faz login nos testes pra ganhar a sessão (cookie).
def _login(client):
    return client.post(
        "/login",
        data={"identifier": "admin", "password": "admin123"},
        follow_redirects=False,
    )


# Se a mock_api estiver fora (ConnectionError), a rota deve
# responder 502 com erro = api_indisponivel.
def test_api_indisponivel_retorna_502(client):
    _login(client)
    # Finge que a API caiu (ConnectionError)
    with patch(
        "app.services.api_client.requests.get",
        side_effect=requests.ConnectionError("down"),
    ):
        resp = client.get("/api/agendamentos")
    assert resp.status_code == 502
    data = resp.get_json()
    assert data["success"] is False
    assert data["erro"] == "api_indisponivel"


# Se a pessoa buscar um texto que não existe, a lista vem vazia
# e o motivo deve ser sem_resultado_busca (não agenda_vazia).
def test_busca_sem_correspondencia(client):
    _login(client)
    sample = [
        {
            "paciente": "Maria Silva",
            "cpf": "123.456.789-00",
            "medico": "Dr. João Souza",
            "especialidade": "Clínico Geral",
            "data": "2026-07-22",
            "horario": "09:00",
            "convenio": "Unimed",
            "status": "Confirmado",
        }
    ]
    with patch("app.services.api_client.requests.get") as mocked:
        mocked.return_value.status_code = 200
        mocked.return_value.json.return_value = sample
        mocked.return_value.raise_for_status = lambda: None
        resp = client.get("/api/agendamentos", query_string={"q": "XYZINEXISTENTE"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["agendamentos"] == []
    assert data["motivo"] == "sem_resultado_busca"


# Sem estar logado, /api/agendamentos não pode devolver dados 
# tem que ser 401 com erro = nao_autenticado.
def test_sem_sessao_api_401(client):
    resp = client.get("/api/agendamentos")
    assert resp.status_code == 401
    assert resp.get_json()["erro"] == "nao_autenticado"
