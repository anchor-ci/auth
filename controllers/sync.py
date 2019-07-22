import requests

from config import get_settings, get_provider_settings
from flask import Blueprint, request, jsonify, abort
from models import User

sync = Blueprint(__name__, 'sync')
settings = get_settings()

def create_repo(information):
    print(information)

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
    provider_settings = get_provider_settings("github")
    user = User.from_uid(uuid)

    if not user:
        return abort(404)

    url = "".join([
        provider_settings.BASE_URL,
        provider_settings.REPO_ENDPOINT.format(user=user.username)
    ])

    response = requests.get(url)
    if response.status_code >= 400:
        return abort(response.status_code)
    else:
        for repo in response.json():
            create_repo(repo)

    return {}, 200
