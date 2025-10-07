import asyncio

import motor
import pytest
from fastapi.testclient import TestClient
from blog.app import app, settings

TEST_DB_NAME = "test_db"


@pytest.fixture(scope="session")
def event_loop():
    """
    Redefine the event_loop fixture to be session scoped.
    Requirement of pytest-asyncio if there are async fixtures
    with non-function scope.
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


@pytest.fixture()
def app_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_database():
    settings.AZURE_COSMOS_DATABASE_NAME = TEST_DB_NAME
    # Attempt a short-lived connection to the configured Mongo/Cosmos DB.
    # If the DB is unreachable (auth/network), skip tests to avoid hard failures
    # during local development where the cloud DB may not be accessible.
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.AZURE_COSMOS_CONNECTION_STRING,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        # Try a lightweight command to validate connectivity/auth
        await mongo_client.admin.command("ping")
    except Exception as e:
        import pytest as _pytest

        _pytest.skip(f"Skipping DB tests because Mongo/Cosmos is unreachable: {e}")

    # If we get here, DB is reachable; drop the test database to ensure a clean slate
    try:
        await mongo_client.drop_database(TEST_DB_NAME)
    except Exception:
        # ignore drop errors
        pass

    yield

    try:
        await mongo_client.drop_database(TEST_DB_NAME)
    except Exception:
        pass
