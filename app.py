import os
from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error_msg

app = Flask(__name__)

db = SQL("sqlite:///rascore.db")

#Flask session configuracoes
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def hello_world():
    print("Hello World")
    message = "pAGINA iNICIAL INDEX..."
    return render_template("error_msg.html", message=message)

@app.route("/login", methods=["POST", "GET"])
def login():
    #limpar dados de sessao anterior
    session.clear()

    if request.method == "POST":

        username = form.request.get("username")
        if not username:
            return error_msg("Usuário não informado.", 403)
        password = form.request.get("password")
        if not password:
            return error_msg("Senha não informada.", 403)
        re_password = form.request.get("re_password")
        if not re_password:
            return error_msg("Repita a Senha para confirmar.", 403)
        if (password != re_password):
            return error_msg("Senhas informadas divergem entre si.", 403)

        # verificar se o username já existe no banco de dados
        # confirmar se a senha confere com a senha repetida

        # gerar o hash pra senha informada
        hash_password = generate_password_hash(password, method='scrypt', salt_length=16)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", "Edu", hash_password)


        return redirect("/")

    else:
        return render_template("login.html")
