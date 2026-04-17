# API Test Automation

Pytest-based API automation framework for validating Fake Store API endpoints with data-driven tests, shared request utilities, JSON schema validation, and session logging.

## Requirements

- Python 3.10+
- Network access to the configured target API

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Project Layout

- 'tests/'
  Pytest test modules. The active suite is currently 'tests/product_test.py'.
- 'conftest.py'
  Shared pytest fixtures for config loading, logger setup, environment selection, test data lookup, and schema path resolution.
- 'core/'
  Framework infrastructure such as the reusable API client and logger helpers.
- 'common/methods/'
  Assertion and validation helpers shared across test modules.
- 'api/'
  Endpoint definitions used by tests.
- 'data/test_data/'
  Per-feature test case definitions loaded dynamically by fixture.
- 'data/json_schema/'
  JSON schemas used for response validation.
- 'data/json_inputs/'
  Example payloads and sample responses used to derive schemas.
- 'logs/'
  Session log output generated during pytest runs.

## Configuration

Environment selection is driven by 'config.json'.

- 'dev'
  Default environment. Points to 'https://fakestoreapi.com'.
- 'qa'
  Placeholder QA environment.
- 'staging'
  Placeholder staging environment.

The same file also defines framework settings such as:

- 'test_data_folder_path'
- 'json_schema_folder_path'
- 'logger_name'
- 'request_timeout_seconds'
- 'max_retries'
- 'retry_backoff_seconds'
- 'retry_statuses'

## How Tests Work

Each test module is mapped to a feature data file by naming convention.

- 'tests/product_test.py'
  Uses 'data/test_data/product_test_data.json'

Within that JSON file, each entry must define a unique 'test_name'. Parametrized tests pass that 'test_name' into the 'test_data' fixture, which loads the matching row and returns the case data to the test.

Typical test data fields include:

- 'test_name'
- 'description'
- 'params'
- 'json_schema'
- 'status_code'
- 'content_type'
- 'max_response_time_ms'

Schema files are resolved automatically from the feature name and the 'json_schema' field. For product tests, schemas are expected under 'data/json_schema/product/'.

## Running Tests

Run the full suite:

```powershell
pytest -q
```

Run with verbose output:

```powershell
pytest -v
```

Run against a specific environment:

```powershell
pytest -q --env dev
pytest -q --env qa
pytest -q --env staging
```

Run a single test module:

```powershell
pytest tests/product_test.py -v
```

Run a single parametrized case:

```powershell
pytest tests/product_test.py -k limit -v
```

Collect tests without executing them:

```powershell
pytest --collect-only -q
```

## Logging

Each pytest session creates a timestamped log file under 'logs/':

- 'logs/session-main-YYYYMMDD-HHMMSS.txt'

The logger writes INFO-level output to console and DEBUG-level output to the session log file.

## Adding New Tests

1. Add or update endpoint constants in 'api/endpoints.py' if needed.
2. Create a new test module under 'tests/' following the '<feature>\_test.py' naming convention.
3. Add matching test data in 'data/test_data/<feature>\_test_data.json'.
4. Add response schemas under 'data/json_schema/<feature>/'.
5. Reuse 'ApiClient' and 'APIAssertions' rather than calling 'requests' directly.

## Notes

- The suite currently targets a live external API, so failures can be caused by network issues or third-party instability.
- 'qa' and 'staging' URLs in 'config.json' are placeholders and may not be reachable as-is.
- 'data/test_data/cart_test_data.json' and 'data/test_data/users_test_data.json' currently exist as placeholders without active test modules.
