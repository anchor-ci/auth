from marshmallow import Schema, fields, post_load
from models import User

# TODO: Need to verify in here if the user already exists
class UserSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    register_time = fields.DateTime(dump_only=True, required=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)
