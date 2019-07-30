import requests

from dataclasses import dataclass
from marshmallow.exceptions import ValidationError
from marshmallow import post_load, validates, Schema, fields
from config import get_settings, get_provider_settings
from flask import Blueprint, request, jsonify, abort
from models import User

sync = Blueprint(__name__, 'sync')
settings = get_settings()

@dataclass
class IncomingRepo:
    name: str
    description: str

class IncomingRepoSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(missing=None)

    @post_load
    def make_repo(self, data, **kwargs):
        return IncomingRepo(**data)

def create_repo(information, user, provider):
    schema = IncomingRepoSchema()
    repo = schema.load(information)

    if repo.errors:
        return None

    repo = repo.data

    url = "".join([
        settings.JOB_URL,
        settings.JOB_REPO_ENDPOINT
    ])

    payload = {
        "provider": provider,
        "name": repo.name,
        "owner": str(user.id),
        "is_organization": False
    }

    response = requests.post(url, json=payload)

    if response.status_code >= 400:
        return None

    return response.json()

@sync.route('/sync/<uuid>')
def sync_user_repositories(uuid):
    """
    A route that will grab all repositories from GitHub (or any
    future provider), and sync their repositories with ours, so we have
    the latest and up to date information

    This route should call out to the job micro service to create all
    repositories

    TODO:
        - Support other providers in future
        - Make syncing errors more descriptive
    """
    provider = "github" # This could be changed to gitlab in future or something

    provider_settings = get_provider_settings(provider)
    user = User.from_uid(uuid)

    if not user:
        return abort(404)

    url = "".join([
        provider_settings.BASE_URL,
        provider_settings.REPO_ENDPOINT.format(user=user.username)
    ])

    repos = []
    response = requests.get(url)
    if response.status_code >= 400:
        return abort(response.status_code)
    else:
        for repo in response.json():
            repo = create_repo(repo, user, provider)
            repos.append(repo)

    code = 200

    if not any(repos):
        code = 400

    return jsonify(repos), code
