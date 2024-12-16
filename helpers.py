from flask import render_template, session, redirect
from functools import wraps

def error_msg(message, code=400):
    message = message
    return render_template("error_msg.html", message=message)

def login_required(f):
    # https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
