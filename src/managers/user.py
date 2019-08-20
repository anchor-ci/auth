from models import db, User

class UserManager:
    def __init__(self):
        pass

    def get_user_from_request(self, request):
        if "x-api-key" not in request.headers:
            return None

        return self.get_user_from_token(
            request.headers.get("x-api-key")
        )

    def get_user_from_token(self, token):
        payload = User.decode_auth_token(token)

        if payload.get("status") == "failed":
            return None

        user = User.query.get(payload.get("sub"))

        return user
