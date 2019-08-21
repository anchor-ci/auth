import requests

from models import OAuth
from config import get_settings, get_provider_settings

class WebhookManager:
    def __init__(self):
        self.settings = get_settings()
        self.provider_settings = {
            "github": get_provider_settings("github")
        }

    def _generate_hook_config(self, url, content_type="json"):
        return {
            "name": "web",
            "active": False,
            "config": {
                "url": url,
                "content_type": content_type
            }
        }

    def create_webhook(self, owner, repo, url, provider="github"):
        oauth = OAuth.query.filter_by(
            user_id=owner.id
        ).scalar()

        if not oauth:
            return None

        base_url = self.provider_settings[provider].BASE_URL
        endpoint = self.provider_settings[provider].WEBHOOK_CREATE_ENDPOINT.format(
            owner=owner.username,
            repo=repo
        )

        complete_url = "".join([base_url, endpoint])
        payload = self._generate_hook_config(url)
        response = requests.post(
            complete_url,
            json=payload,
            headers={
                "Authorization": f"token {oauth.token}"
            }
        )

        return response
