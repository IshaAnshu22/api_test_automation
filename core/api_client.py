import requests as requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from common.enums.auth_type_enum import AuthTypeEnum


class ApiClientError(RuntimeError):
    pass


class ApiClient:
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(
        self,
        url,
        headers=None,
        timeout=10,
        max_retries=3,
        retry_backoff=0.5,
        retry_statuses=None,
    ):
        self.url = url
        self.headers = headers or self.default_headers.copy()
        self.timeout = timeout
        self.auth_type = None
        self.token = None
        self.username = None
        self.password = None
        self.session = requests.Session()
        self._configure_session(max_retries, retry_backoff, retry_statuses)

    def set_auth(self, auth_type: AuthTypeEnum, token=None, username=None, password=None):
        self.auth_type = auth_type
        self.token = token
        self.username = username
        self.password = password

    def _configure_session(self, max_retries, retry_backoff, retry_statuses=None):
        retry_strategy = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=retry_statuses or [429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST", "PUT", "PATCH", "DELETE"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def set_headers(self, headers=None):
        final_headers = self.headers.copy()

        if headers:
            final_headers.update(headers)

        if self.auth_type == AuthTypeEnum.BEARER and self.token:
            final_headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth_type == AuthTypeEnum.API_TOKEN and self.token:
            final_headers["x-api-key"] = self.token

        return final_headers

    def _auth(self):
        if self.auth_type == AuthTypeEnum.BASIC and self.username and self.password:
            return HTTPBasicAuth(self.username, self.password)
        return None

    def request(self, method, endpoint, headers=None, body=None, timeout=None, **kwargs):
        request_timeout = timeout if timeout is not None else self.timeout
        request_kwargs = {
            "headers": self.set_headers(headers),
            "auth": self._auth(),
            "timeout": request_timeout,
            **kwargs,
        }
        if body is not None:
            request_kwargs["json"] = body

        url = f"{self.url}{endpoint}"

        try:
            return self.session.request(method=method.upper(), url=url, **request_kwargs)
        except requests.exceptions.RequestException as exc:
            raise ApiClientError(
                f"{method.upper()} {url} failed: {exc.__class__.__name__}: {exc}"
            ) from exc

    def get(self, endpoint, headers=None, **kwargs):
        return self.request("GET", endpoint, headers=headers, **kwargs)

    def post(self, endpoint, headers=None, body=None, **kwargs):
        return self.request("POST", endpoint, headers=headers, body=body, **kwargs)

    def put(self, endpoint, headers=None, body=None, **kwargs):
        return self.request("PUT", endpoint, headers=headers, body=body, **kwargs)

    def patch(self, endpoint, headers=None, body=None, **kwargs):
        return self.request("PATCH", endpoint, headers=headers, body=body, **kwargs)

    def delete(self, endpoint, headers=None, **kwargs):
        return self.request("DELETE", endpoint, headers=headers, **kwargs)

    def close(self):
        self.session.close()
