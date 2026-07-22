# Rotas = endereços da aplicação (/login, /agenda, etc.).
# Blueprint é um jeito do Flask de agrupar rotas pra depois plugar no app

import logging
import sqlite3
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.api_client import fetch_agendamentos
from app.services.auth import authenticate

bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


def login_required_html(view):
    # "Decorador": envolve a página e só deixa entrar se tiver sessão.
    # Se não estiver logado, manda de volta pro /login.
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped


def login_required_json(view):
    # Igual ao de cima, mas pra rotas JSON (devolve 401 em vez de redirect)
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(success=False, erro="nao_autenticado"), 401
        return view(*args, **kwargs)

    return wrapped


def _filtrar_agendamentos(items, q):
    # Busca simples: olha se o texto aparece no paciente, CPF ou médico
    q = q.casefold()
    resultado = []
    for item in items:
        texto = f"{item['paciente']} {item['cpf']} {item['medico']}".casefold()
        if q in texto:
            resultado.append(item)
    return resultado


@bp.get("/")
def index():
    # Página inicial: se já logou, vai pra agenda, senão, volta pro login
    if session.get("user_id"):
        return redirect(url_for("main.agenda"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    # GET = só mostrar o formulário
    # POST = alguém clicou em Entrar e mandou os dados
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("main.agenda"))
        return render_template("login.html")

    identifier = request.form.get("identifier", "")
    password = request.form.get("password", "")

    try:
        user = authenticate(
            current_app.config["DATABASE_PATH"],
            identifier,
            password,
        )
    except sqlite3.Error:
        logger.exception("SQLite indisponível no login")
        return (
            render_template(
                "login.html",
                error="Não foi possível conectar ao banco de dados. Tente novamente.",
            ),
            503,
        )

    if user is None:
        # 200 = página normal, mas com a mensagem de erro
        return (
            render_template("login.html", error="Usuário ou senha inválidos."),
            200,
        )

    # session = lembrancinha no cookie (assinada com SECRET_KEY)
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("main.agenda"))


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/agenda")
@login_required_html
def agenda():
    # Só o HTML + Tabulator. Os dados vêm via JavaScript de /api/agendamentos
    return render_template("agenda.html", username=session.get("username"))


@bp.get("/api/agendamentos")
@login_required_json
def api_agendamentos():
    # Única rota de dados: busca na mock_api, filtra se tiver ?q=, devolve JSON
    q = (request.args.get("q") or "").strip()
    busca_aplicada = bool(q)

    result = fetch_agendamentos(
        current_app.config["MOCK_API_URL"],
        current_app.config["API_TIMEOUT"],
    )

    if not result.ok:
        return jsonify(success=False, erro=result.error_code), 502

    items = result.items
    if busca_aplicada:
        items = _filtrar_agendamentos(items, q)

    motivo = None
    if not items:
        if busca_aplicada:
            motivo = "sem_resultado_busca"
        else:
            motivo = "agenda_vazia"

    return jsonify(success=True, agendamentos=items, motivo=motivo), 200
