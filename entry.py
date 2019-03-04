#!/usr/bin/python2.7
from flask import Flask, Blueprint, render_template, jsonify, request, Response, url_for, send_file
from PIL import Image
from StringIO import StringIO
from errors import InvalidRequest
# Used if augur is to be a Blueprint
# augur = Blueprint("augur", __name__,
#                    template_folder = "templates",
#                    static_folder = "static")

augur = Flask(__name__, static_url_path="", static_folder="static")
application = augur
augur.secret_key = "EFF121E88B54D79A39CCF18E358BB"


# Augur Routes
@augur.route("/")
def index():
    # Displays an explanation of the API
    return render_template("index.html.jinja")


@augur.route("/debug/formData", methods=["POST"])
def debug_formData():
    # Current intended functionality is returning the image that is sent as form data
    image = getImageFromRequest(request)
    # OOF
    image_name = image[1]
    image_extension = "." + image_name.split('.')[-1]
    image = image[0]

    # image.save(outTempFile)
    return sendImage(image, image_name)


@augur.route("/thumbnail", methods=["POST"])
def debug_thumbnail():
    if 'size' not in request.args:
        output_size = 200
    else:
        try:
            output_size = int(request.args['size'])
        except:
            if request.args['size'][-2:] == "px":
                output_size = int(request.args['size'][:-2])
            else:
                raise InvalidRequest(
                    "Invalid size parameter", given_size=request.args['size'])

    image = getImageFromRequest(request)
    image_name = image[1]
    image = image[0]
    image_extension = "." + image_name.split('.')[-1]

    image.thumbnail((output_size, output_size))

# Augur error handlers

@augur.errorhandler(InvalidRequest)
def error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Helper Methods


def sendImage(image, image_name):
    return send_file(prepareImageForReturn(image), as_attachment=True, attachment_filename=image_name)


def prepareImageForReturn(image):
    imageIO = StringIO()
    image.save(imageIO, 'JPEG', quality=70)
    imageIO.seek(0, 0)
    return imageIO


def getImageFromRequest(request):
    # This method will be expanded to include other ways of including a file, rather than just including it in the initial request (such as a url to get the image from)
    # Ensure file actually exists
    if 'file' not in request.files:
        raise InvalidRequest(
            "No file detected in request (It should be attached with name file)")
    image = request.files['file']
    newImage = Image.open(image)
    return [newImage, image.filename]
