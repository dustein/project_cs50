from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    print("Hello World")
    
    return render_template("layout.html")
