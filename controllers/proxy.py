"""
The proxy API is a way for other
services to makes requests to
providers (github, gitlab) without having
access to the user's oauth token.
"""

from marshmallow.exceptions import ValidationError
from schema import ProxyRequestSchema
from flask import Blueprint, request
from config import get_settings

proxy = Blueprint('proxies', __name__)

@proxy.route('')
def proxy_request():
    schema = ProxyRequestSchema()

    try:
        result = schema.load(request.json)
    except ValidationError as e:
        return e.messages, 400

    return {}, 200
