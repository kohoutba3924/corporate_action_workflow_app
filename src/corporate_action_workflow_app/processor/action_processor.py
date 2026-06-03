from corporate_action_workflow_app.processor.strategy_factory import get_processor
from corporate_action_workflow_app.services.logging_service import log_transition
from corporate_action_workflow_app.services.validation import validate_action


class ActionProcessor:
    def __init__(self, queue):
        self.queue = queue

    def process_next(self) -> bool:
        action = self.queue.dequeue()
        if action is None:
            return False

        try:
            # 1. Validate
            validate_action(action)
            action.mark_validated()
            log_transition(action)
            self.queue.update(action)

            # 2. Process
            action.mark_processing()
            log_transition(action)
            self.queue.update(action)

            processor_strategy = get_processor(action.action_type)
            processor_strategy.process(action)

            # 3. Complete
            action.mark_completed()
            log_transition(action)
            self.queue.update(action)

        except Exception:
            action.mark_failed()
            log_transition(action)
            self.queue.update(action)
            return False

        return True
