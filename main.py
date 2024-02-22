import requests
import json
import urllib.parse
from datetime import datetime
from getpass import getpass
from os import getenv
from dotenv import load_dotenv


class OneDrive:
    def __init__(self):
        load_dotenv()
        self.auth_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.access_URL = "https://graph.microsoft.com/v1.0/"
        self.permissions = ["offline_access", "files.readwrite", "User.Read"]
        self.scope = "+".join(self.permissions)
        self.client_id = getenv("CLIENT_ID")
        self.client_secret = getenv("CLIENT_SECRET")
        self.code = self.authenticate()
        self.tokens = self.get_tokens()

    @staticmethod
    def call_refresh(function):
        def wrapper(self, *args, **kwargs):
            self.refresh_tokens()
            return function(self, *args, **kwargs)

        return wrapper

    def authenticate(self):
        response_type = "code"
        redirect_uri = "http://localhost:8000/"

        print(
            f"Click over this link: {self.auth_URL}?client_id={self.client_id}&scope={self.scope}&response_type={response_type}&redirect_uri={urllib.parse.quote(redirect_uri)}"
        )
        print("Sign in to your account and copy the whole redirected URL.")
        code = getpass("Paste the URL here: ")
        print()

        return code[(code.find("?code") + len("?code") + 1) :]

    def get_tokens(self):
        payload = {
            "client_id": self.client_id,
            "scope": self.permissions,
            "code": self.code,
            "redirect_uri": "http://localhost:8000/",
            "grant_type": "authorization_code",
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_URL, data=payload)
        data = json.loads(response.text)

        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "last_refresh": datetime.now(),
        }

    def refresh_tokens(self):
        if self.tokens["last_refresh"] < datetime.now():
            return

        payload = {
            "client_id": self.client_id,
            "scope": self.permissions,
            "refresh_token": self.tokens["refresh_token"],
            "grant_type": "refresh_token",
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_URL, data=payload)
        data = json.loads(response.text)

        self.tokens = {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "last_refresh": datetime.now(),
        }

    @call_refresh
    def get_items(self):
        headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}
        items = json.loads(
            requests.get(
                f"{self.access_URL}me/drive/root/children", headers=headers
            ).text
        )["value"]

        return items


if __name__ == "__main__":
    onedrive = OneDrive()

    items = onedrive.get_items()
    for item in items:
        print(item["name"], "| item-id >", item["id"])
