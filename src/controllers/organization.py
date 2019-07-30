from flask_restful import Resource, Api
from flask import request, Blueprint, jsonify
from schema import OrganizationSchema
from models import Organization, db

org = Blueprint('organizations', __name__)
api = Api(org)

class OrganizationController(Resource):
    def _get_all(self):
        org_schema = OrganizationSchema(many=True)
        result = org_schema.dump(
            Organization.query.all()
        )

        if result.errors:
            return result.errors, 400

        return result.data, 200

    def _get(self, oid):
        org_schema = OrganizationSchema()
        result = org_schema.dump(
            Organization.query.filter_by(id=oid).first()
        )

        if result.errors:
            return results.errors, 400

        return result.data, 200

    def get(self, oid=None):
        if oid:
            return self._get(oid)
        else:
            return self._get_all()

    def post(self, oid=None):
        schema = OrganizationSchema()
        result = schema.load(request.json)

        if result.errors:
            return result.errors, 400

        db.session.add(result.data)
        db.session.commit()

        return schema.dump(result.data)

    def put(self, oid=None):
        pass

    def delete(self, oid=None):
        pass

api.add_resource(OrganizationController, "", "<oid>")
