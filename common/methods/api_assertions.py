import time
import pytest
from jsonschema import Draft7Validator


class APIAssertions:

    def make_request(self, logger, api_client, method, endpoint, **kwargs):
        start = time.time()
        response = getattr(api_client, method)(endpoint, **kwargs)
        elapsed = (time.time() - start) * 1000

        logger.info(f"{method.upper()} {endpoint}")
        logger.info(f"Status Code: {response.status_code}")
        logger.debug(f"Response: {response.text}")
        logger.info(f"Elapsed Time: {elapsed:.2f} ms")

        return response, elapsed

    def assert_status_code(self, logger, response, expected):
        try:
            assert response.status_code == expected
        except AssertionError:
            logger.error(
                f"Status Code Assertion Failed | Expected: {expected}, Got: {response.status_code}"
            )

    def assert_response_time(self, logger, elapsed, max_time):
        buffer = 1.2
        try:
            assert elapsed <= max_time * buffer
        except AssertionError:
            logger.error(
                f"Response Time Assertion Failed | Actual: {elapsed:.2f} ms, Allowed: {max_time} ms"
            )

    def assert_headers(self, logger, response, expected_header):
        try:
            content_type = response.headers.get("Content-Type", "")
            assert expected_header in content_type
        except AssertionError:
            logger.error(
                f"Header Assertion Failed | Expected: {expected_header}, Got: {content_type}"
            )

    def validate_schema(self, logger, body, schema):
        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(body), key=lambda e: e.path)

        if errors:
            messages = [f"{e.message} at {list(e.path)}" for e in errors]
            for msg in messages:
                logger.error(f"Schema Validation Error: {msg}")

            pytest.fail("\n".join(messages))