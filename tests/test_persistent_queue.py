from datetime import date

from first_app.queue.persistent_queue import PersistentQueue
from first_app.models.corporate_actions import CorporateAction, CorporateActionStatus
from tests.utils.queue_helpers import make_test_queue


def test_persistent_queue_enqueue_and_load():
    q, _ = make_test_queue()

    action = CorporateAction(
        action_type="DIVIDEND",
        metadata={"amount": 1.0},
        record_date=date.today(),
        payable_date=date.today(),
    )

    q.enqueue(action)

    loaded = q.all()
    assert len(loaded) == 1
    assert loaded[0].action_id == action.action_id


def test_persistent_queue_dequeue_returns_pending():
    q, _ = make_test_queue()

    action = CorporateAction(action_type="DIVIDEND", metadata={"amount": 1.0})
    q.enqueue(action)

    dequeued = q.dequeue()
    assert dequeued.action_id == action.action_id


def test_persistent_queue_update_persists_changes():
    q, _ = make_test_queue()

    action = CorporateAction(action_type="DIVIDEND", metadata={"amount": 1.0})
    q.enqueue(action)

    action.mark_completed()
    q.update(action)

    loaded = q.all()
    assert loaded[0].status == CorporateActionStatus.COMPLETED
