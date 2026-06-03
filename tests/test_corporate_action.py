import pytest
from datetime import date, timedelta

from corporate_action_workflow_app.models.corporate_actions import CorporateAction, CorporateActionStatus

# -----------------------------------------------------------------------------
# INITIALIZATION & STATE TRANSITIONS
# -----------------------------------------------------------------------------


def test_corporate_action_initial_state():
    action = CorporateAction(action_type="DIVIDEND")
    assert action.status == CorporateActionStatus.RECEIVED
    assert action.action_type == "DIVIDEND"
    assert action.action_id is not None


def test_status_transitions():
    action = CorporateAction(action_type="DIVIDEND")

    action.mark_validated()
    assert action.status == CorporateActionStatus.VALIDATED

    action.mark_processing()
    assert action.status == CorporateActionStatus.PROCESSING

    action.mark_completed()
    assert action.status == CorporateActionStatus.COMPLETED


# -----------------------------------------------------------------------------
# VALIDATION: VALID CASES
# -----------------------------------------------------------------------------


def test_valid_dividend_action():
    action = CorporateAction(
        action_type="DIVIDEND",
        record_date=date.today(),
        payable_date=date.today() + timedelta(days=1),
        metadata={"amount": 1.23},
    )
    action.validate()  # should NOT raise


def test_valid_split_action():
    action = CorporateAction(
        action_type="SPLIT",
        metadata={"ratio": "2:1"},
    )
    action.validate()  # should NOT raise


# -----------------------------------------------------------------------------
# VALIDATION: INVALID ACTION TYPES
# -----------------------------------------------------------------------------


def test_invalid_action_type_empty():
    action = CorporateAction(action_type="")
    with pytest.raises(ValueError):
        action.validate()


def test_invalid_action_type_not_allowed():
    action = CorporateAction(action_type="UNKNOWN_TYPE")
    with pytest.raises(ValueError):
        action.validate()


# -----------------------------------------------------------------------------
# VALIDATION: INVALID DATES
# -----------------------------------------------------------------------------


def test_invalid_dates_payable_before_record():
    action = CorporateAction(
        action_type="DIVIDEND",
        record_date=date.today(),
        payable_date=date.today() - timedelta(days=1),
        metadata={"amount": 1.23},
    )
    with pytest.raises(ValueError):
        action.validate()


# -----------------------------------------------------------------------------
# VALIDATION: INVALID METADATA
# -----------------------------------------------------------------------------


def test_invalid_metadata_not_dict():
    action = CorporateAction(
        action_type="DIVIDEND",
        metadata="not a dict",
    )
    with pytest.raises(ValueError):
        action.validate()


def test_dividend_missing_amount():
    action = CorporateAction(
        action_type="DIVIDEND",
        metadata={},  # missing required 'amount'
    )
    with pytest.raises(ValueError):
        action.validate()
