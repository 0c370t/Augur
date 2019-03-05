#!/usr/bin/python2.7
from flask import Flask, Blueprint, render_template, jsonify, request, Response, url_for, send_file
from PIL import Image
from StringIO import StringIO
import json
import sys
import os

# Used if augur is to be a Blueprint
# augur = Blueprint("augur", __name__,
#                    template_folder = "templates",
#                    static_folder = "static")

augur = Flask(__name__, static_url_path="", static_folder="static")
application = augur
augur.secret_key = "EFF121E88B54D79A39CCF18E358BB"
sys.path.insert(0, augur.root_path)
os.chdir(augur.root_path)
from errors import InvalidRequest

# TODO: Make lookup function for matching image extension to image format (or just a dict)
# TODO: Research other ways a file could be sent or referenced
# TODO  Download more ram

# Globals
endpoints_raw = open("endpoints.json").read()
endpoints = json.loads(endpoints_raw)


# Augur Routes


@augur.route("/")
def index():
    # Displays an explanation of the API
    return render_template("index.html.jinja", docs=endpoints)


@augur.route("/doc/<string:requested_doc>", methods=["GET"])
def doc(requested_doc):
    if requested_doc in endpoints:
        return jsonify(endpoints[requested_doc])
    raise InvalidRequest(
        "The endpoint you have requested does not exist!", endpoint=requested_doc)


@augur.route("/debug/formData", methods=["POST"])
def debug_formData():
    # Current intended functionality is returning the image that is sent as form data
    image = getImageDataFromRequest(request)
    # OOF
    image_name = image[1]
    image_extension = "." + image_name.split('.')[-1]
    image = image[0]

    # image.save(outTempFile)
    return sendImage(image, image_name)


@augur.route("/thumbnail", methods=["POST"])
def debug_thumbnail():
    if 'size' not in request.args and 'size' not in request.form:
        output_size = 200
    else:
        if 'size' in request.args:
            tempSize = request.args['size']
        else:
            tempSize = request.form['size']
        try:
            output_size = int(tempSize)
        except:
            if tempSize[-2:] == "px":
                output_size = int(tempSize[:-2])
            else:
                raise InvalidRequest(
                    "Invalid size parameter", given_size=tempSize)

    image_data = getImageDataFromRequest(request)
    image_data['image'].thumbnail((output_size, output_size))

    return sendImage(image_data)

# Augur error handlers


@augur.errorhandler(InvalidRequest)
def error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Helper Methods


def sendImage(image_data):
    # Expects dict strucutre from getImageDataFromRequest()
    imageAsFile = pilImageToFile(image_data['image'])
    return send_file(imageAsFile, as_attachment=True, attachment_filename=image_data['image_name'])


def pilImageToFile(image):
    imageIO = StringIO()
    image.save(imageIO, 'JPEG', quality=70)
    imageIO.seek(0, 0)
    return imageIO


def getImageDataFromRequest(request):
    # This method will be expanded to include other ways of including a file, rather than just including it in the initial request (such as a url to get the image from)
    # Ensure file actually exists
    if 'file' not in request.files:
        raise InvalidRequest(
            "No file detected in request (It should be attached with name file)")
    image = request.files['file']
    newImage = Image.open(image)
    out = {
        'image': newImage,
        'image_name': image.filename,
        'image_extension': "." + image.filename.split('.')[-1]
    }
    return out
