# API "simulada" dos agendamentos.
# O app web vai chamar GET /agendamentos daqui.
# MOCK_MODE muda o comportamento pra testar os erros depois.

import os
import time

from flask import Flask, Response, jsonify

# Dois agendamentos de exemplo com todos os campos que o desafio pede
SAMPLE = [
    {
        "paciente": "Maria Silva",
        "cpf": "123.456.789-00",
        "medico": "Dr. João Souza",
        "especialidade": "Clínico Geral",
        "data": "2026-07-22",
        "horario": "09:00",
        "convenio": "Unimed",
        "status": "Confirmado",
    },
    {
        "paciente": "Pedro Alves",
        "cpf": "987.654.321-00",
        "medico": "Dra. Ana Costa",
        "especialidade": "Cardiologia",
        "data": "2026-07-23",
        "horario": "14:30",
        "convenio": "Particular",
        "status": "Pendente",
    },
]


def create_app():
    app = Flask(__name__)

    @app.get("/agendamentos")
    def agendamentos():
        # Le o modo da variável de ambiente (padrão = ok)
        mode = os.getenv("MOCK_MODE", "ok").lower()

        if mode == "slow":
            # Demora de propósito => o cliente HTTP pode dar Timeout
            segundos = float(os.getenv("MOCK_SLOW_SECONDS", "5"))
            time.sleep(segundos)
            return jsonify(SAMPLE)

        if mode == "empty":
            # Lista vazia (agenda sem nada)
            return jsonify([])

        if mode == "invalid":
            # JSON válido, mas formato errado (não é uma lista)
            return jsonify({"erro": "formato_errado"})

        if mode == "malformed":
            # Texto que NÃO é JSON válido (quebra o .json() do requests)
            return Response("{nao-json", status=200, mimetype="application/json")

        # mode == "ok" (ou qualquer outra coisa desconhecida)
        return jsonify(SAMPLE)

    return app
