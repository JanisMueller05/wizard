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
        spiele_runde(spielerliste_deque, runde, restkarten, trumpf)


        print("-----------"
              "Runde zuende"
              "-----------")

    print("Spiel vorbei")
    print(f"Punktetabelle: {tabelle}")


def spiele_runde(spielerliste, runde, restkarten, trumpf):
    beste_karten = {}
    for spieler in spielerliste_deque:
        print("-----")
        print(spieler)
        print("-----")
        # 1. Karten bewerten
        #karten_fuer_stiche = []

        anzahl_stiche, gute_karten_fuer_spieler = karten_bewerten(spieler.karten_auf_der_hand, bestimme_trumpf(restkarten), runde,1.5)
        print(f" angesagte Stiche: {anzahl_stiche}")

        beste_karten[spieler] = gute_karten_fuer_spieler


        #for karte in spieler.karten_auf_der_hand:
            # auswahl karte legen
            #print(karte)

        spieler.karten_auf_der_hand = []     #Karten auf der Hand leeren für die nächste Runde

    #beste_karten.append(gute_karten)
    #erster_spieler = spielerliste_deque[0]
    # karten_legen(spieler.karten_auf_der_hand, runde, beste_karten, trumpf, spielerliste_deque)
    spielerliste_deque.rotate(-1)      #ki


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
        trumpf_farbe = "Narr"

    elif trumpf_karte.value == 14:
        haeufigkeiten = {}
        start_spieler = spielerliste_deque[0]

        for karte in start_spieler.karten_auf_der_hand:
            farbe = karte.color
            if farbe:                                                   #ki
               haeufigkeiten[farbe] = haeufigkeiten.get(farbe,0) + 1

        if haeufigkeiten:
           haeufigste_farbe = max(haeufigkeiten, key=haeufigkeiten.get)  #ki
           trumpf_farbe = print(f' Ersatztrumpf für Zauberer: {haeufigste_farbe}')

        else: trumpf_farbe = print(f' Ersatztrumpf für Zauberer: {rng.choice(colors)}')

    return trumpf_farbe

def karten_bewerten(karten, trumpf_farbe, runde, bewertungs_grenze):
    anzahl_stiche = 0
    anzahl_karten = len(karten)
    score = 0
    gute_karten = []
    for karte in karten:

        if karte.value == 14:
            score_karte = 2

        elif  karte.color == trumpf_farbe:
            score_karte = karte.value / anzahl_karten

        else:
            score_karte = karte.value / (anzahl_karten * 2)

        if score_karte >= 1:
            gute_karten.append(karte)

        score += score_karte

        print(f'karte {karte}, score {score_karte}')

        if score > bewertungs_grenze:
            anzahl_stiche += 1
            score = 0
    #for karte in gute_karten:
        #print(f'Die guten: {karte}')

    return anzahl_stiche, gute_karten


#def eintraege_punkte_tabelle(tabelle, aktuelle_runde, angesagte_stiche, gemachte_stiche, punkte):

def karten_legen (karten, anzahl_karten, gute_karten, trumpf_farbe, spielerliste):
    alle_gelegten_karten = []

    for i in range(anzahl_karten):
        karten_in_diesem_stich = []
        if i == 1:
            gewinner_letzte_runde = spielerliste[0]

        for karte in gewinner_letzte_runde.karten_auf_der_hand:
            if karte.value == 13:
               erste_karte = karte
            else:
                #if min(gewinner_letzte_runde.karten_auf_der_hand) != 0:
                    #erste_karte = min(gewinner_letzte_runde.karten_auf_der_hand)
                #else:
                erste_karte = gewinner_letzte_runde.karten_auf_der_hand.pop(0)
        karten_in_diesem_stich.append(erste_karte.value)
        #alle_gelegten_karten.append(erste_karte)
        bedien_farbe = erste_karte.color
        #ersatz_trumpf = rng.choice(colors)
        #spielerliste.remove(gewinner_letzte_runde)

        if bedien_farbe in colors:
            for spieler in spielerliste:
                if spieler == gewinner_letzte_runde:
                    continue
                normale_legbare_karten = []
                aktuelle_gute_karten = gute_karten[spieler]
                for karte in spieler.karten_auf_der_hand:
                    if karte.color == bedien_farbe:
                        normale_legbare_karten.append(karte.value)

                    alle_legbaren_karten = normale_legbare_karten.copy()
                    if karte == 0|14:
                        alle_legbaren_karten.append(karte)

                if normale_legbare_karten == []:
                    normale_legbaren_karten = spieler.karten_auf_der_hand

                #if max(normale_legbare_karten) > max(karten_in_diesem_stich) :
                    #gelegte_karte = max(normale_legbare_karten)

                #elif max(normale_legbare_karten) < max(karten_in_diesem_stich) and max(normale_legbare_karten) in aktuelle_gute_karten:

                    #if max(alle_legbaren_karten) == 14 and 14 not in karten_in_diesem_stich:
                          #gelegte_karte = max(alle_legbaren_karten)

                    #elif: min(alle_legbaren_karten) == 0
                        #gelegte_karte = min(alle_legbaren_karten)

                    #else: gelegte_karte = min(normale_legbare_karten)

                #else: gelegte_karte = min(normale_legbare_karten)


                #spieler.karten_auf_der_hand.remove(gelegte_karte)
                #alle_gelegten_karten.append(gelegte_karte)
                #karten_in_diesem_stich.append(gelegte_karte)



        gewinner_karte = max(karten_in_diesem_stich, key=lambda karten: karten.value)     #ki
        gewinner_letzte_runde = spielerliste_deque[karten_in_diesem_stich.index(gewinner_karte)]
        print(karten_in_diesem_stich)

    #return alle_gelegten_karten

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

# brauche: , punkte func