from flask import Flask, render_template, request, abort
from burn.storage import MemoryStorage
import uuid

app = Flask(__name__)
storage = MemoryStorage()

MAX_MESSAGE_LENGTH = 500

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create():
    global storage
    message = request.json["message"]
    if len(message) > MAX_MESSAGE_LENGTH:
        return "Message is too long. Please keep it shorter than 400 characters.", 403

    id = uuid.uuid4()
    storage.put(id, message)
    return str(id)

@app.route("/<token>")
def fetch(token):
    global storage
    msg = storage.get(uuid.UUID(token))
    if not msg:
        return abort(404)
    return render_template("open.html", msg=msg)

@app.route("/about")
def about():
    return render_template("about.html")
