from flask import Flask, render_template, send_from_directory, jsonify
from burn.api import json_api
import uuid

app = Flask(__name__)


@app.route("/")
def index():
    maxlength = app.config.get('MAX_CONTENT_LENGTH', 1024*1024*10)
    return render_template("index.html", maxlength=maxlength)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')


@app.route("/<uuid:token>", methods=["GET"])
def open(token):
    return render_template("open.html")


app.register_blueprint(json_api, url_prefix='/api')


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
