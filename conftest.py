import datetime
import json
import logging
import os
from logging.handlers import RotatingFileHandler
import pytest
from core.api_client import ApiClient
from core.logger import get_logger, set_logger_name


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev")


@pytest.fixture(scope="session", autouse=True)
def config():
    base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, "config.json")

    with open(config_path, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session", autouse=True)
def logger(config):

    # Folder where logs will be stored
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "main")
    logfile = os.path.join(log_dir, f"session-{worker_id}-{ts}.txt")

    set_logger_name(config.get("logger_name", "session"))
    logger = get_logger()

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    DATEFMT = "%Y-%m-%d %H:%M:%S"

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(FORMAT, DATEFMT))
        logger.addHandler(console)

    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        file = RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=3)
        file.setLevel(logging.DEBUG)
        file.setFormatter(logging.Formatter(FORMAT, DATEFMT))
        logger.addHandler(file)

    print(f"\nLog file: {logfile}\n")

    logger.info("=" * 80)
    logger.info("Pytest Session Started")
    logger.info(f"Log file: {logfile}")
    logger.info("=" * 80)

    yield logger

    logger.info("=" * 80)
    logger.info("Pytest Session Finished")
    logger.info("=" * 80)

@pytest.fixture
def setup(config, request):
    env = request.config.getoption("--env")
    env_config = config.get(env, config["dev"])
    url = env_config["base_url"]
    api_client = ApiClient(url)
    return api_client


@pytest.fixture
def test_data(request, config):
    file_name = request.fspath.basename
    feature_name = file_name.split("_")[0]

    test_name = request.function.__name__

    test_data_file_name = feature_name + "_test_data.json"
    test_folder_path = os.path.join(os.path.dirname(__file__), config["test_data_folder_path"])
    test_file_path = os.path.join(test_folder_path, test_data_file_name)
    with open(test_file_path, "r") as f:
        testcases = json.load(f)
    for testcase in testcases:
        if testcase["test_name"] == test_name:
            return testcase
    raise Exception(f"Test case {test_name} not found in the test data file {test_data_file_name}")


@pytest.fixture
def test_context(setup, test_data, config):
    return {
        "setup": setup,
        "test_data": test_data,
        "config": config
    }


@pytest.fixture
def get_schema_folder_path(request, test_context):

    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        test_context["config"]["json_schema_folder_path"], request.fspath.basename.split("_")[0],
        test_context["test_data"]["json_schema"])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):

    logger = logging.getLogger()
    logger.info(f"START: {item.nodeid}")
    yield
    logger.info(f"END: {item.nodeid}")
