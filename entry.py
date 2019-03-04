#!/usr/bin/python2.7
from flask import Flask, Blueprint, render_template, jsonify, request

# Used if augur is to be a Blueprint
# augur = Blueprint("augur", __name__,
#                    template_folder = "templates",
#                    static_folder = "static")

augur = Flask(__name__, static_url_path="", static_folder="static")
application = augur
augur.secret_key = "EFF121E88B54D79A39CCF18E358BB"


@augur.route("/")
def index():
    # Displays an explanation of the API
    return render_template("index.html.jinja")
