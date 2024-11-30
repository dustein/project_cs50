import os
from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from cs50 import SQL

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
    message = "teste"
    return render_template("error_msg.html", message=message)

@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        username = form.request.get("username")
        password = form.request.get("password")

        return redirect("/")
    else:
        return render_template("login.html")
