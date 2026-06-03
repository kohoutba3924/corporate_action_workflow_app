import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from typing import Optional


# Create stable corporate action processing states
class CorporateActionStatus(Enum):
    RECEIVED = auto()
    VALIDATED = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()


# Create the corporate action class datatype definition
@dataclass
class CorporateAction:
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = ""  # e.g., "DIVIDEND", "SPLIT", "MERGER"
    record_date: Optional[date] = None
    payable_date: Optional[date] = None
    status: CorporateActionStatus = CorporateActionStatus.RECEIVED
    metadata: dict = field(default_factory=dict)

    # Methods for setting and transitioning state
    def mark_validated(self):
        self.status = CorporateActionStatus.VALIDATED

    def mark_processing(self):
        self.status = CorporateActionStatus.PROCESSING

    def mark_completed(self):
        self.status = CorporateActionStatus.COMPLETED

    def mark_failed(self):
        self.status = CorporateActionStatus.FAILED

    # Allowed corporate action types
    ALLOWED_ACTION_TYPES = {"DIVIDEND", "SPLIT", "MERGER"}

    # Methods to enforce data domain business rules
    def validate(self):
        """Validate the corporate action before processing."""
        self._validate_action_type()
        self._validate_dates()
        self._validate_metadata()

    def _validate_action_type(self):
        if not self.action_type:
            raise ValueError("action_type is required")

        if self.action_type.upper() not in self.ALLOWED_ACTION_TYPES:
            allowed = ", ".join(self.ALLOWED_ACTION_TYPES)
            raise ValueError(
                f"Invalid action_type '{self.action_type}'. Allowed types: {allowed}"
            )

    def _validate_dates(self):
        # If both dates are provided, payable_date must be >= record_date
        if self.record_date and self.payable_date:
            if self.payable_date < self.record_date:
                raise ValueError("payable_date cannot be earlier than record_date")

    def _validate_metadata(self):
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

        # Example rule: dividends require an 'amount'
        if self.action_type.upper() == "DIVIDEND":
            if "amount" not in self.metadata:
                raise ValueError("DIVIDEND actions require metadata['amount']")

    # Methods to faciliate persistance
    def to_dict(self):
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "payable_date": (
                self.payable_date.isoformat() if self.payable_date else None
            ),
            "status": self.status.name,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            action_id=data["action_id"],
            action_type=data["action_type"],
            record_date=(
                date.fromisoformat(data["record_date"]) if data["record_date"] else None
            ),
            payable_date=(
                date.fromisoformat(data["payable_date"])
                if data["payable_date"]
                else None
            ),
            metadata=data.get("metadata", {}),
            status=CorporateActionStatus[data["status"]],
        )
