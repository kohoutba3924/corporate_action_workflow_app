import json
import tempfile
from fastapi.testclient import TestClient
from corporate_action_workflow_app.api.app import create_app


def make_client():
    """
    Creates a TestClient with a temporary JSON store.
    Returns (client, store_path) so tests can inspect the file if needed.
    """
    tmp = tempfile.TemporaryDirectory()
    store_path = f"{tmp.name}/actions.json"

    # Create empty file so PersistentQueue doesn't fail on first load
    with open(store_path, "w") as f:
        json.dump([], f)

    app = create_app(store_path)
    client = TestClient(app)
    return client, store_path, tmp


# ---------------------------------------------------------
# POST /actions
# ---------------------------------------------------------
def test_create_action_minimal():
    client, _, _ = make_client()

    response = client.post("/actions", json={"action_type": "SPLIT"})
    assert response.status_code == 200

    data = response.json()
    assert data["action_type"] == "SPLIT"
    assert data["status"] == "RECEIVED"
    assert data["metadata"] == {}


def test_create_action_with_metadata():
    client, _, _ = make_client()

    response = client.post(
        "/actions",
        json={"action_type": "DIVIDEND", "metadata": {"amount": 1.23}},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["metadata"]["amount"] == 1.23


# ---------------------------------------------------------
# POST /actions/process
# ---------------------------------------------------------
def test_process_action():
    client, store_path, _ = make_client()

    # Create action
    client.post(
        "/actions",
        json={"action_type": "DIVIDEND", "metadata": {"amount": 4.22}},
    )

    # Process it
    response = client.post("/actions/process")
    assert response.status_code == 200
    assert response.json()["processed"] is True

    # Verify status updated in store
    with open(store_path) as f:
        stored = json.load(f)
    assert stored[0]["status"] == "COMPLETED"


def test_process_empty_queue():
    client, _, _ = make_client()

    response = client.post("/actions/process")
    assert response.status_code == 200
    assert response.json()["processed"] is False


# ---------------------------------------------------------
# GET /actions
# ---------------------------------------------------------
def test_list_actions():
    client, _, _ = make_client()

    client.post(
        "/actions",
        json={"action_type": "DIVIDEND", "metadata": {"amount": 3.45}},
    )
    client.post("/actions", json={"action_type": "SPLIT"})

    response = client.get("/actions")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {a["action_type"] for a in data} == {"DIVIDEND", "SPLIT"}


# ---------------------------------------------------------
# GET /actions/{action_id}
# ---------------------------------------------------------
def test_inspect_action():
    client, _, _ = make_client()

    create_resp = client.post(
        "/actions",
        json={"action_type": "DIVIDEND", "metadata": {"amount": 3.15}},
    )
    action_id = create_resp.json()["action_id"]

    response = client.get(f"/actions/{action_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["action_id"] == action_id
    assert data["action_type"] == "DIVIDEND"


def test_inspect_action_not_found():
    client, _, _ = make_client()

    response = client.get("/actions/DOES_NOT_EXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "Action not found"


# ---------------------------------------------------------
# GET /stats
# ---------------------------------------------------------
def test_stats():
    client, _, _ = make_client()

    # Create 2 actions
    client.post(
        "/actions",
        json={"action_type": "DIVIDEND", "metadata": {"amount": 5.55}},
    )
    client.post("/actions", json={"action_type": "SPLIT"})

    # Process one
    client.post("/actions/process")

    response = client.get("/stats")
    assert response.status_code == 200

    stats = response.json()
    assert stats["COMPLETED"] == 1
    assert stats["RECEIVED"] == 1


# ---------------------------------------------------------
# DELETE /actions
# ---------------------------------------------------------
def test_clear_actions():
    client, store_path, _ = make_client()

    client.post("/actions", json={"action_type": "DIVIDEND"})
    client.post("/actions", json={"action_type": "SPLIT"})

    response = client.delete("/actions")
    assert response.status_code == 200
    assert response.json()["cleared"] is True

    # Verify file is empty
    with open(store_path) as f:
        stored = json.load(f)
    assert stored == []
