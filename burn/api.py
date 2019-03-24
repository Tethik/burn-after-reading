from datetime import datetime, timedelta
import math
import logging
from flask import Flask, render_template, request, abort, send_from_directory, jsonify, Blueprint, Response
from flask import current_app as app

from burn.storage import Storage

json_api = Blueprint('json_api', __name__)
   
@json_api.before_request
def before_request():
    capacity = app.config.get('BURN_MAX_STORAGE', 65536)
    database_file = app.config.get('BURN_DATABASE_FILE', "/dev/shm/burn.db")
    attachment_path = app.config.get('BURN_ATTACHMENTS_PATH', "/dev/shm/burn-attachment/")
    app.storage = Storage(capacity, attachment_path, database_file)
    app.storage.expire() # TODO: Run this as a cronjob.


@json_api.route("/create", methods=["POST"])
def create():
    message = request.json["message"]
    anonymize_ip = request.json["anonymize_ip"]
    burn_after_reading = request.json["burn_after_reading"]

    max_expiry_delta = app.config.get('BURN_MAX_EXPIRY_TIME', 60*60*24*7)
    given_expiry = datetime.utcfromtimestamp(request.json["expiry"] / 1000)
    max_expiry = datetime.utcnow() + timedelta(seconds=max_expiry_delta)
    expiry = min(given_expiry, max_expiry)

    _id = app.storage.create(message, expiry, anonymize_ip, request.remote_addr,
                          burn_after_reading=burn_after_reading)

    return jsonify({"id": _id})


@json_api.route("/<uuid:token>", methods=["DELETE"])
def delete(token):
    app.storage.delete(token)
    return jsonify({"message": "ok"})


@json_api.route("/<uuid:token>", methods=["GET"])
def read(token):
    ret = app.storage.get(token, request.remote_addr)

    if not ret:
        return abort(404)

    visitors = app.storage.list_visitors(token)    
    unique_visitors = set([v[0] for v in visitors])

    aliased_visitors = list()
    alias_dictionary = dict()
    for identifier, time, creator in visitors:
        if identifier not in alias_dictionary:
            if creator:
                alias_dictionary[identifier] = "Author"
            else:
                alias_dictionary[identifier] = "Visitor " + str(len(alias_dictionary.keys()))
                
        aliased_visitors.append({"id": identifier, "alias": alias_dictionary[identifier], "time": time})

    ret.update({
        "visitors": aliased_visitors,
        "unique_visitors": list(unique_visitors)
    })   

    return jsonify(ret)
