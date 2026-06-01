import tempfile
import json
from first_app.queue.persistent_queue import PersistentQueue


def make_test_queue():
    tmp = tempfile.TemporaryDirectory()
    store_path = f"{tmp.name}/actions.json"

    # Ensure the file exists and starts empty
    with open(store_path, "w") as f:
        json.dump([], f)

    queue = PersistentQueue(store_path)
    return queue, tmp
