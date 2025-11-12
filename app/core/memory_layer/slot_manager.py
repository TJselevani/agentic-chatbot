class SlotManager:
    def __init__(self):
        self.slots = {}
        self.required_slots = {
            "book_vehicle": ["pickup", "dropoff", "vehicle_type"]
        }

    def get_missing_slots(self, intent: str):
        """Return which slots are still missing for a given intent."""
        required = self.required_slots.get(intent, [])
        filled = self.slots.get(intent, {})
        return [slot for slot in required if slot not in filled or not filled[slot]]

    def update_slot(self, intent: str, slot_name: str, slot_value: str):
        """Save collected slot information."""
        if intent not in self.slots:
            self.slots[intent] = {}
        self.slots[intent][slot_name] = slot_value

    def get_filled_slots(self, intent: str):
        """Return all filled slots for an intent."""
        return self.slots.get(intent, {})
