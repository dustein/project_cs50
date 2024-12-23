import os
import sqlite3
from flask import Flask, render_template, redirect, request, session, g, url_for
# from flask_session.__init__ import Session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy import create_engine, func, delete, Column, Integer, String, Text, Float, DateTime, ForeignKey
from datetime import datetime


from helpers import error_msg, login_required

#Flask session configuracoes
app = Flask(__name__, static_folder='static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# SQLAlchemy
engine = create_engine('sqlite:///rascore.db')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    hash = Column(String(255), nullable=False)

class Agenda(Base):
    __tablename__ = 'agenda'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    title = Column(String(255))
    event_start = Column(DateTime)
    event_end = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    if user_id is None:
        return redirect(url_for('login'))

    events = db_session.query(Agenda).filter(user_id == user_id).all()
    events_to_jinja = []
    for evento in events:
        novo = {
            "user_id" : evento.user_id,
            "group_id" : evento.group_id,
            "title" : evento.title,
            "event_start" : evento.event_start.strftime('%Y-%m-%d'),
            "event_end" : evento.event_start.strftime('%Y-%m-%d'),
        }
        events_to_jinja.append(novo)
    events = Agenda.query.all()

    return render_template("index.html", events = events_to_jinja)

@app.route("/register", methods=["POST", "GET"])
def register():
    #limpar dados de sessao anterior
    session.clear()

    if request.method == "POST":

        username = request.form.get("username").upper()
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

        new_user = User(username=username, hash=hash_password)
        db_session.add(new_user)
        db_session.commit()

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username").upper()
        if not username:
            return error_msg("Usuário não foi informado...")

        look_username = User.query.filter_by(username=username).first()
        print(look_username)
        if not look_username:
            return error_msg("Nome de usuário não encontrado.")

        password = request.form.get("password")
        print(password)
        if not password:
            return error_msg("Não foi informada a senha...")

        if not check_password_hash(look_username.hash, password):

            return error_msg("Senha incorreta.")

        if look_username:
            session["user_id"] = look_username.id
            session["user_name"] = look_username.username
        else:
            return error_msg("Usuário não encontrado.")

        print("usuario autenticado")

        return redirect("/")

    else:

        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/perfil")
@login_required
def perfil():
    user_id = session["user_id"]
    if user_id is None:
        return redirect(url_for('login'))

    user_data = db_session.query(User).filter(User.id == user_id).first()
    
    print(user_data)
    return render_template("perfil.html", user_data=user_data)

@app.route("/select", methods = ["GET", "POST"])
@login_required
def select():
    user_id = session["user_id"]
    if user_id is None:
        return redirect(url_for('login'))

    events = db_session.query(Agenda).filter(user_id == user_id).all()
    events_to_jinja = []
    for evento in events:
        novo = {
            "user_id" : evento.user_id,
            "group_id" : evento.group_id,
            "title" : evento.title,
            "event_start" : evento.event_start.strftime('%Y-%m-%d'),
            "event_end" : evento.event_start.strftime('%Y-%m-%d'),
        }
        events_to_jinja.append(novo)

    print(events_to_jinja)

    if request.method == "POST":
        user_data = db_session.query(User).filter(User.id == user_id).first()
        group_id = user_id
        selected_date = request.form.get("selected_date")
        title = user_data.username
        event_start = event_end = selected_date
        print(user_id, group_id, title, event_start, event_end)
        
        def insert_event(group_id, title, event_start, event_end, user_id):
            new_event = Agenda(
                group_id=group_id,
                title=title,
                event_start=datetime.strptime(event_start, '%Y-%m-%d'),
                event_end=datetime.strptime(event_end, '%Y-%m-%d'),
                user_id=user_id
            )
            db_session.add(new_event)
            db_session.commit()
            
        insert_event(group_id, title, event_start, event_end, user_id)
        
        return redirect("/select")

    else:

        return render_template("select.html", events = events_to_jinja)

@app.route("/cancel", methods = ["GET", "POST"])
@login_required
def cancel():
    user_id = session["user_id"]
    # mes_hoje = datetime.today().strftime('%m')
    # mes_seguinte = int(mes_hoje) + 1
    # if (mes_seguinte > 12):
    #     mes_seguinte = "01"
    current_dateTime = datetime.now()

    datas = db_session.query(Agenda).filter(Agenda.user_id == user_id, Agenda.event_start > current_dateTime)
    events_to_jinja = []
    for evento in datas:
        novo = {
            "id" : evento.id,
            "user_id" : evento.user_id,
            "event_start" : evento.event_start.strftime('%d-%m-%Y'),
        }
        events_to_jinja.append(novo)


    if (request.method == "POST"):

        data_cancel = request.form.get("data_cancel")
        date_object = datetime.strptime(data_cancel, '%d-%m-%Y').date()
        print("data cancel: ")
        print(f"{date_object} 00:00:00.000000")
        date_to_delete = f"{date_object} 00:00:00.000000"
        event_to_delete = db_session.query(Agenda).filter(Agenda.event_start == date_to_delete, Agenda.user_id == user_id).first()
        if event_to_delete:
            db_session.delete(event_to_delete)
            db_session.commit()
            print(f"Evento com id {event_to_delete.id} e título '{event_to_delete.title}' deletado.")
        else:
            print("Nenhum evento encontrado para deletar.")
        
        return redirect("/cancel")
    
    else:

        return render_template("/cancel.html", events = events_to_jinja)

# SQL Alchemy
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
