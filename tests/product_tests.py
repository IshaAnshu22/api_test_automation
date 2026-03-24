import json
import numbers
import pytest
from api.endpoints import PRODUCT_ENDPOINTS
from common.methods.api_assertions import APIAssertions


class TestProduct:

    @pytest.mark.parametrize("test_data", [
        pytest.param("get_products", id="basic"),
        pytest.param("get_products_limit", id="limit"),
    ], indirect=True)
    def test_get_products(self, setup, logger, test_data, get_schema_file_path):

        api_client = setup

        # Build params
        params = {}
        if test_data.get("limit"):
            params["limit"] = test_data["limit"]

        api_assert = APIAssertions()

        # Make request
        response, elapsed = api_assert.make_request(
            logger,
            api_client,
            "get",
            PRODUCT_ENDPOINTS["get_products"],
            params=params
        )
        api_assert.assert_response_time(logger, elapsed, test_data["max_response_time_ms"])
        api_assert.assert_status_code(logger, response, test_data["status_code"])
        api_assert.assert_headers(logger, response, test_data["content_type"])

        try:
            body = response.json()
        except json.JSONDecodeError:
            pytest.fail("Response is not valid JSON")

        assert isinstance(body, list), "Expected list of products"

        if params.get("limit"):
            assert len(body) <= int(test_data["limit"])

        for item in body:
            self.validate_product(item)

        # Schema validation
        try:
            with open(get_schema_file_path, 'r') as f:
                schema = json.load(f)
            api_assert.validate_schema(logger, body, schema)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            pytest.fail(f"Schema validation setup failed: {str(e)}")


    def validate_product(self, item):
        assert isinstance(item["id"], int), f"id must be int, got {type(item['id'])}"
        assert isinstance(item["title"], str), f"title must be str, got {type(item['title'])}"
        assert isinstance(item["price"], numbers.Number), f"price must be number, got {type(item['price'])}"
        assert isinstance(item["description"], str), f"description must be str, got {type(item['description'])}"
        assert isinstance(item["category"], str), f"category must be str, got {type(item['category'])}"
        assert isinstance(item["image"], str), f"image must be str, got {type(item['image'])}"
        assert isinstance(item["rating"], dict), f"rating must be dict, got {type(item['rating'])}"
        rating = item["rating"]
        assert isinstance(rating["rate"], numbers.Number), f"rating.rate must be number"
        assert isinstance(rating["count"], int), f"rating.count must be int"

