from flask import Flask, render_template, request, abort
from burn.storage import MemoryStorage
import uuid

app = Flask(__name__)
MAX_MESSAGE_LENGTH = 2048

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create():
    storage = MemoryStorage(500)
    message = request.json["message"]
    if len(message) > MAX_MESSAGE_LENGTH:
        return "Message is too long. Please keep it shorter than 400 characters.", 403

    id = storage.put(message)
    return str(id)

@app.route("/<token>", methods=["GET","DELETE"])
def fetch(token):
    storage = MemoryStorage(500)
    u = uuid.UUID(token)

    if request.method == "DELETE":
        storage.delete(u)
        return "ok"

    msg = storage.get(u)
    if not msg:
        return abort(404)
    return render_template("open.html", msg=msg)



@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
