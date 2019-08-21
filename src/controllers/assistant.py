"""
Provides all endpoints for assisting the user.
"""

from marshmallow import post_load, Schema, fields
from config import get_settings, get_provider_settings
from flask import Blueprint, request, jsonify, abort
from flask_restful import Resource, Api
from managers.webhooks import WebhookManager
from managers.user import UserManager
from managers.api_calls import Jobs
from utils import error_response

assistant = Blueprint(__name__, 'assistant')
api = Api(assistant)
settings = get_settings()

class WebhookSchema(Schema):
    repo = fields.UUID(required=True)

    @post_load
    def get_repo(self, data, **kwargs):
        repo = Jobs.get_repository(data.get('repo'))
        return repo

class WebhookController(Resource):
    def __init__(self):
        super().__init__()

        self.user_manager = UserManager()
        self.manager = WebhookManager()

    def post(self):
        if request.json is None or not request.json:
            return error_response("Request must be application/json"), 400

        schema = WebhookSchema()
        load = schema.load(request.json)

        if load.errors:
            return load.errors, 400

        user = self.user_manager.get_user_from_request(request)

        if user is None:
            return error_response("Couldn't authenticate user from token"), 401

        if load.data is None or "id" not in load.data:
            return error_response("Error grabbing repository for user"), 400

        # TODO: Add webhook user validation back in, this will require allowing users to join organizations
        #if user.id != load.data.get("id"):
        #    return error_response("Repository not owned by requester"), 403

        dock_url = "".join([settings.JOB_URL, "/repo", load.data.get("id"), "/job"])
        response = self.manager.create_webhook(
            owner=user,
            repo=load.data.get("name"),
            url=dock_url
        )

        print(response)
        print(response.json())

        return {}, 400

api.add_resource(WebhookController, "/webhook")

