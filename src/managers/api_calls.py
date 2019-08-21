import requests
import os

from config import get_settings

settings = get_settings()

class Jobs:
    @staticmethod
    def get_repository(rid):
        url = "".join([settings.JOB_URL, settings.JOB_REPO_ENDPOINT, "/", str(rid)])
        response = requests.get(url)

        if response.status_code >= 400:
            return None

        return response.json()
