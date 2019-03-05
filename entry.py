#!/usr/bin/python2.7
from flask import Flask, Blueprint, render_template, jsonify, request, Response, url_for, send_file
from PIL import Image
from StringIO import StringIO
import json
import sys
import os

augur = Flask(__name__, static_url_path="", static_folder="static")
application = augur
augur.secret_key = "EFF121E88B54D79A39CCF18E358BB"
sys.path.insert(0, augur.root_path)
os.chdir(augur.root_path)
from errors import InvalidRequest
from image_format import getFormatByExtension
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

@augur.route("/thumbnail", methods=["POST"])
def debug_thumbnail():
    output_size = getArg(request,"size",200)
    try:
        output_size = int(output_size)
    except:
        if tempSize[-2:] == "px":
            output_size = int(output_size[:-2])
        else:
            raise InvalidRequest(
                "Invalid size parameter", given_size=output_size)


    request.image_data['image'].thumbnail((output_size, output_size))

    return sendImage(request.image_data)

@augur.before_request
def preprocessor():
    if request.method == "POST":
        request.image_data = getImageDataFromRequest(request)
        format_conversion = getArg(request,'output_format',request.image_data['image_format'])
        request.image_data['image_format'] = getFormatByExtension(format_conversion)

# Augur error handlers


@augur.errorhandler(InvalidRequest)
def error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Helper Methods

def getArg(request, arg, default):
    if arg not in request.args and arg not in request.form:
        return default
    else:
        if arg in request.args:
            return request.args[arg]
        else:
            return request.form[arg]

def sendImage(image_data, **kwargs):
    # Expects dict strucutre from getImageDataFromRequest()
    imageAsFile = pilImageToFile(image_data)
    return send_file(imageAsFile, as_attachment=True, attachment_filename=image_data['image_name'])


def pilImageToFile(image_data, **kwargs):
    imageIO = StringIO()
    image_data['image'].save(imageIO, image_data['image_format'], **kwargs)
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
        'image_format': getFormatByExtension(image.filename),
        'image_extension': "." + image.filename.split('.')[-1]
    }
    return out
