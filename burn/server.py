from datetime import datetime
import math

from flask import Flask, render_template, request, abort, send_from_directory
from burn.storage import MemoryStorage

app = Flask(__name__)

AES_CIPHER_SIZE = 128

@app.before_first_request
def init():
    capacity = app.config.get('BURN_MAX_STORAGE', 65536)
    database_file = app.config.get('BURN_DATABASE_FILE', "/dev/shm/burn.db")
    app.storage = MemoryStorage(capacity, database_file)

@app.route("/")
def index():
    maxlength = app.config.get('BURN_MAX_MESSAGE_LENGTH', 2048)
    return render_template("index.html", maxlength=maxlength)

@app.route("/create", methods=["POST"])
def create():
    message = request.json["message"]
    expiry = datetime.utcfromtimestamp(request.json["expiry"] / 1000)
    anonymize_ip = request.json["anonymize_ip"]
    burn_after_reading = request.json["burn_after_reading"]
    maxlength = app.config.get('BURN_MAX_MESSAGE_LENGTH', 2048)
    # ciphertext padding. Guesstimated.
    ciphertext_maxlength = AES_CIPHER_SIZE - (maxlength % AES_CIPHER_SIZE) + maxlength
    # base64.
    ciphertext_maxlength = math.ceil(ciphertext_maxlength / 3) * 4
    # sjcl metadata (iv, etc)
    ciphertext_maxlength += AES_CIPHER_SIZE

    if len(message) > ciphertext_maxlength:
        return "Message is too long. Please keep it shorter than %s characters." % maxlength, 403

    _id = app.storage.put(message, expiry, anonymize_ip, request.remote_addr, burn_after_reading=burn_after_reading)
    return str(_id)

@app.route("/<uuid:token>", methods=["DELETE"])
def delete(token):
    app.storage.delete(token)
    return "ok"

@app.route("/<uuid:token>", methods=["GET"])
def fetch(token):    
    ret = app.storage.get(token, request.remote_addr)

    if not ret:
        return abort(404)
        
    visitors = app.storage.list_visitors(token)
    unique_visitors = set([v[0] for v in visitors])

    aliased_visitors = list()
    v_counter = 1
    alias_dictionary = dict()
    for identifier, time, creator in visitors:
        if identifier not in alias_dictionary:
            if creator:
                alias_dictionary[identifier] = "Author (" + identifier + ")"
            else:
                alias_dictionary[identifier] = "Visitor " + str(v_counter) + " (" + identifier + ")"
                v_counter += 1
        aliased_visitors.append((alias_dictionary[identifier], time))

    msg, expiry, anonymize_ip_salt, burn_after_reading = ret
    return render_template("open.html", msg=msg, expiry=expiry,
                           visitors=aliased_visitors, burn_after_reading=burn_after_reading,
                           unique_visitors=len(unique_visitors),
                           anonymous=(anonymize_ip_salt != None))

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')
