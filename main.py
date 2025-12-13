from pandas.core.common import not_none

from card import Card
from player import Player
import numpy as np
import pandas as pd

rng = np.random.default_rng(seed=4)  # Zufallszahlengenerator mit Seed

colors = ["red", "green", "blue", "yellow"]

spielerliste = [
Player("Gregor_samsa", 0, []),
Player( "Billy_Bonka", 0, []),
Player("Testo_Torsten", 0, [])
]

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


def erstelle_punkte_tabelle(spieler_namen: list[str]) -> pd.DataFrame:
    """
    Erstellt eine leere Pandas DataFrame für die Punkte-Tabelle des Wizard-Spiels.
    """
    spalten = pd.MultiIndex.from_product([spieler_namen, ['Angesagt', 'Gemacht', 'Punkte']],
                                         names=['Spieler', 'Kategorie'])
    punkte_tabelle = pd.DataFrame(columns=spalten)
    punkte_tabelle.index.name = 'Runde'
    # Explizite Typ-Konvertierung, um NaN zu vermeiden
    return punkte_tabelle.astype('int64')


def fuege_runde_punkte_hinzu(punkte_tabelle: pd.DataFrame, runden_nummer: int,
                             runden_daten: dict[str, list[int]]) -> pd.DataFrame:
    """
    Fügt die Ergebnisse einer Spielrunde zur Punkte-Tabelle hinzu.
    """
    neue_runde = {}
    for spieler, daten in runden_daten.items():
        neue_runde[(spieler, 'Angesagt')] = daten[0]
        neue_runde[(spieler, 'Gemacht')] = daten[1]
        neue_runde[(spieler, 'Punkte')] = daten[2]
    punkte_tabelle.loc[runden_nummer] = neue_runde
    return punkte_tabelle


def berechne_gesamtpunkte(tabelle: pd.DataFrame) -> pd.DataFrame:
    """
    Fügt eine Zeile 'GESAMT' hinzu, welche die Summe aller 'Punkte' für jeden Spieler enthält.
    """
    gesamt_punkte_reihe = tabelle.xs('Punkte', level='Kategorie', axis=1).sum(axis=0)
    gesamt_reihe = {}
    for spieler in tabelle.columns.get_level_values('Spieler').unique():
        gesamt_reihe[(spieler, 'Angesagt')] = 0
        gesamt_reihe[(spieler, 'Gemacht')] = 0
        gesamt_reihe[(spieler, 'Punkte')] = gesamt_punkte_reihe[spieler]
        #gewinner_des_spiels(gesamt_reihe[(spieler, 'Punkte')])
    tabelle.loc['GESAMT'] = gesamt_reihe
    return tabelle, gesamt_punkte_reihe

def gewinner_des_spiels(gesamt_reihe):
    gewinner = gesamt_reihe.idxmax()
    punkte = gesamt_reihe.max()
    return gewinner, punkte


def print_tabelle(tabelle: pd.DataFrame):
    """
    Gibt die Pandas Punkte-Tabelle lesbar in der Konsole aus.
    """
    print(tabelle.to_string())



#SPIELLOGIK

def spiele_runde(spielerliste, runde, trumpf, tabelle, anzahl_runden):

    runden_daten = {}

    #Kartenausgabe & Ansagen
    for spieler in spielerliste:
        print("-----")
        print(f"Spieler: {spieler.name}")

        print(f"Karten auf der Hand ({len(spieler.karten_auf_der_hand)}): {spieler.karten_auf_der_hand}")
        print("-----")


        anzahl_angesagte_stiche = karten_bewerten(spieler.karten_auf_der_hand, trumpf, 1.5)
        print(f" -> Angesagte Stiche: {anzahl_angesagte_stiche}")

        runden_daten[spieler.name] = [
            anzahl_angesagte_stiche, 0, 0
        ]

    start_spieler_index = (runde % len(spielerliste)) - 1
    stich_gewinner = []

    for i in range(runde):

        gewinner = spiele_stich(spielerliste, start_spieler_index, trumpf, tabelle)
        stich_gewinner.append(gewinner)

        #bestimmt Index des letzten Gewinners
        gewinner_letzte_runde = next(
            (spieler for spieler in spielerliste if spieler.name == gewinner))
        start_spieler_index = spielerliste.index(gewinner_letzte_runde)


    for spieler in spielerliste:
        anzahl_gemachte_stiche = wie_viele_gemachte_stiche(spieler, stich_gewinner)
        anzahl_angesagte_stiche_alt = runden_daten[spieler.name][0]
        runden_daten[spieler.name] = [anzahl_angesagte_stiche_alt, anzahl_gemachte_stiche, 0]



    #Daten abspeichern
    for spieler, daten in runden_daten.items():
        anzahl_angesagte_stiche = daten[0]
        anzahl_gemachte_stiche = daten[1]


        if anzahl_angesagte_stiche == anzahl_gemachte_stiche:
            punkte = 20 + anzahl_gemachte_stiche * 10
        else:
            punkte = (abs(anzahl_angesagte_stiche - anzahl_gemachte_stiche)) * (-10)

        runden_daten[spieler] = [anzahl_angesagte_stiche, anzahl_gemachte_stiche, punkte]

    #Tabelle füllen und ausgeben
    tabelle = fuege_runde_punkte_hinzu(tabelle, runde, runden_daten)

    #Gesamtsumme hinzufügen, falls es die letzte Runde war
    if runde == anzahl_runden:
        tabelle, gesamt_punkte = berechne_gesamtpunkte(tabelle)
        print("\n🏆 ENDSTAND DES SPIELS (inkl. GESAMT) 🏆")
        print_tabelle(tabelle)
        gewinner, punkte = gewinner_des_spiels(gesamt_punkte)
        print(f" -> Gewinner ist: {gewinner} mit {punkte} Punkten.")
    else:
        print("\n-----------"
            f"ERGEBNISSE NACH RUNDE {runde}"
            "-----------")
        print_tabelle(tabelle)

    return tabelle


