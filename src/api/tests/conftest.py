import asyncio
import uuid
import motor
import pytest
from fastapi.testclient import TestClient
from todo.app import app, settings
from todo.models import TodoItem, TodoList


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


@pytest.fixture(autouse=True)
async def per_test_database():
    """Use a unique database per test to guarantee isolation."""
    unique_db = f"test_db_{uuid.uuid4().hex[:8]}"
    settings.AZURE_COSMOS_DATABASE_NAME = unique_db

    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.AZURE_COSMOS_CONNECTION_STRING
    )

    # Reset the app's DB client so it re-initializes against the new DB
    existing = getattr(app.state, "mongo_client", None)
    if existing is not None:
        try:
            existing.close()
        except Exception:
            pass
        app.state.mongo_client = None

    # Initialize Beanie/Mongo client with the new DB
    await app.startup_event()

    # Ensure collections are empty within the currently bound database
    try:
        await TodoItem.find_all().delete()
        await TodoList.find_all().delete()
    except Exception:
        # If deletion fails, tests will surface any remaining state
        pass

    yield

    # Cleanup: drop the unique DB
    await client.drop_database(unique_db)


@pytest.fixture()
def app_client(per_test_database):
    with TestClient(app) as client:
        # API-level cleanup to ensure no residual data
        try:
            lists_resp = client.get("/lists")
            if lists_resp.status_code == 200:
                for lst in lists_resp.json():
                    list_id = lst.get("id")
                    if not list_id:
                        continue
                    # Delete items first
                    items_resp = client.get(f"/lists/{list_id}/items")
                    if items_resp.status_code == 200:
                        for item in items_resp.json():
                            item_id = item.get("id")
                            if item_id:
                                client.delete(f"/lists/{list_id}/items/{item_id}")
                    # Then delete the list
                    client.delete(f"/lists/{list_id}")
        except Exception:
            # Best-effort cleanup; proceed to tests
            pass
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_database():
    """Session-level setup is handled per test; no-op here to reserve hook."""
    yield
