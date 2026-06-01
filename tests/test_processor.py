from datetime import date

from first_app.processor.action_processor import ActionProcessor
from first_app.models.corporate_actions import (
    CorporateAction,
    CorporateActionStatus,
)
from tests.utils.queue_helpers import make_test_queue


# Validate a valid corporate action object will be fully processed by the processor
def test_processor_completes_valid_action():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    action = CorporateAction(
        action_type="DIVIDEND",
        metadata={"amount": 1.23},  # required for DIVIDEND
        record_date=date.today(),
        payable_date=date.today(),
    )
    q.enqueue(action)

    processed = processor.process_next()
    assert processed is True

    # Reload from queue to get the persisted version
    stored = q.all()[0]
    assert stored.status == CorporateActionStatus.COMPLETED


# Validate that an invalid corporate action object will fail as expected
def test_processor_handles_validation_failure():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    # Missing action_type triggers validation failure
    action = CorporateAction(action_type="")
    q.enqueue(action)

    processed = processor.process_next()
    assert processed is False

    stored = q.all()[0]
    assert stored.status == CorporateActionStatus.FAILED


# Validate that the processor behaves as expected when provided an empty queue
def test_processor_returns_false_on_empty_queue():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    processed = processor.process_next()
    assert processed is False
