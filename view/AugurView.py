#!/usr/bin/python2.7
from flask import Blueprint, render_template, current_app, jsonify, make_response, request, url_for
from werkzeug.utils import secure_filename
from Augur import doc_builder, image_format
import os, sys, time, base64
import requests
current_milli_time = lambda: int(round(time.time() * 1000))

sys.path.insert(0,'..')

view = Blueprint('AugurView',__name__,template_folder="templates",static_folder="static")
#   Note to future Brian:
#
#   Chrome will allow users to download images even if the image is missing from the server
#   You /could/ require images to be uploaded every time, then restructure the backend
#   So the image is saved, added to a request, sent, then deleted, and then the response is
#   saved, sent back, then jQuery makes a call to the backend that deletes that image
#   This would essentially cause the tmp file to operate as ram, and is much closer to the
#   Intended functionality than you have gotten thusfar.
#   -B

UPLOAD_FOLDER = 'view/static/img/tmp/user_uploads'

@view.route("/")
def index():
    return render_template("view/view.html.jinja")

@view.route("/processImage", methods=["POST"])
def upload_image():
    # Returns an http response, so the response code indicates success or errors

    # If the file is not included, client error
    if 'file' not in request.files:
        return make_response("No File Given!", 400)

    image = request.files['file']
    # If the file was "included", but there is no filename, client error
    if image.filename == '':
        return make_response("No File Given!", 400)

    if image and allowed_file(image.filename):
        filename = base64.b16encode(str(current_milli_time)) + "." + image.filename.rsplit('.')[-1]
        # TODO: Ensure File doesn't conflict with an existing name (perhaps append some counter to the end of it?)
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        # Make the request to Augur
        request = requests.post("https://augur.noimbrian.com")


        return make_response("static/img/tmp/user_uploads/%s" % filename, 200)
    else:
        # If the extension was invalid, client error
        return make_response("Invalid File Extension", 400)

@view.route("/getEndpoints")
def getEndpoints():
    docs = doc_builder.endpoint_docs
    out = []
    for doc in docs:
        if doc['method'] == "POST":
            t = {} # Temporary Variable
            t['route'] = doc['route']
            t['description'] = doc['title']
            out += [t]
    return jsonify(out)

# Context Processor
@view.context_processor
def inject_debug():
    ## This is used to determine which jQuery file should be loaded by the user
    return dict(debug=current_app.debug)


# Helper Methods

def allowed_file(filename):
    # While extension checking is also done by Augur itself,
    #   because the files are stored here, they need to be verified.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in image_format.valid_extensions
