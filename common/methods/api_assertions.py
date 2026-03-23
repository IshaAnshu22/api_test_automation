import time
import pytest
from jsonschema import Draft7Validator

class APIAssertions:

    def make_request(self, api_client, method, endpoint, logger, **kwargs):
        start = time.time()
        response = getattr(api_client, method)(endpoint, **kwargs)
        elapsed = (time.time() - start) * 1000

        logger.info(f"{method.upper()} {endpoint}")
        logger.info(f"Status Code: {response.status_code}")
        logger.debug(f"Response: {response.text}")
        logger.info(f"Elapsed Time: {elapsed:.2f} ms")

        return response, elapsed

    def assert_status_code(self, response, expected):
        assert response.status_code == expected, \
            f"Expected {expected}, got {response.status_code}"

    def assert_response_time(self, elapsed, max_time):
        buffer = 1.2  # avoid flakiness
        assert elapsed <= max_time * buffer, \
            f"{elapsed}ms exceeded allowed {max_time}ms"

    def assert_headers(self, response, expected_header):
        assert expected_header in response.headers.get("Content-Type", ""), \
            f"{expected_header} not found in headers"

    def validate_schema(self, body, schema):
        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(body), key=lambda e: e.path)

        if errors:
            messages = [f"{e.message} at {list(e.path)}" for e in errors]
            pytest.fail("\n".join(messages))
