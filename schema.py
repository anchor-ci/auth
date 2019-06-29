from models import User
from repository import ProxyRequest
from marshmallow import (
    Schema,
    fields,
    post_load,
    pre_load,
    validates,
    validate
)

PROVIDERS = (
    "gitlab",
    "github"
)

class UserSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    register_time = fields.DateTime(dump_only=True, required=True)

    @validates('username')
    def validate_username(self, data, **kwargs):
        raise NotImplementedError("Implement username validation")

    @validates('email')
    def validate_email(self, data, **kwargs):
        raise NotImplementedError("Implement email validation")

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class ProxyRequestSchema(Schema):
    # TODO: Add a URL field that is auto-generated from provider / path
    provider = fields.Str(validate=validate.OneOf(PROVIDERS), required=True)
    endpoint = fields.Str(required=True)
    # Who to make calls on behalf of 
    user = fields.UUID(required=True)

    @pre_load
    def fix_data(self, data, **kwargs):
        if data is None:
            return

        if "provider" in data:
            data["provider"] = data["provider"].lower()

    @post_load
    def load_request(self, data, **kwargs):
       return ProxyRequest(**data)
