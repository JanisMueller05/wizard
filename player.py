class Player:
    def __init__(self, name, points, karten_auf_der_hand, spielstil="normal"):
        self.name = name
        self.points = points
        self.karten_auf_der_hand = karten_auf_der_hand
        self.spielstil = spielstil
        stile = {
            "aggressiv": 0.9,
            "normal": 1.1
        }
        self.bewertungs_grenze = stile.get(spielstil, 1.1)

    def __str__(self):
        return f'{self.name}'
    def __repr__(self):
        return f'{self.name}'