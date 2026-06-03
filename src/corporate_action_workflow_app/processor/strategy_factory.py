from corporate_action_workflow_app.processor.strategies.dividend_processor import DividendProcessor
from corporate_action_workflow_app.processor.strategies.merger_processor import MergerProcessor
from corporate_action_workflow_app.processor.strategies.split_processor import SplitProcessor


def get_processor(action_type: str):
    action_type = action_type.upper()

    if action_type == "DIVIDEND":
        return DividendProcessor()
    if action_type == "SPLIT":
        return SplitProcessor()
    if action_type == "MERGER":
        return MergerProcessor()

    raise ValueError(f"No processor found for action type '{action_type}'")
