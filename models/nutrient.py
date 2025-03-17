class Nutrient:
    def __init__(self, label: str, quantity: float, unit: str) -> None:
        self.name = label
        self.quantity = quantity
        self.unit = unit

    def __str__(self) -> str:
        return f"{self.name}: {self.quantity} {self.unit}"

    def to_json(self):
        return {
            'label': self.name,
            'quantity': self.quantity,
            'unit': self.unit
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(data['label'], data['quantity'], data['unit'])