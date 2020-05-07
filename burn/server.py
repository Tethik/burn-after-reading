from flask import Flask, render_template, send_from_directory, jsonify
from burn.api import json_api
import uuid

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    # For reference: https://securityheaders.com

    # CSP set to disallow anything but images and scripts from this same domain.
    # unsafe-inline is needed due to angular, as it uses this to render the templates
    # See: https://stackoverflow.com/a/34557568
    response.headers.add("Content-Security-Policy",
                         "default-src 'none'; img-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'")
    # Since the URL contains the ID this could potentially leak. By disabling referrer entirely
    # that should be safer
    response.headers.add("Referrer-Policy", "no-referrer")
    # Only feature needed is sync-xhr, again only from the same domain
    response.headers.add("Feature-Policy", "sync-xhr 'self'")
    # Disable loading this site via an iframe to protect against clickjacking.
    response.headers.add("X-Frame-Options", "DENY")
    # Disable the browser from determining content type from the MIME. Preventing potential malicious uploads.
    response.headers.add("X-Content-Type-Options", "nosniff")

    return response


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