def starte_spiel(spielerliste, startrunde=1):

    runden_anzahl = wie_viele_runden_spielen_wir(len(spielerliste))
    spieler_namen_str = [spieler.name for spieler in spielerliste]
    tabelle = erstelle_punkte_tabelle(spieler_namen_str)

    print("\n===========================================")
    print(f"🃏 STARTE WIZARD-SPIEL mit {runden_anzahl} Runden 🃏")
    print("===========================================")

    for runde in range(startrunde, runden_anzahl + 1):
        print(f"\n====================== RUNDE {runde} ======================")

        karten = karten_mischen()

        # Kartenausteilen und Trumpf bestimmen
        restkarten = teile_karten_aus(karten, runde, spielerliste)
        trumpf = bestimme_trumpf(restkarten, runde)

        print(f"📢 Startspieler: {spielerliste[runde % len(spielerliste) - 1]}")
        print(f"👑 Trumpffarbe: {trumpf} | {runde} Karten pro Spieler")

        # spiele_runde führt Logik und Ausgabe durch
        tabelle = spiele_runde(spielerliste, runde, trumpf, tabelle, runden_anzahl)

    print("\n Das Spiel ist vorbei.")

def teile_karten_aus(karten, anzahl_karten, spielerliste):
    for i in range(anzahl_karten):
        for spieler in spielerliste:
            oberste_karte = karten.pop(0)
            spieler.karten_auf_der_hand.append(oberste_karte)

    return karten

def bestimme_trumpf(restkarten, runde):
    trumpf_karte = restkarten[0]  # oberste Karte aufdecken

    if trumpf_karte.color in colors:
        trumpf_farbe = trumpf_karte.color

    elif trumpf_karte.value == 0:
        trumpf_farbe = None

    elif trumpf_karte.value == 14:
        haeufigkeiten = {}
        start_spieler = spielerliste[(runde % len(spielerliste)) - 1]

        for karte in start_spieler.karten_auf_der_hand:
            farbe = karte.color
            if farbe:                                                   #ki
               haeufigkeiten[farbe] = haeufigkeiten.get(farbe,0) + 1

#Ersatztrumpf für Zauberer finden --> häufigste Farbe bei aggressiven Spielstil
        if haeufigkeiten:
           trumpf_farbe = max(haeufigkeiten, key=haeufigkeiten.get)  #ki

        else: trumpf_farbe = {rng.choice(colors)}

    return trumpf_farbe

def karten_bewerten(karten, trumpf_farbe, bewertungs_grenze):
    anzahl_stiche = 0
    anzahl_karten = len(karten)
    score = 0

    for karte in karten:

        if karte.value == 14:
            score += 2

        elif trumpf_farbe == None:
            score += (1.5 * karte.value) / anzahl_karten

        elif karte.color == trumpf_farbe:
            score += karte.value / anzahl_karten

        else:
            score += karte.value / (anzahl_karten * 2)

        #print(f'karte {karte}, score {score_karte}')

        if score > bewertungs_grenze:
            anzahl_stiche += 1
            score = 0

    return anzahl_stiche



def spiele_stich(spielerliste, start_spieler_index, trumpf_farbe, tabelle):
    stich_karten = {}
    bedien_farbe = ""

    for i in range(len(spielerliste)):

        aktiver_spieler = spielerliste[(start_spieler_index + i) % len(spielerliste)]
        #print(aktiver_spieler)

        # finde alle erlaubten Karten
        moegliche_karten = finde_erlaubte_karten_für_Zug(aktiver_spieler.karten_auf_der_hand, bedien_farbe)

        #prüfen, welche höchste karte ist und , ob meine ggf größer
        hoechste_karte = bestimme_hoechste_karte(stich_karten, bedien_farbe, trumpf_farbe)
        gelegte_karte = schlaue_karte_auswaehlen(moegliche_karten, hoechste_karte, bedien_farbe, trumpf_farbe)

        aktiver_spieler.karten_auf_der_hand.remove(gelegte_karte)
        stich_karten[aktiver_spieler.name] = gelegte_karte

        if bedien_farbe == "":
            bedien_farbe = gelegte_karte.color


    print(f"Der Stich: {stich_karten}")
    gewinner, karte = gewinner_des_stiches(stich_karten, bedien_farbe, trumpf_farbe)
    print(f"Gewinner des Stiches ist: {gewinner} mit {karte}")

    return gewinner



