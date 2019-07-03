import requests

from base64 import b64decode
from config import get_provider_settings
from dataclasses import dataclass
from models import db, Organization, User

@dataclass
class ProxyRequest:
    provider: str
    endpoint: str
    user: str

@dataclass
class CiFileRequest:
    provider: str
    owner: str
    file_path: str
    provider_owner: str
    repository: str
    is_organization: bool

    def _do_request(self, url):
        response = requests.get(url)
        if response.status_code >= 400:
            return None

        content = response.json()
        if content.get("encoding") == "base64":
            return b64decode(content.get("content"))

        return None

    def make_request(self):
        settings = get_provider_settings(self.provider)
        owner = None

        if self.is_organization:
            owner = Organization.query.filter_by(
                id=self.owner
            ).first().name
        else:
            owner = User.query.filter_by(
                id=self.owner
            ).first().username

        endpoint = settings.FILE_ENDPOINT.format(
            owner=owner,
            repo=self.repository,
            path=self.file_path
        )

        url = "".join([settings.BASE_URL, endpoint])
        content = self._do_request(url)

        if content == None:
            return {}
        else:
            content = content.decode('utf-8')
            return {"content": content}

        return {}
