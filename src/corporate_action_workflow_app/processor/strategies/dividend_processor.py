class DividendProcessor:
    def process(self, action):
        amount = action.metadata.get("amount")

        # Simulated calculation — placeholder for real logic to demonstrate branching
        action.metadata["calculated_amount"] = amount
