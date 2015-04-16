from flask import Flask, render_template, request
from burn.storage import MemoryStorage
import uuid

app = Flask(__name__)
storage = MemoryStorage()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create():
    global storage
    return str(uuid.uuid4())

@app.route("/<token>")
def fetch(token):
    global storage
    msg = storage.get(token)
    return render_template("open.html", msg=msg)

@app.route("/about")
def about():
    return render_template("about.html")
