import os
from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error_msg, login_required

app = Flask(__name__)

db = SQL("sqlite:///rascore.db")

#Flask session configuracoes
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/register", methods=["POST", "GET"])
def register():
    #limpar dados de sessao anterior
    session.clear()

    if request.method == "POST":

        username = request.form.get("username").lower()
        if not username:
            return error_msg("Usuário não informado.", 403)
        password = request.form.get("password")
        if not password:
            return error_msg("Senha não informada.", 403)
        re_password = request.form.get("re_password")
        if not re_password:
            return error_msg("Repita a Senha para confirmar.", 403)
        if (password != re_password):
            return error_msg("Senhas informadas divergem entre si.", 403)

        # verificar se o username já existe no banco de dados
        # confirmar se a senha confere com a senha repetida

        # gerar o hash pra senha informada
        hash_password = generate_password_hash(password, method='scrypt', salt_length=16)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)


        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username").lower()
        if not username:
            return error_msg("Usuário não foi informado...")
        look_username = db.execute("SELECT * FROM users WHERE username = ?", username)
        print(look_username)
        if not look_username:
            return error_msg("Nome de usuário não encontrado.")

        password = request.form.get("password")
        print(password)
        if not password:
            return error_msg("Não foi informada a senha...")
        if not check_password_hash(look_username[0]['hash'], password):
            return error_msg("Senha incorreta.")

        #gravar na sessao user autenticado

        session["user_id"] = look_username[0]["id"]
        print("usuario autenticado")

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
@login_required
def hello_world():
    print("Hello World")
    message = "pAGINA iNICIAL INDEX..."
    return render_template("error_msg.html", message=message)

@app.route("/perfil")
@login_required
def perfil():
    user_id = session['user_id']
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    # user_data = get_user_data[0]
    print(user_data)
    return render_template("perfil.html", user_data=user_data[0])

@app.route("/select", methods = ["GET", "POST"])
@login_required
def select():
    if request.method == "POST":
        return "POST"

    else:
        return render_template("select.html")
