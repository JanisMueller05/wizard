class Player:
    def __init__(self, name, points, karten_auf_der_hand):
        self.name = name
        self.points = points
        self.karten_auf_der_hand = karten_auf_der_hand
    def __str__(self):
        return f'{self.name} {self.points}'