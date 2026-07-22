# Rotas = endereços da aplicação (/login, /agenda, etc.).
# Blueprint é um jeito do Flask de agrupar rotas pra depois plugar no app

import logging
import sqlite3
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

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
    # Por enquanto só um stub (placeholder). Tabulator entra depois.
    return render_template("agenda.html", username=session.get("username"))
