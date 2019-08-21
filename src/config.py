import os
import sys

class ProviderSettings:
    pass

class GithubSettings:
    BASE_URL = "https://api.github.com"
    FILE_ENDPOINT = "/repos/{owner}/{repo}/contents/{path}"
    REPO_ENDPOINT = "/users/{user}/repos"
    WEBHOOK_CREATE_ENDPOINT = "/repos/{owner}/{repo}/hooks"

class Settings:
    # in days
    table_name = "users"
    database = ""
    DATABASE_USER = os.environ.get("DB_USER")
    DATABASE_PASSWORD = os.environ.get("DB_PASSWORD")
    DATABASE_URL = os.environ.get('DB_URL', 'db')
    DATABASE_PORT = os.environ.get('DB_PORT', 5432)
    SQLALCHEMY_DATABASE_URI = f"postgres://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}"

    TOKEN_TTL = 1
    SECRET_KEY = "\xbc\x02P\xd5\x10s\xf4@^\xad\xf9g\xed\xb3\xe4:\x9e<\xb3\xbe\x9e\xc3\x01\xfe"
    GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

    GITHUB_OAUTH_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"
    JOB_REPO_ENDPOINT = "/repo"

class NonprodSettings(Settings):
    FRONTEND_URI = "http://localhost:3000/home"
    AUTH_URL = "http://192.168.39.217:30001"
    JOB_URL = "http://192.168.39.217:30002"
    JOB_REPO_ENDPOINT = "/repo"

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
