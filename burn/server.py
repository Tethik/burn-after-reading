from flask import Flask, render_template, request, abort, send_from_directory
from burn.storage import MemoryStorage
from datetime import datetime
import uuid

app = Flask(__name__)
MAX_MESSAGE_LENGTH = 2048 # No exact math done to determine this.
MAX_STORAGE = 65536

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create():
    storage = MemoryStorage(MAX_STORAGE)
    message = request.json["message"]
    expiry = datetime.utcfromtimestamp(request.json["expiry"] / 1000)
    anonymize_ip = request.json["anonymize_ip"]
    if len(message) > MAX_MESSAGE_LENGTH:
        return "Message is too long. Please keep it shorter than 250 characters.", 403

    ip = request.remote_addr
    id = storage.put(message, expiry, anonymize_ip, ip)
    return str(id)

@app.route("/<token>", methods=["GET","DELETE"])
def fetch(token):
    storage = MemoryStorage(500)
    u = uuid.UUID(token)
    ip = request.remote_addr

    ret = storage.get(u, ip)

    if not ret:
        return abort(404)

    if request.method == "DELETE":
        storage.delete(u)
        return "ok"

    visitors = storage.list_visitors(u)
    unique_visitors = set([v[0] for v in visitors])

    aliased_visitors = list()
    v_counter = 1
    alias_dictionary = dict()
    for v in visitors:
        ip, time, creator = v
        if ip not in alias_dictionary:
            if creator:
                alias_dictionary[ip] = "Author (" + ip + ")"
            else:
                alias_dictionary[ip] = "Visitor " + str(v_counter) + " (" + ip + ")"
                v_counter += 1
        aliased_visitors.append((alias_dictionary[ip], time))

    msg, expiry, anonymize_ip_salt = ret
    return render_template("open.html", msg=msg, expiry=expiry,
        visitors=aliased_visitors, unique_visitors=len(unique_visitors), anonymous=(anonymize_ip_salt != None))

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')
