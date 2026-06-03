class SplitProcessor:
    def process(self, action):
        # Simulated calculation — placeholder for real logic to demonstrate branching
        ratio = action.metadata.get("ratio", "1:1")
        action.metadata["applied_ratio"] = ratio
