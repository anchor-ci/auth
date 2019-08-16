import requests

from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify
from models import User, db, OAuth
from config import get_settings

settings = get_settings()
auth = Blueprint(__name__, 'auth')
api = Api(auth)

class ValidRoute(Resource):
    def post(self):
        # verify token
        token = request.headers.get('x-api-key')

        if not token:
            abort(400)

        code = 200
        response = User.decode_auth_token(token)

        if response.get('status') == 'failed':
            code = 400

        return response, code

@auth.route('/github')
def catch_login():
    #TODO: Add state # from docs: https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/
    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    oauth_url = settings.GITHUB_OAUTH_URL
    user_url = settings.GITHUB_USER_URL

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': request.args.get('code')
    }

    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }

    if payload.get('code'):
        response = requests.post(
            oauth_url,
            json=payload,
            headers=headers
        )

        # Check if the code has expired
        body = response.json()

        if response.status_code == 200:
            token = response.json().get('access_token')

            headers = {
                "Accept": "application/json",
                "Authorization": f"token {token}"
            }

            response = requests.get(
                user_url,
                headers=headers
            ).json()

            username = response.get('login')
            exists = User.query.filter_by(
                username=username
            ).first()

            # Just a login version, skip registration
            if exists:
                return exists.encode_auth_token(), 200

            user = User(
                username=username,
                email=response.get('email'),
                name=response.get('name')
            )

            db.session.add(user)
            db.session.commit()

            oauth = OAuth(
                user=user,
                token=token,
                provider="github"
            )

            db.session.add(oauth)
            db.session.commit()

            return user.encode_auth_token(), 201
        else:
            return jsonify({"status":"failed"}), 409
    else:
        return jsonify({}), 400

    return jsonify({"error": "fallthrough"}), 400

api.add_resource(ValidRoute, '/verify')
