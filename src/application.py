import requests

from controllers import proxy, org, sync
from config import get_settings
from flask import Flask, request, abort, jsonify, Response, redirect, url_for
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from schema import UserSchema
from models import db, User, OAuth

def get_app(config=get_settings()):
    app = Flask(__name__)
    app.config.from_object(config)

    register_extensions(app)
    register_blueprints(app)

    return app

def register_blueprints(app):
    app.register_blueprint(proxy, url_prefix="/proxy")
    app.register_blueprint(org, url_prefix="/organization")

def register_extensions(app):
    api = Api(app)

    @app.route('/auth/github')
    def catch_login():
        #TODO: Add state # from docs: https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/
        payload = {
            'client_id': app.config.get('GITHUB_CLIENT_ID'),
            'client_secret': app.config.get('GITHUB_CLIENT_SECRET'),
            'code': request.args.get('code')
        }

        headers = {
            "content-type": "application/json",
            "accept": "application/json"
        }

        if payload.get('code'):
            response = requests.post(
                app.config.get('GITHUB_OAUTH_URL'),
                json=payload,
                headers=headers
            )

            # Check if the code has expired
            body = response.json()
            reason = body.get('error')
            if reason == "bad_verification_code":
                return jsonify({"status":"failed"}), 409

            if response.status_code == 200:
                token = response.json().get('access_token')

                headers = {
                    "Accept": "application/json",
                    "Authorization": f"token {token}"
                }

                response = requests.get(
                    app.config.get('GITHUB_USER_URL'),
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
            return jsonify({}), 400

    api.add_resource(ValidRoute, '/verify')
    api.add_resource(UserRoute, '/users')
    app.register_blueprint(sync)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        db.session.commit()

class LoginRoute(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:
            return {"status":"failed"}, 404

        is_user = user.verify_password(password)
        if not is_user:
            abort(400)
        token = user.encode_auth_token()
        return {"status":"success", "token": token.decode()}, 200

class UserRoute(Resource):
    def post(self):
        data = request.get_json()
        schema = UserSchema()
        results = schema.load(request.get_json())

        if results.errors:
            return results.errors, 400

        db.session.add(results.data)
        db.session.commit()

        token = user.encode_auth_token()
        response = {
            "token": token.decode(),
            "user": schema.dumps(user)
        }

        return response, 201

    def get(self):
        users = db.session.query(User).all()
        schema = UserSchema(many=True)
        dumped_users = schema.dumps(users).data
        return Response(response=dumped_users, mimetype="application/json", status=200)

class ValidRoute(Resource):
    def post(self):
        # verify token
        token = request.headers.get('x-api-key')
        data = request.get_json()
        if not token or not data:
            abort(400)

        # grab user
        username = data.get('username')
        user = User.query.filter_by(
            username=username
        ).first()

        # if user doesn't exist
        if not user:
            abort(400)

        code = 200
        response = User.decode_auth_token(token)
        if response.get('status') == 'failed':
            code = 400

        return response, code

application = get_app()

CORS(application, origins="*", allow_headers=["Content-Type", "Access-Control-Allow-Credentials"])

if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0", port=9000)

