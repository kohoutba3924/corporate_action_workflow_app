import json
from pathlib import Path

from corporate_action_workflow_app.models.corporate_actions import CorporateAction


class JsonStore:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        if not self.filepath.exists():
            self.filepath.write_text("[]")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_raw(self) -> list[dict]:
        with self.filepath.open("r") as f:
            return json.load(f)

    def _save_raw(self, data: list[dict]):
        with self.filepath.open("w") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> list[CorporateAction]:
        raw = self._load_raw()
        return [CorporateAction.from_dict(item) for item in raw]

    def save_all(self, actions: list[CorporateAction]):
        raw = [a.to_dict() for a in actions]
        self._save_raw(raw)

    def append(self, action: CorporateAction):
        raw = self._load_raw()
        raw.append(action.to_dict())
        self._save_raw(raw)

    def update(self, action: CorporateAction):
        raw = self._load_raw()
        for idx, item in enumerate(raw):
            if item["action_id"] == action.action_id:
                raw[idx] = action.to_dict()
                break
        self._save_raw(raw)
