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

import pandas as pd
tab= pd.DataFrame({"Runde": [1,2,3], "Spieler" : ["karlo", "rese", "kaldap"], "Punkte": [0,10,15], "angesagt": [0,1,2], "gemacht":[2,3,5]})
print(tab)
f = tab.groupby(["Runde"])
print(f)
#pep=pd.pivot_table(index="Runde", columns="angesagt", values="Punkte", aggfunc="sum",fill_value=0, data=tab)
#print(pep)