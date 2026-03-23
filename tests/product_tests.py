import json
import numbers
from time import time
import pytest
from jsonschema.exceptions import ValidationError
from jsonschema import validate
from api.endpoints import PRODUCT_ENDPOINTS


class TestProduct:

    def test_get_products(self, test_context, logger, get_schema_folder_path):

        test_data = test_context["test_data"]

        # Build query params
        opt_params = {}
        # if test_data.get("category"):
        # opt_params["category"] = test_data["category"]
        if test_data.get("limit"):
            opt_params["limit"] = test_data["limit"]

        # API Request
        start = time()
        response = test_context["setup"].get(PRODUCT_ENDPOINTS["get_products"], headers=None, params=opt_params)
        end = time()

        elapsed = (end - start) * 1000

        # 1. Response time check
        logger.info("Checking response time.")
        assert elapsed <= test_data["max_elapsed_time_in_ms"], \
            f"Elapsed time {elapsed}ms exceeded max {test_data['max_elapsed_time_in_ms']}ms"
        logger.debug(f"Elapsed time is {elapsed}ms")
        logger.info(f"Response time within expected range")

        # 2. Status code check
        assert response.status_code == test_data["expected_status_code"], \
            f"Expected {test_data['expected_status_code']}, got {response.status_code}"

        # 3. Header check
        assert test_data["content_type_header"] in response.headers["Content-Type"], \
            f"{test_data['content_type_header']} not in headers"

        # 4. Body validation
        body = response.json()
        assert isinstance(body, list), "Expected list of products"

        # 5. Limit validation
        if opt_params.get("limit"):
            assert len(body) == int(test_data["limit"]), \
                f"Returned {len(body)} items but expected limit {test_data['limit']}"

        # 6. Category validation (only if category passed)
        # category_filter = opt_params.get("category")

        for item in body:
            # Basic type checks
            assert isinstance(item["id"], int)
            assert isinstance(item["title"], str)
            assert isinstance(item["price"], numbers.Number)
            assert isinstance(item["description"], str)
            assert isinstance(item["category"], str)
            assert isinstance(item["image"], str)

            # Nested rating object
            assert isinstance(item["rating"], dict)
            assert isinstance(item["rating"]["rate"], numbers.Number)
            assert isinstance(item["rating"]["count"], int)

            # Validate category only if filter applied
            # if category_filter:
            #     assert item["category"] == category_filter, \
            #         f"Category mismatch: expected {category_filter}, got {item['category']}"

        # 7. JSON Schema validation
        json_schema_folder_path = get_schema_folder_path

        with open(json_schema_folder_path, "r") as f:
            schema = json.load(f)

        try:
            validate(instance=body, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Schema validation failed: {e.message}, Path: {list(e.path)}")
