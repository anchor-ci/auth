"""
Provides all endpoints for assisting the user.
"""

from marshmallow.exceptions import ValidationError
from marshmallow import post_load, validates, Schema, fields
from config import get_settings, get_provider_settings
from flask import Blueprint, request, jsonify, abort
from flask_restful import Resource, Api
from managers.webhooks import WebhookManager
from managers.user import UserManager

assistant = Blueprint(__name__, 'assistant')
api = Api(assistant)
settings = get_settings()

class WebhookController(Resource):
    def __init__(self):
        super().__init__()

        self.user_manager = UserManager()
        self.manager = WebhookManager()

    def post(self):
        user = self.user_manager.get_user_from_request(request)

        if user is None:
            return {"error": "Couldn't authenticate user from token"}, 401

        return {}, 400

api.add_resource(WebhookController, "/webhook")

