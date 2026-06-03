from corporate_action_workflow_app.models.corporate_actions import CorporateAction
from tests.utils.queue_helpers import make_test_queue


# Validates adding a corporate action to the queue works as expected
def test_enqueue_and_size():
    q, _ = make_test_queue()
    action = CorporateAction(action_type="DIVIDEND", metadata={"amount": 1.0})

    q.enqueue(action)

    assert q.size() == 1
    assert not q.is_empty()


# Validates that corporate actions added to the queue are stored and processed in the expected order
def test_dequeue_returns_items_in_order():
    q, _ = make_test_queue()
    a1 = CorporateAction(action_type="DIVIDEND", metadata={"amount": 1.0})
    a2 = CorporateAction(action_type="SPLIT", metadata={"ratio": "2:1"})

    q.enqueue(a1)
    q.enqueue(a2)

    first = q.dequeue()
    assert first.action_id == a1.action_id

    # Mark the first action as processed so the next RECEIVED is a2
    first.mark_processing()
    q.update(first)

    second = q.dequeue()
    assert second.action_id == a2.action_id

    second.mark_processing()
    q.update(second)

    assert q.is_empty()


# Validates that peek() functions as expected and does not modify the queue order
def test_peek_does_not_remove_item():
    q, _ = make_test_queue()
    action = CorporateAction(action_type="DIVIDEND", metadata={"amount": 1.0})

    q.enqueue(action)

    peeked = q.peek()
    assert peeked.action_id == action.action_id
    assert q.size() == 1
