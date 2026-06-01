from fastapi import FastAPI, HTTPException

from first_app.api.models import ActionCreate, ActionResponse
from first_app.models.corporate_actions import CorporateAction
from first_app.processor.action_processor import ActionProcessor
from first_app.queue.persistent_queue import PersistentQueue


def create_app(store_path: str = "data/actions.json") -> FastAPI:
    """
    Application factory for creating a FastAPI app instance.
    Allows injecting a custom store path for testing.
    """
    app = FastAPI(title="Corporate Action Workflow API")

    # Create queue + processor for this app instance
    queue = PersistentQueue(store_path)
    processor = ActionProcessor(queue)

    # Attach to app.state so routes can access them
    app.state.queue = queue
    app.state.processor = processor

    # ---------------------------------------------------------
    # POST /actions  (create)
    # ---------------------------------------------------------
    @app.post("/actions", response_model=ActionResponse)
    def create_action(payload: ActionCreate):

        action = CorporateAction(
            action_type=payload.action_type,
            metadata=payload.metadata,  # <-- direct metadata pass-through
            record_date=payload.record_date,
            payable_date=payload.payable_date,
        )

        app.state.queue.enqueue(action)
        return ActionResponse(**action.to_dict())

    # ---------------------------------------------------------
    # POST /actions/process
    # ---------------------------------------------------------
    @app.post("/actions/process")
    def process_next():
        result = app.state.processor.process_next()
        return {"processed": result}

    # ---------------------------------------------------------
    # GET /actions
    # ---------------------------------------------------------
    @app.get("/actions", response_model=list[ActionResponse])
    def list_actions():
        actions = app.state.queue.all()
        return [ActionResponse(**a.to_dict()) for a in actions]

    # ---------------------------------------------------------
    # GET /actions/{action_id}
    # ---------------------------------------------------------
    @app.get("/actions/{action_id}", response_model=ActionResponse)
    def inspect_action(action_id: str):
        for a in app.state.queue.all():
            if a.action_id == action_id:
                return ActionResponse(**a.to_dict())

        raise HTTPException(status_code=404, detail="Action not found")

    # ---------------------------------------------------------
    # GET /stats
    # ---------------------------------------------------------
    @app.get("/stats")
    def stats():
        actions = app.state.queue.all()
        counts = {}

        for a in actions:
            counts[a.status.name] = counts.get(a.status.name, 0) + 1

        return counts

    # ---------------------------------------------------------
    # DELETE /actions
    # ---------------------------------------------------------
    @app.delete("/actions")
    def clear_actions():
        app.state.queue.store.save_all([])
        return {"cleared": True}

    return app


# Default app for Uvicorn
app = create_app()
