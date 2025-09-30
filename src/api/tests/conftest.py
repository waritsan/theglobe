import asyncio

import pytest
from fastapi.testclient import TestClient
from todo.app import app


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
    """
    Provide a TestClient and proactively clear any pre-existing data
    via the public API to ensure each test starts from a clean state.
    """
    with TestClient(app) as client:
        # Best-effort cleanup: remove any existing items and lists
        try:
            lists_resp = client.get("/lists")
            if lists_resp.status_code == 200:
                for lst in lists_resp.json():
                    list_id = lst.get("id")
                    if not list_id:
                        continue
                    # Delete items for the list (if any)
                    items_resp = client.get(f"/lists/{list_id}/items")
                    if items_resp.status_code == 200:
                        for item in items_resp.json():
                            item_id = item.get("id")
                            if item_id:
                                client.delete(f"/lists/{list_id}/items/{item_id}")
                    # Delete the list itself
                    client.delete(f"/lists/{list_id}")
        except Exception:
            # If cleanup fails, continue; tests will still run
            pass
        yield client
