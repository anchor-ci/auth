"""
The proxy API is a way for other
services to makes requests to
providers (github, gitlab) without having
access to the user's oauth token.
"""

from marshmallow.exceptions import ValidationError
from schema import ProxyRequestSchema, AnchorFileRequestSchema
from flask import Blueprint, request, jsonify
from config import get_settings

proxy = Blueprint('proxies', __name__)

@proxy.route("")
def proxy_request():
    data = {}

    if request.json:
        data = request.json

    schema = ProxyRequestSchema()
    result = schema.load(data)

    if result.errors:
        return jsonify(result.errors), 400

    return jsonify({}), 200

@proxy.route("/file")
def get_ci_file():
    data = {}
    if request.json:
        data = request.json

    schema = AnchorFileRequestSchema()
    result = schema.load(data)

    if result.errors:
        return jsonify(result.errors), 400
    else:
        contents = result.data.make_request()
        return jsonify(contents), 200

    return {"error": "you shouldn't get here!"}, 400
