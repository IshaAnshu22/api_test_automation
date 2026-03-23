import requests as requests
from requests.auth import HTTPBasicAuth

from common.enums.auth_type_enum import AuthTypeEnum


class ApiClient:
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or self.default_headers.copy()
        self.auth_type = None
        self.token = None
        self.username = None
        self.password = None

    def set_auth(self, auth_type: AuthTypeEnum, token=None, username=None, password=None):
        self.auth_type = auth_type
        self.token = token
        self.username = username
        self.password = password

    def set_headers(self, headers=None):
        if headers:
            self.headers.update(headers)
        if self.auth_type == AuthTypeEnum.BEARER and self.token is not None:
            self.headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth_type == AuthTypeEnum.API_TOKEN and self.token is not None:
            self.headers["x-api-key"] = self.token

    def _auth(self):
        if self.auth_type == AuthTypeEnum.BASIC and self.username and self.password:
            return HTTPBasicAuth(self.username, self.password)
        return None

    def get(self, endpoint, headers, **kwargs):
        return requests.get(f'{self.url}{endpoint}', headers=self.set_headers(headers), auth=self._auth(), **kwargs)

    def post(self, endpoint, headers, body, **kwargs):
        return requests.post(f'{self.url}{endpoint}', headers=self.set_headers(headers), auth=self._auth(), json=body, **kwargs)

    def put(self, endpoint, headers, body, **kwargs):
        return requests.put(f'{self.url}{endpoint}', headers=self.set_headers(headers), auth=self._auth(), json=body, **kwargs)

    def delete(self, endpoint, headers, **kwargs):
        return requests.delete(f'{self.url}{endpoint}', headers=self.set_headers(headers), auth=self._auth(), **kwargs)
