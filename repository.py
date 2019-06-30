import requests

from config import get_provider_settings
from dataclasses import dataclass

@dataclass
class ProxyRequest:
    provider: str
    endpoint: str
    user: str

@dataclass
class CiFileRequest:
    provider: str
    user: str
    file_path: str

    def make_request(self):
        """
        TODO:
            - Add provider username to schema
            - Add repository to schema
            - Will need both to make the request
        """
        settings = get_provider_settings(self.provider)
        endpoint = settings.FILE_ENDPOINT.format()
        url = "".join([settings.BASE_URL, ])

        return {}
