from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel, Field


class ActionCreate(BaseModel):
    action_type: str
    metadata: Dict = Field(default_factory=dict)
    record_date: Optional[date] = None
    payable_date: Optional[date] = None


class ActionResponse(BaseModel):
    action_id: str
    action_type: str
    status: str
    record_date: Optional[date]
    payable_date: Optional[date]
    metadata: Dict
