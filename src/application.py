import requests

from controllers import proxy, org, sync, auth
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
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(proxy, url_prefix="/proxy")
    app.register_blueprint(org, url_prefix="/organization")
    app.register_blueprint(sync)

def register_extensions(app):
    api = Api(app)

    api.add_resource(UserRoute, '/users', '/user/<uid>')

    db.init_app(app)

    with app.app_context():
        db.create_all()
        db.session.commit()

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

    def _get_all(self):
        users = db.session.query(User).all()
        schema = UserSchema(many=True)
        dumped_users = schema.dumps(users).data
        return Response(response=dumped_users, mimetype="application/json", status=200)

    def _get_one(self, uid):
        users = User.all()
        schema = UserSchema()
        dumped_users = schema.dumps(users).data
        return Response(response=dumped_users, mimetype="application/json", status=200)

    def get(self, uid=None):
        if not uid:
            return self._get_all()
        else:
            return self._get_one(uid)

        abort(500)

application = get_app()

CORS(application, origins="*", allow_headers=["Content-Type", "Access-Control-Allow-Credentials", "x-api-key"])

if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0", port=9000)