def schlaue_karte_auswaehlen(karten, hoechste_stich_karte, bedien_farbe, trumpf_farbe):

    if hoechste_stich_karte:

        bedien_karten = [
            karte for karte in karten if karte.color == bedien_farbe
        ]
        trumpf_karten = [
            karte for karte in karten if karte.color == trumpf_farbe
        ]
        normale_karten_ohne_trumpf = [
            karte for karte in karten if karte.color in colors and karte.color != trumpf_farbe
        ]
        sonder_karten = [
            karte for karte in karten if karte.color == ""
        ]


        hoechste_karte_farbe = hoechste_stich_karte.color
        hoechste_karte_wert = hoechste_stich_karte.value


        if hoechste_karte_wert == 14:
            if normale_karten_ohne_trumpf:
                gelegte_karte = min(normale_karten_ohne_trumpf, key=lambda karte: karte.value)
            else: gelegte_karte = min(karten, key=lambda karte: karte.value)
            return gelegte_karte


        if hoechste_karte_farbe == trumpf_farbe:
            for karte in trumpf_karten:
                if karte.value > hoechste_karte_wert:
                    gelegte_karte = karte
                    return gelegte_karte

            for karte in sonder_karten:
                if karte.value == 14:
                    gelegte_karte = karte
                    return gelegte_karte

            if normale_karten_ohne_trumpf:
                gelegte_karte = min(normale_karten_ohne_trumpf, key=lambda karte: karte.value)
            else: gelegte_karte = min(karten, key=lambda karte: karte.value)
            return gelegte_karte


        if hoechste_karte_farbe == bedien_farbe:
            if bedien_karten:
                for karte in bedien_karten:
                    if karte.value > hoechste_stich_karte.value:
                        gelegte_karte = karte
                    else: gelegte_karte = min(bedien_karten, key=lambda karte: karte.value)
                    return gelegte_karte

            if trumpf_karten:
                gelegte_karte = min(trumpf_karten, key=lambda karte: karte.value)
                return gelegte_karte

            for karte in sonder_karten:
                if karte.value == 14:
                    gelegte_karte = karte
                    return gelegte_karte

            if normale_karten_ohne_trumpf:
                gelegte_karte = min(normale_karten_ohne_trumpf, key=lambda karte: karte.value)
            else: gelegte_karte = min(karten, key=lambda karte: karte.value)
            return gelegte_karte


        if normale_karten_ohne_trumpf:
            gelegte_karte = max(normale_karten_ohne_trumpf, key=lambda karte: karte.value)
            return gelegte_karte

        if trumpf_karten:
            gelegte_karte = min(trumpf_karten, key=lambda karte: karte.value)
            return gelegte_karte


    gelegte_karte = max(karten, key=lambda karte: karte.value)

    return gelegte_karte


#Idee: Bestimme höchste karte. schaue ob ich noch stich machen will --> schaue ob noch größere karte.

       #nutze Funktion um größte karte zu finden erneut für gewinner



def finde_erlaubte_karten_für_Zug(karten, bedien_farbe):
    if bedien_farbe == "": 
        return karten

    bedien_farbe_karten = [karte for karte in karten if karte.color == bedien_farbe]
    if len(bedien_farbe_karten) == 0:
        return karten

    erlaubte_karten = [karte for karte in karten if karte.color == bedien_farbe or karte.color == ""]
    return erlaubte_karten


def bestimme_hoechste_karte(stich_karten, bedien_farbe, trumpf_farbe):
    alle_bedienkarten = []
    alle_trumpfkarten = []

    if stich_karten.items():

        for spieler, karte in stich_karten.items():

            if karte.value == 14:
                hoechste_karte = karte
                return hoechste_karte

            if karte.color == trumpf_farbe:
                alle_trumpfkarten.append(karte)

            if karte.color == bedien_farbe:
                alle_bedienkarten.append(karte)

        #for spieler, karte in stich_karten.items():
        if alle_trumpfkarten:
            hoechste_karte = max(alle_trumpfkarten, key=lambda karte: karte.value)
                #if karte.color == trumpf_farbe and karte.value == max(alle_trumpfkarten):
                    #hoechste_karte = karte
            return hoechste_karte

        if alle_bedienkarten:
            hoechste_karte = max(alle_bedienkarten, key=lambda karte: karte.value)
                #if karte.color == bedien_farbe and karte.value == max(alle_bedienkarten):
                    #hoechste_karte = karte
            return hoechste_karte

        hoechste_karte = 0

    return None


def gewinner_des_stiches(stich_karten, bedien_farbe, trumpf_farbe):
    hoechste_karte = bestimme_hoechste_karte(stich_karten, bedien_farbe, trumpf_farbe)
    for spieler, karte in stich_karten.items():
        if karte == hoechste_karte:
            return spieler, karte


def wie_viele_gemachte_stiche(spieler, stichgewinner):
    anzahl_gemachte_stiche = stichgewinner.count(spieler.name)
    return anzahl_gemachte_stiche



starte_spiel(spielerliste,1)
