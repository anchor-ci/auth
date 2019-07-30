"""
The proxy API is a way for other
services to makes requests to
providers (github, gitlab) without having
access to the user's oauth token.
"""

from marshmallow.exceptions import ValidationError
from schema import AnchorFileRequestSchema
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from config import get_settings

proxy = Blueprint('proxies', __name__)
api = Api(proxy)

class FileProxy(Resource):
    def get(self):
        data = getattr(request, "json", {})
        schema = AnchorFileRequestSchema()
        result = schema.load(data)

        if result.errors:
            return result.errors, 400
        else:
            contents = result.data.make_request()
            code = 200
            if not contents:
                code = 404
            return contents, code

        return {"error": "you shouldn't get here!"}, 400

api.add_resource(FileProxy, "/file")
