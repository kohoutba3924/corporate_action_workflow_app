import argparse
from datetime import date

from corporate_action_workflow_app.models.corporate_actions import CorporateAction
from corporate_action_workflow_app.processor.action_processor import ActionProcessor
from corporate_action_workflow_app.queue.persistent_queue import PersistentQueue

# Default persistence file
DEFAULT_STORE = "data/actions.json"


def build_parser():
    parser = argparse.ArgumentParser(description="Corporate Action Workflow Engine CLI")

    sub = parser.add_subparsers(dest="command")

    # ---------------------------------------------------------
    # add
    # ---------------------------------------------------------
    add_cmd = sub.add_parser("add", help="Add a new corporate action")
    add_cmd.add_argument(
        "--type", required=True, help="Action type (DIVIDEND, SPLIT, MERGER)"
    )
    add_cmd.add_argument("--amount", type=float, help="Dividend amount (for DIVIDEND)")
    add_cmd.add_argument("--ratio", help="Split ratio (for SPLIT)")
    add_cmd.add_argument("--record-date", help="Record date (YYYY-MM-DD)")
    add_cmd.add_argument("--payable-date", help="Payable date (YYYY-MM-DD)")

    # ---------------------------------------------------------
    # process
    # ---------------------------------------------------------
    sub.add_parser("process", help="Process the next pending action")

    # ---------------------------------------------------------
    # history
    # ---------------------------------------------------------
    sub.add_parser("history", help="List all actions in the system")

    # ---------------------------------------------------------
    # inspect
    # ---------------------------------------------------------
    inspect_cmd = sub.add_parser("inspect", help="Inspect a single action")
    inspect_cmd.add_argument("action_id", help="Action ID to inspect")

    # ---------------------------------------------------------
    # stats
    # ---------------------------------------------------------
    sub.add_parser("stats", help="Show action statistics")

    # ---------------------------------------------------------
    # clear
    # ---------------------------------------------------------
    sub.add_parser("clear", help="Clear all stored actions")

    return parser


def parse_date(value):
    if not value:
        return None
    return date.fromisoformat(value)


def handle_add(args, queue):
    metadata = {}

    if args.amount is not None:
        metadata["amount"] = args.amount

    if args.ratio:
        metadata["ratio"] = args.ratio

    action = CorporateAction(
        action_type=args.type,
        metadata=metadata,
        record_date=parse_date(args.record_date),
        payable_date=parse_date(args.payable_date),
    )

    queue.enqueue(action)
    print(f"Added action {action.action_id} ({action.action_type})")


def handle_process(queue):
    processor = ActionProcessor(queue)
    result = processor.process_next()

    if result:
        print("Processed next action successfully")
    else:
        print("No action processed (queue empty or failed)")


def handle_history(queue):
    actions = queue.all()

    if not actions:
        print("No actions found")
        return

    for a in actions:
        print(f"{a.action_id} | {a.action_type} | {a.status.value}")


def handle_inspect(args, queue):
    actions = queue.all()
    for a in actions:
        if a.action_id == args.action_id:
            print(a.to_dict())
            return

    print(f"No action found with ID {args.action_id}")


def handle_stats(queue):
    actions = queue.all()

    if not actions:
        print("No actions found")
        return

    counts = {}
    for a in actions:
        counts[a.status] = counts.get(a.status, 0) + 1

    print("Action statistics:")
    for status, count in counts.items():
        print(f"  {status.name}: {count}")


def handle_clear(queue):
    queue.store.save_all([])  # wipe file
    print("All actions cleared.")


def main():
    parser = build_parser()
    args = parser.parse_args()

    queue = PersistentQueue(DEFAULT_STORE)

    if args.command == "add":
        handle_add(args, queue)
    elif args.command == "process":
        handle_process(queue)
    elif args.command == "history":
        handle_history(queue)
    elif args.command == "inspect":
        handle_inspect(args, queue)
    elif args.command == "stats":
        handle_stats(queue)
    elif args.command == "clear":
        handle_clear(queue)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
