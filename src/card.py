class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        if self.value == 14:
            return "Zauberer"
        if self.value == 0:
            return "Narr"
        return f'{self.color} {self.value}'

    def __repr__(self):
        if self.color== "Wizard" or self.color == "Narr":
            # Für spezielle Karten wie den Wizard oder Narr
            return self.color
        else:
            # Für Standard-Spielkarten
            return f"{self.value} {self.color}"