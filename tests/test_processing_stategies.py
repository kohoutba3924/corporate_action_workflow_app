import pytest
from datetime import date

from first_app.models.corporate_actions import CorporateAction, CorporateActionStatus
from first_app.processor.strategies.dividend_processor import DividendProcessor
from first_app.processor.strategies.split_processor import SplitProcessor
from first_app.processor.strategies.merger_processor import MergerProcessor
from first_app.processor.strategy_factory import get_processor
from first_app.processor.action_processor import ActionProcessor
from tests.utils.queue_helpers import make_test_queue

# -----------------------------------------------------------------------------
# STRATEGY UNIT TESTS
# -----------------------------------------------------------------------------


def test_dividend_processor_applies_calculated_amount():
    action = CorporateAction(
        action_type="DIVIDEND",
        metadata={"amount": 5.0},
    )
    processor = DividendProcessor()
    processor.process(action)

    assert action.metadata["calculated_amount"] == 5.0


def test_split_processor_applies_ratio():
    action = CorporateAction(
        action_type="SPLIT",
        metadata={"ratio": "3:1"},
    )
    processor = SplitProcessor()
    processor.process(action)

    assert action.metadata["applied_ratio"] == "3:1"


def test_merger_processor_marks_merged():
    action = CorporateAction(
        action_type="MERGER",
        metadata={},
    )
    processor = MergerProcessor()
    processor.process(action)

    assert action.metadata["merged"] is True


# -----------------------------------------------------------------------------
# FACTORY TESTS
# -----------------------------------------------------------------------------


def test_factory_returns_dividend_processor():
    processor = get_processor("DIVIDEND")
    assert isinstance(processor, DividendProcessor)


def test_factory_returns_split_processor():
    processor = get_processor("SPLIT")
    assert isinstance(processor, SplitProcessor)


def test_factory_returns_merger_processor():
    processor = get_processor("MERGER")
    assert isinstance(processor, MergerProcessor)


def test_factory_raises_for_unknown_type():
    with pytest.raises(ValueError):
        get_processor("UNKNOWN_TYPE")


# -----------------------------------------------------------------------------
# PROCESSOR BRANCHING TESTS
# -----------------------------------------------------------------------------


def test_processor_routes_to_dividend_strategy():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    action = CorporateAction(
        action_type="DIVIDEND",
        metadata={"amount": 1.0},
        record_date=date.today(),
        payable_date=date.today(),
    )
    q.enqueue(action)

    processed = processor.process_next()
    assert processed is True

    stored = q.all()[0]
    assert stored.status == CorporateActionStatus.COMPLETED
    assert stored.metadata["calculated_amount"] == 1.0


def test_processor_routes_to_split_strategy():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    action = CorporateAction(
        action_type="SPLIT",
        metadata={"ratio": "2:1"},  # ratio is optional in your current domain model
    )
    q.enqueue(action)

    processed = processor.process_next()
    assert processed is True

    stored = q.all()[0]
    assert stored.status == CorporateActionStatus.COMPLETED
    assert stored.metadata["applied_ratio"] == "2:1"


def test_processor_routes_to_merger_strategy():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    action = CorporateAction(
        action_type="MERGER",
        metadata={},
    )
    q.enqueue(action)

    processed = processor.process_next()
    assert processed is True

    stored = q.all()[0]
    assert stored.status == CorporateActionStatus.COMPLETED
    assert stored.metadata["merged"] is True


# -----------------------------------------------------------------------------
# PROCESSOR FAILURE TESTS
# -----------------------------------------------------------------------------


def test_processor_fails_on_unknown_action_type():
    q, _ = make_test_queue()
    processor = ActionProcessor(q)

    action = CorporateAction(
        action_type="UNKNOWN",
        metadata={},
    )
    q.enqueue(action)

    processed = processor.process_next()
    assert processed is False

    stored = q.all()[0]
    assert stored.status == CorporateActionStatus.FAILED
