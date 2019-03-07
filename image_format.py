#!/usr/bin/python2.7
from errors import InvalidRequest

format_extension_map = {
    "JPEG":[
        "jpg",
        "jpeg",
        "jif",
        "jfif",
        "jpe"
    ],
    "BMP":[
        "bmp",
        "dib"
    ],
    "GIF":[
        "gif"
    ],
    "PNG":[
        "png"
    ]
}

valid_formats = format_extension_map.keys()
valid_extensions = [extension for format in valid_formats for extension in format_extension_map[format]]

def getFormatByExtension(extension):
    extension = extension.split('.')[-1].lower()
    if extension not in valid_extensions:
        raise InvalidRequest("Invalid extension!", detected_extension=extension)
    for format in format_extension_map:
        if extension in format_extension_map[format]:
            return format
    raise InvalidRequest("Invalid extension!", detected_extension=extenstion)

def getExtensionByFormat(format):
    if format not in valid_formats:
        return -1
    else:
        return format_extension_map[format][0]
