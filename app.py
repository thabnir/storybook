from functools import wraps
import os
from flask import Flask, render_template, redirect, request, session, url_for
from flask_session import Session

from dnd import DND

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

dnd = DND()

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    if "username" in session:
        return redirect("/waitingroom")
    return render_template("index.html")

@app.route("/joingame", methods=["POST"])
def joingame():
    session.clear()
    session["username"] = request.form.get("username")
    session["character_class"] = request.form.get("character_class")
    dnd.add_user((session["username"], session["character_class"]))
    return redirect("/waitingroom")

@app.route("/waitingroom")
@login_required
def waitingroom():
    if dnd.get_is_started():
        return redirect("/game")
    return render_template("waitingroom.html", name=session["username"])

@app.route("/startgame")
@login_required
def startgame():
    global dnd
    try:
        dnd.start_game()
        return redirect("/game")
    except ValueError:
        return redirect("/waitingroom")

@app.route("/api/waitingroom")
@login_required
def waitingroom_status():
    global dnd
    if dnd.get_is_started():
        return "", 200
    return "", 204

@app.route("/game")
@login_required
def game():
    global dnd
    if not dnd.get_is_started:
        return redirect("/waitingroom")
    return render_template("game.html", character_1_name=dnd.character_1_name, character_1_health = dnd.character_1_health, character_2_name=dnd.character_2_name, character_2_health=dnd.character_2_health, is_first=(session["username"] == dnd.character_1_name))

@app.route("/api/getmessages")
@login_required
def getmessages():
    global dnd
    return dnd.content

@app.route("/api/gethealth")
@login_required
def gethealth():
    global dnd
    return [dnd.character_1_health, dnd.character_2_health]

@app.route("/api/action", methods=["POST"])
@login_required
def action():
    global dnd
    if request.form.get("action"):
        dnd.user_submit_message(request.form.get("action"), session["username"])
        return ""
    return "Could not complete action."

@app.route("/jail")
def jail():
    session.clear()
    return render_template("jail.html")

@app.route("/endgame")
@login_required
def endgame():
    global dnd
    dnd = DND()
    session.clear()
    app.config['SECRET_KEY'] = os.urandom(32)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6969)
