from models import User, Organization
from repository import ProxyRequest, CiFileRequest
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

class OrganizationSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)

    @post_load
    def make_org(self, data, **kwargs):
        return Organization(**data)

class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    register_time = fields.DateTime(dump_only=True, required=True)
    organization = fields.Nested(OrganizationSchema)

    @validates('username')
    def validate_username(self, data, **kwargs):
        raise NotImplementedError("Implement username validation")

    @validates('email')
    def validate_email(self, data, **kwargs):
        raise NotImplementedError("Implement email validation")

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class AnchorFileRequestSchema(Schema):
    owner = fields.UUID(required=True)
    repository = fields.Str(required=True)
    # provider_owner is their provider respective username
    provider_owner = fields.Str(missing=None)
    file_path = fields.Str(missing=".anchorci.yml")
    provider = fields.Str(validate=validate.OneOf(PROVIDERS), required=True)
    is_organization = fields.Bool(required=True)

    @pre_load
    def fix_data(self, data, **kwargs):
        if data and "provider" in data:
            data["provider"] = data["provider"].lower()

    @post_load
    def make_file_request(self, data, **kwargs):
        if not data.get("provider_owner"):
            data["provider_owner"] = data.get("owner")

        return CiFileRequest(**data)
