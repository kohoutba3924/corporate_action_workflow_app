from first_app.models.corporate_actions import CorporateAction, CorporateActionStatus
from first_app.persistence.json_store import JsonStore


class PersistentQueue:
    def __init__(self, filepath: str):
        self.store = JsonStore(filepath)

    # ------------------------------------------------------------------
    # Queue operations
    # ------------------------------------------------------------------

    def enqueue(self, action: CorporateAction):
        self.store.append(action)

    def dequeue(self) -> CorporateAction | None:
        actions = self.store.load_all()

        # Find first pending action
        for action in actions:
            if action.status == CorporateActionStatus.RECEIVED:
                return action

        return None

    def all(self) -> list[CorporateAction]:
        return self.store.load_all()

    def update(self, action: CorporateAction):
        self.store.update(action)

    # Convenience helpers
    def is_empty(self) -> bool:
        return all(a.status != CorporateActionStatus.RECEIVED for a in self.all())

    def size(self) -> int:
        return sum(1 for a in self.all() if a.status == CorporateActionStatus.RECEIVED)

    def peek(self) -> CorporateAction | None:
        actions = self.store.load_all()
        for action in actions:
            if action.status == CorporateActionStatus.RECEIVED:
                return action
        return None
