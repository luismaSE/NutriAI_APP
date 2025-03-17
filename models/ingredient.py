from models.nutrient import Nutrient

class Ingredient:
    def __init__(self, name: str, weight: float, calories: float, protein: Nutrient, carbs: Nutrient, fibtg: Nutrient,
                 fasat: Nutrient, fat: Nutrient, na: Nutrient, chole: Nutrient, sugar: Nutrient) -> None:
        self.name = name
        self.quantity = 1.0
        self.weight = weight
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fibtg = fibtg
        self.fasat = fasat
        self.fat = fat
        self.na = na
        self.chole = chole
        self.sugar = sugar

    def __str__(self) -> str:
        return (
            f"\n{self.name} ({self.weight} g):\n"
            f" {self.calories} kcal\n"
            f" {self.protein}\n"
            f" {self.carbs}\n"
            f" {self.fibtg}\n"
            f" {self.fasat}\n"
            f" {self.fat}\n"
            f" {self.na}\n"
            f" {self.chole}\n"
            f" {self.sugar}"
        )

    def to_json(self):
        return {
            'name': self.name,
            'weight': self.weight,
            'calories': self.calories,
            'protein': self.protein.to_json(),
            'carbs': self.carbs.to_json(),
            'fibtg': self.fibtg.to_json(),
            'fasat': self.fasat.to_json(),
            'fat': self.fat.to_json(),
            'na': self.na.to_json(),
            'chole': self.chole.to_json(),
            'sugar': self.sugar.to_json()
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            data['name'],
            data['weight'],
            data['calories'],
            Nutrient.from_json(data['protein']),
            Nutrient.from_json(data['carbs']),
            Nutrient.from_json(data['fibtg']),
            Nutrient.from_json(data['fasat']),
            Nutrient.from_json(data['fat']),
            Nutrient.from_json(data['na']),
            Nutrient.from_json(data['chole']),
            Nutrient.from_json(data['sugar']),
        )