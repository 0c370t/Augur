#!/usr/bin/python2.7
from flask import jsonify, url_for
from errors import UnknownValue
import json
import re

## This module works with endpoints.json and global_params.json
##      and enables user-friendly legibility with dev-friendly writability


# Aquire all needed data
endpoints_raw = open("json/endpoints.json").read()
endpoint_docs = json.loads(endpoints_raw)
endpoint_routes = [re.sub('\[(\w+)\]','',endpoint['route']) for endpoint in endpoint_docs]
global_parameters_raw = open("json/global_params.json").read()
global_parameters = json.loads(global_parameters_raw)

# Mutate Examples
for doc in endpoint_docs:
    for example in doc['example_requests']:
        if 'form' not in example:
            example['form'] = ""
        if 'args' not in example:
            example['args'] = ""
        example['example'] = "curl '%s%s%s' %s" % ('https://augur.noimbrian.com',doc['route'],example['args'],example['form'])
        if doc['method'] == 'POST':
            example['example'] += " -F 'file=@.../input_image.jpg' > output_image.jpg"


def getAllDocs():
    return endpoint_docs

def getDoc(requested_doc):
    # Clean up parameter value
    while requested_doc[-1] == '/':
        requested_doc = requested_doc[:-1]
    while requested_doc[0] == '/':
        requested_doc = requested_doc[1:]
    requested_doc = "/"+requested_doc+"/"

    if requested_doc in endpoint_routes:
        docIndex = endpoint_routes.index(requested_doc)
        doc = endpoint_docs[docIndex]
        method = doc['method']
        doc['global_parameters'] = global_parameters[method]
        return jsonify(doc)
    else:
        raise UnknownValue("The endpoint you have requested documentation for does not exist, ensure that you have spelled everything correctly, and cases are correct")

def getGlobalParams():
    return global_parameters
