import os
import sys

class ProviderSettings:
    pass

class GithubSettings:
    BASE_URL = "https://api.github.com"
    FILE_ENDPOINT = "/repos/{owner}/{repo}/contents/{path}"
    REPO_ENDPOINT = "/users/{user}/repos"

class Settings:
    # in days
    TOKEN_TTL = 1
    SECRET_KEY = "\xbc\x02P\xd5\x10s\xf4@^\xad\xf9g\xed\xb3\xe4:\x9e<\xb3\xbe\x9e\xc3\x01\xfe"
    GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

    GITHUB_OAUTH_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"

class NonprodSettings(Settings):
    SQLALCHEMY_DATABASE_URI = f"postgres://postgres:docker@{os.environ.get('DB_URL', 'db')}:{os.environ.get('DB_PORT', 5432)}"
    table_name = "users"
    database = ""
    FRONTEND_URI = "http://localhost:3000/home"

class ProdSettings(Settings):
    pass

def get_provider_settings(provider: str) -> ProviderSettings:
    module = sys.modules[__name__]
    reduced = list(
        filter(lambda x: provider in x.lower(), dir(module))
    )

    # Instantiate and return the first selection
    if reduced:
        return getattr(module, reduced[0])()

    return None

def get_settings():
    env = os.environ.get('ENVIRONMENT', 'nonprod')

    if env == 'nonprod':
        return NonprodSettings()

    if env == 'prod':
        return ProdSettings()

    raise ValueError("ENVIRONMENT is not set")
