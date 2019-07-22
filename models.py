import jwt
import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from config import get_settings

settings = get_settings()
db = SQLAlchemy()

class Organization(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid4)
    name = db.Column(db.String(255), nullable=False, unique=True)

class User(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid4, primary_key=True)
    username = db.Column(db.String(127), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    register_time = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # For when a user is a part of an organization
    org_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Organization.id), nullable=True, default=None)
    organization = db.relationship(Organization)

    def __init__(self, username, email, name, organization=None):
        if organization:
            self.org_id = organization.id

        self.organization = organization
        self.username = username
        self.email = email
        self.register_time = datetime.datetime.now()
        self.name = name

    @staticmethod
    def from_uid(uid):
        return User.query.get(uid)

    @staticmethod
    def decode_auth_token(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            return payload
        except jwt.ExpiredSignatureError:
            return {"status": "failed", "reason":"expired"}
        except jwt.InvalidTokenError:
            return {"status":"failed", "reason":"invalid"}

    def encode_auth_token(self):
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=settings.TOKEN_TTL),
            "iat": datetime.datetime.utcnow(),
            "sub": str(self.id)
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )

class OAuth(db.Model):
    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id))
    user = db.relationship(User, cascade="all,delete")
    provider = db.Column(db.String(64), nullable=False)
    token = db.Column(db.String(255), nullable=False)

