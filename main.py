from card import Card
from player import Player
import numpy as np
import pandas as pd
from collections import deque

rng = np.random.default_rng(seed=4)  # Zufallszahlengenerator mit Seed

colors = ["red", "green", "blue", "yellow"]

def karten_mischen():
    karten = []
    for color in colors:
        karten.append(Card("",14))
        karten.append(Card("", 0))
        for value in range(13):
            karten.append(Card(color, value+1))
    rng.shuffle(karten)
    return karten

def wie_viele_runden_spielen_wir(spieler_anzahl):
    if spieler_anzahl == 3:
        return 9
    if spieler_anzahl == 4:
        return 15
    if spieler_anzahl == 5:
        return 12

    print("unzulaessige Spieleranzahl")
    return 0


def punkte_tabelle(spielerliste):
    runden_anzahl = wie_viele_runden_spielen_wir(len(spielerliste))
    runden_index = pd.Index(range(1,runden_anzahl+1), name = "Runde")
    metriken = ["Angesagt", "Gemacht", "Punkte"]
    multi_index_columns = pd.MultiIndex.from_product([spielerliste, metriken], names = ["Spieler", "Metriken"])
    Tabelle = pd.DataFrame(index=runden_index, columns=multi_index_columns)
    return Tabelle

def runden_zugehoerigkeit (spieler, runden_anzahl, spielerliste):
    try:
        start_offset = spielerliste.index(spieler)
    except ValueError:
        return []

    persoehnliche_runden = []
    for runde in range (1, runden_anzahl + 1):
        if (runde-1) % len(spielerliste) == start_offset:
            persoehnliche_runden.append(runde)

    return persoehnliche_runden

def starte_spiel(spielerliste, startrunde=1):
    runden_anzahl = wie_viele_runden_spielen_wir(len(spielerliste))
    tabelle = punkte_tabelle(spielerliste)


    for i in range(len(spielerliste)):
        spieler_name = spielerliste[i]
        runden_liste = runden_zugehoerigkeit(spieler_name, runden_anzahl, spielerliste)
        print(f"{spieler_name}: {runden_liste}")

    for runde in range(startrunde, runden_anzahl):
        karten = karten_mischen()

        print(f' \n Spieler {spielerliste[(runde-1)%len(spielerliste)]} sagt an')
        restkarten = teile_karten_aus(karten, runde, spielerliste)
        trumpf = bestimme_trumpf(restkarten)
        print(f" \n Runde: {runde}, Trumpffarbe: {trumpf}")
        spiele_runde(spielerliste, runde, restkarten)


        print("-----------"
              "Runde zuende"
              "-----------")

    print("Spiel vorbei")
    print(f"Punktetabelle: {tabelle}")


def spiele_runde(spielerliste, runde, restkarten):
    for spieler in spielerliste_deque:
        print("-----")
        print(spieler)
        print("-----")
        # 1. Karten bewerten
        karten_fuer_stiche = []

        anzahl_stiche = karten_bewerten(spieler.karten_auf_der_hand, bestimme_trumpf(restkarten), runde, karten_fuer_stiche,1.5)
        print(f" angesagte Stiche: {anzahl_stiche}")


        for karte in spieler.karten_auf_der_hand:
            # auswahl karte legen
            print(karte)

        erster_spieler = spielerliste_deque[0]
        karten_legen(spieler.karten_auf_der_hand, runde, gute_karten, spielerliste, erster_spieler)

        spieler.karten_auf_der_hand = []     #Karten auf der Hand leeren für die nächste Runde

    spielerliste_deque.rotate(-1)            #ki
    #karten_legen(runde, spielerliste, spielerliste_deque[0])



def teile_karten_aus(karten, anzahl_karten, spielerliste):
    for i in range(anzahl_karten):
        for spieler in spielerliste:
            oberste_karte = karten.pop(0)
            spieler.karten_auf_der_hand.append(oberste_karte)

    return karten

def bestimme_trumpf(restkarten):
    trumpf_karte = restkarten[0]  # oberste Karte aufdecken
    if trumpf_karte.color in colors:
        trumpf_farbe = trumpf_karte.color

    elif trumpf_karte.value == 0:
        trumpf_farbe = ["Narr"]

    elif trumpf_karte.value == 14:
        haeufigkeiten = {}
        start_spieler = spielerliste_deque[0]
        for karte in start_spieler.karten_auf_der_hand:
            farbe = karte.color
            haeufigkeiten[farbe] = haeufigkeiten.get(farbe,0) + 1

        haeufigste_farbe = max(haeufigkeiten, key=haeufigkeiten.get)
        trumpf_farbe = [haeufigste_farbe]
        #trumpf_farbe = rng.choice(colors)

    return trumpf_farbe

def karten_bewerten(karten, trumpf_farbe, runde, gute_karten, bewertungs_grenze):
    anzahl_stiche = 0
    anzahl_karten = len(karten)
    score = 0
    for karte in karten:

        if karte.value == 14:
            score += 2

        elif  karte.color == trumpf_farbe:
            score += karte.value / anzahl_karten

        else:
            score += karte.value / (anzahl_karten * 2)


        #print(f'karte {karte}, score {score}')
        if score > bewertungs_grenze:
            gute_karten.append(karte)
            anzahl_stiche += 1
            score = 0

    return anzahl_stiche, gute_karten

#def eintraege_punkte_tabelle(tabelle, aktuelle_runde, angesagte_stiche, gemachte_stiche, punkte):

def karten_legen (karten, anzahl_karten, gute_karten, spielerliste_deque, gewinner_letzte_runde):
    alle_gelegten_karten = []

    for i in range(anzahl_karten):
        karten_in_einer_runde = []
        #erste_karte = gewinner_letzte_runde.karten_auf_der_hand[0]
        #karten_in_einer_runde.append(erste_karte)
        #alle_gelegten_karten.append(erste_karte)
        #ersatz_trumpf = erste_karte.color
        ersatz_trumpf = rng.choice(colors)

        if ersatz_trumpf in colors:

            #spielerliste_deque.remove(gewinner_letzte_runde)
            for spieler in spielerliste_deque:
                legbare_karten = []
                for karte in spieler.karten_auf_der_hand:
                    if karte.color == ersatz_trumpf:
                        legbare_karten.append(karte)

                if max(legbare_karten) < max(karten_in_einer_runde) and max(legbare_karten) not in gute_karten:
                    gelegte_karte = max(legbare_karten)

                elif max(legbare_karten) < max(karten_in_einer_runde) and max(legbare_karten) in gute_karten:
                    pass



                else: gelegte_karte = rng.choice(karten)

                spieler.karten_auf_der_hand.remove(gelegte_karte)
                alle_gelegten_karten.append(gelegte_karte)
                karten_in_einer_runde.append(gelegte_karte)



        gewinner_karte = max(karten_in_einer_runde, key=lambda karten: karten.value)
        gewinner_letzte_runde = spielerliste_deque[karten_in_einer_runde.index(gewinner_karte)]
        print(karten_in_einer_runde)

    return print(alle_gelegten_karten)

#def beste_karte_aus_runde (karten, runde, spielerliste):
    #for i in range(len(spielerliste):
        #karten.value[i]


#continue schleife. 2. karte zur ersten. bedienen



spielerliste = [
Player("Gregor_samsa", 1337, []),
Player( "Billy_Bonka", 420, []),
Player("Testo_Torsten", 100, [])
]
spielerliste_deque = deque(spielerliste)
starte_spiel(spielerliste,1)

# brauche: karten legen funktion, punkte func, regel bedienen