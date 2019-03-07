#!/usr/bin/python2.7
from flask import Flask, Blueprint, render_template, jsonify, request, Response, url_for, send_file
from PIL import Image, ImageFilter
from StringIO import StringIO
from io import BytesIO
import werkzeug
import requests
import json
import sys
import os
import random
import re

augur = Flask(__name__, static_url_path="", static_folder="static")
application = augur
augur.secret_key = "EFF121E88B54D79A39CCF18E358BB"
sys.path.insert(0, augur.root_path)
os.chdir(augur.root_path)
from errors import InvalidRequest
from image_format import getFormatByExtension, isValidExtension, getValidExtensions, getExtensionByFormat
# TODO: Research other ways a file could be sent or referenced
# TODO  Download more ram

# Globals
endpoints_raw = open("json/endpoints.json").read()
endpoint_docs = json.loads(endpoints_raw)
endpoint_routes = [re.sub('\[(\w+)\]','',endpoint['route']) for endpoint in endpoint_docs]
global_parameters_raw = open("json/global_params.json").read()
global_parameters = json.loads(global_parameters_raw)

# Augur Routes

@augur.route("/")
def index():
    # Displays an explanation of the API
    return render_template("index.html.jinja", docs=endpoint_docs, global_params=global_parameters)


@augur.route("/doc/<path:requested_doc>", methods=["GET"])
def doc(requested_doc):
    # Force proper leading and trailing slashes
    while requested_doc[-1] == '/':
        requested_doc = requested_doc[:-1]
    while requested_doc[0] == '/':
        requested_doc = requested_doc[1:]
    requested_doc = "/"+requested_doc+"/"
    if requested_doc in endpoint_routes:
        indexOfDoc = endpoint_routes.index(requested_doc)
        doc = endpoint_docs[indexOfDoc]
        doc['global_parameters'] = global_parameters[doc['method']]
        return jsonify(doc)
    raise InvalidRequest(
        "The endpoint you have requested does not exist!", endpoint=requested_doc)

# Augur POST Endpoints

@augur.route("/thumbnail", methods=["POST"])
def thumbnail():
    output_size = getArg(request,"size",200)
    output_size = getPixelValue(output_size,'size')

    request.image_data['image'].thumbnail((output_size, output_size))

    return sendImage(request.image_data)

@augur.route("/blur/gaussian", methods=["POST"])
def blur_gaussian():
    radius = getArg(request,"radius",2)
    radius = getPixelValue(radius,"radius")

    request.image_data['image'] = request.image_data['image'].filter(ImageFilter.GaussianBlur(radius))

    return sendImage(request.image_data)

@augur.route("/blur/box", methods=["POST"])
def blur_box():
    radius = getArg(request,"radius",2)
    radius = getPixelValue(radius,"radius")
    request.image_data['image'] = request.image_data['image'].filter(ImageFilter.BoxBlur(radius))
    return sendImage(request.image_data)

@augur.route("/blur/unsharp", methods=["POST"])
def blur_unsharp():
    radius = getArg(request,"radius",2)
    radius = int(getPixelValue(radius,"radius"))
    percent = getArg(request,"percent",150)
    threshold = getArg(request,"threshold",3)
    request.image_data['image'] = request.image_data['image'].filter(ImageFilter.UnsharpMask(radius, percent, threshold))
    return sendImage(request.image_data)

@augur.route("/fun/needsmore", methods=["POST"])
def fun_needsmore():
    temp_image_data = temp_image_data = {
        'image' : request.image_data['image'],
        'image_name' : request.image_data['image_name'].split('.')[0] + "." + "jpg",
        'image_format' : "JPEG",
        'image_extension' : "jpg"
    }
    for i in range(random.randint(15,30)):
        temp_image_data['image'] = request.image_data['image']
        request.image_data['image'] = Image.open(pilImageToFile(temp_image_data, quality=random.randint(1,25)))
    return sendImage(temp_image_data)

# Augur Utility Funtions

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
        try:
            if arg in request.args:
                return type(default)(request.args[arg])
            else:
                return type(default)(request.form[arg])
        except:
            raise InvalidRequest("Parameter %s was given with invalid format! (Default for parameter is %s)" % (arg,default))

def getPixelValue(value, name):
    try:
        return int(value)
    except:
        if value[-2:] == "px":
            return int(value[:-2])
        else:
            raise InvalidRequest(
                "Invalid parameter", given_value=value, parameter=name)

def sendImage(image_data, **kwargs):
    # Expects dict strucutre from getImageDataFromRequest()
    imageAsFile = pilImageToFile(image_data, **kwargs)
    return send_file(imageAsFile, as_attachment=True, attachment_filename=image_data['image_name'])


def pilImageToFile(image_data, **kwargs):
    imageIO = StringIO()
    image_data['image'].save(imageIO, image_data['image_format'], **kwargs)
    imageIO.seek(0, 0)
    return imageIO


def getImageDataFromRequest(request):
    # This method will be expanded to include other ways of including a file, rather than just including it in the initial request (such as a url to get the image from)
    # Ensure file actually exists
    if 'file' not in request.files and 'file' not in request.form and 'file' not in request.args:
        raise InvalidRequest(
            "No file detected in request (It should be attached with name file)")
    if 'file' in request.files:
        image = request.files['file']
        imageObject = Image.open(image)
        return {
            'image': imageObject,
            'image_name': image.filename,
            'image_format': getFormatByExtension(image.filename),
            'image_extension': "." + image.filename.split('.')[-1]
        }
    else:
        fileURL = getArg(request,'file','')
        if isinstance(fileURL, basestring) and fileURL[:4] == "http":
            # Ensure it points to an image file
            image_extension = fileURL.split(".")[-1]
            if isValidExtension(image_extension):
                # Make Request
                response = requests.get(fileURL)
                imageObject = Image.open(BytesIO(response.content))
                imageName = fileURL.split('/')[-1]
                return {
                    'image': imageObject,
                    'image_name': imageName,
                    'image_format': getFormatByExtension(imageName),
                    'image_extension': "." + imageName.split(".")[-1]
                }
            else:
                raise InvalidRequest("Invalid File Extension! (Must be one of %s)" % getValidExtensions())
        else:
            raise InvalidRequest("Invalid File Type! (Files can be attached directly, or given as a url)")
