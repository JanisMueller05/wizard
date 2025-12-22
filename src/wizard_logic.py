from src.card import Card
from src.player import Player
import json
import numpy as np
import pandas as pd
import datetime
import math
import os

pd.set_option('display.max_columns', None)          # Verhindert, dass Spalten mit "..." abgekürzt werden
pd.set_option('display.width', 5000)                # Erlaubt eine sehr breite Darstellung im Terminal
pd.set_option('display.colheader_justify', 'center') # Zentriert die Überschriften über den Daten


rng = np.random.default_rng(seed=42)  # Zufallszahlengenerator mit Seed

colors = ["red", "green", "blue", "yellow"]

def lade_spieler_aus_config():
    # 1. Die passive Textdatei öffnen
    with open("configs/players.json", "r", encoding="utf-8") as f:
        daten = json.load(f)  # Macht aus dem Text ein Dictionary

    # 2. Aus dem Text echte Python-Objekte bauen
    spieler_objekte = []
    for s in daten["spieler"]:
        # Hier rufen wir deine Player-Klasse auf
        neuer_spieler = Player(s["name"], 0, [], spielstil=s["spielstil"])
        spieler_objekte.append(neuer_spieler)

    return spieler_objekte



gewinner_liste = []

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
        return 20
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

#ki
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
    gewinner_liste.append(gewinner)
    return gewinner, punkte


def print_tabelle(tabelle: pd.DataFrame):
    #Gibt die Pandas Punkte-Tabelle lesbar in der Konsole aus.
    print(tabelle.to_string())


#SPIELLOGIK

def spiele_runde(runde, trumpf, tabelle, anzahl_runden, spielerliste):

    runden_daten = {}

    #Kartenausgabe & Ansagen
    for spieler in spielerliste:
        #print("-----")
        #print(f"Spieler: {spieler.name}")

        #print(f"Karten auf der Hand ({len(spieler.karten_auf_der_hand)}): {spieler.karten_auf_der_hand}")
        #print("-----")


        anzahl_angesagte_stiche = karten_bewerten(spieler.karten_auf_der_hand, trumpf, spielerliste, runde, spieler.spielstil)
        #print(f" -> Angesagte Stiche: {anzahl_angesagte_stiche}")

        runden_daten[spieler.name] = [
            anzahl_angesagte_stiche, 0, 0
        ]
        # Vorläufiges Speichern der Ansagen, damit spiele_stich darauf zugreifen kann
        tabelle = fuege_runde_punkte_hinzu(tabelle, runde, runden_daten)


    stich_gewinner = []

    stiche_dieser_runde = {spieler.name: 0 for spieler in spielerliste}
    start_spieler_index = (runde % len(spielerliste)) - 1

    for i in range(runde):

        gewinner = spiele_stich(spielerliste, start_spieler_index, trumpf, runde, tabelle, stiche_dieser_runde)

        stich_gewinner.append(gewinner)
        stiche_dieser_runde[gewinner] += 1

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
    tabelle = tabelle.fillna(0).astype(int)

    #Gesamtsumme hinzufügen, falls es die letzte Runde war
    if runde == anzahl_runden:
        tabelle, gesamt_punkte = berechne_gesamtpunkte(tabelle)
        #print("\n ENDSTAND DES SPIELS (inkl. GESAMT) 🏆")
        print_tabelle(tabelle)
        gewinner, punkte = gewinner_des_spiels(gesamt_punkte)
        #print(f" -> Gewinner ist: {gewinner} mit {punkte} Punkten.")
    #else:
        #print("\n-----------"
        #    f"ERGEBNISSE NACH RUNDE {runde}"
         #   "-----------")
        #print_tabelle(tabelle)

    return tabelle


def starte_spiel(startrunde, spielerliste):

    runden_anzahl = wie_viele_runden_spielen_wir(len(spielerliste))
    spieler_namen_str = [spieler.name for spieler in spielerliste]
    tabelle = erstelle_punkte_tabelle(spieler_namen_str)

    #print("\n===========================================")
    #print(f"🃏 STARTE WIZARD-SPIEL mit {runden_anzahl} Runden 🃏")
    #print("===========================================")

    for runde in range(startrunde, runden_anzahl + 1):
        #print(f"\n====================== RUNDE {runde} ======================")

        #karten mischen
        karten = karten_mischen()

        # Kartenausteilen und Trumpf bestimmen
        restkarten = teile_karten_aus(karten, runde, spielerliste)
        trumpf = bestimme_trumpf(restkarten, runde, spielerliste)

        #print(f" Startspieler: {spielerliste[runde % len(spielerliste) - 1]}")
        #print(f" Trumpffarbe: {trumpf} | {runde} Karten pro Spieler")


        tabelle = spiele_runde(runde, trumpf, tabelle, runden_anzahl, spielerliste)


    #print("\n Das Spiel ist vorbei.")



def teile_karten_aus(karten, anzahl_karten, spielerliste):
    for i in range(anzahl_karten):
        for spieler in spielerliste:
            oberste_karte = karten.pop(0)
            spieler.karten_auf_der_hand.append(oberste_karte)

    return karten

def bestimme_trumpf(restkarten, runde, spielerliste):
    if restkarten:
        trumpf_karte = restkarten[0]  # oberste Karte aufdecken
    else:
        return None

    if trumpf_karte.color in colors:
        trumpf_farbe = trumpf_karte.color

    elif trumpf_karte.value == 0:
        trumpf_farbe = None

    elif trumpf_karte.value == 14:
        haeufigkeiten = {farbe: 0 for farbe in colors}
        start_spieler = spielerliste[(runde % len(spielerliste)) - 1]


        for karte in start_spieler.karten_auf_der_hand:
            farbe = karte.color
            if farbe in colors:                                                   #ki
               haeufigkeiten[farbe] = haeufigkeiten.get(farbe,0) + 1

        #Ersatztrumpf für Zauberer finden --> häufigste Farbe bei aggressiven Spielstil

        if start_spieler.spielstil == "aggressiv":
            trumpf_farbe = max(haeufigkeiten, key=haeufigkeiten.get)  #ki
        else: trumpf_farbe = min(haeufigkeiten, key=haeufigkeiten.get)

    return trumpf_farbe


def karten_bewerten(karten, trumpf_farbe, spielerliste, runde, spielstil):
    anzahl_spieler = len(spielerliste)
    total_prob = 0

    for karte in karten:
        prob = 0  # Wahrscheinlichkeit, dass diese Karte einen Stich macht

        if karte.value == 14:
            prob = 0.95

        elif karte.value == 0:
            prob = 0.05

        elif karte.color == trumpf_farbe:
            # Wertigkeit im Verhältnis zu den Spielern
            prob = (karte.value / 13) * 0.8
            if runde < 5:
                prob += 0.1
            if karte.value > 10: prob += 0.15


        else:
            # Je mehr Spieler, desto wahrscheinlicher wird die Farbe gestochen (Trumpf oder höher)
            basis_prob = (karte.value / 13)
            # Risiko-Skalierung: Bei vielen Spielern sinkt die Chance einer normalen Karte extrem
            spieler_malus = 0.75 ** (anzahl_spieler - 1)
            prob = basis_prob * spieler_malus

            # In hohen Runden (viele Karten) werden kleine Zahlen wertlos
            if runde > 5 and karte.value < 8:
                prob *= 0.5

        total_prob += prob

    # Wir runden mathematisch (0.5 wird aufgerundet), statt nur abzuschneiden
    anzahl_stiche = round(total_prob)

    # Sicherstellen, dass in Runde 1 bei einer starken Karte mindestens 1 geboten wird
    if runde == 1 and total_prob > 0.4:
        return 1


    if spielstil == "aggressiv":
        anzahl_stiche = math.floor(total_prob + 0.65)
    else:
        # Normales Runden
        anzahl_stiche = round(total_prob)

    return min(anzahl_stiche, len(karten))


def spiele_stich(spielerliste, start_spieler_index, trumpf_farbe, runde, tabelle, stiche_dieser_runde):
    stich_karten = {}
    bedien_farbe = ""
    aktuelle_gewinn_karte = None
    gewinner = None

    for i in range(len(spielerliste)):

        aktiver_spieler = spielerliste[(start_spieler_index + i) % len(spielerliste)]
        #print(aktiver_spieler)

        # 1. Daten aus der Tabelle holen
        geplante_stiche = tabelle.loc[runde, (aktiver_spieler.name, 'Angesagt')]
        # 'Gemacht' tracken wir hier besser lokal oder über eine Variable,
        # da die Tabelle erst am Ende der Runde befüllt wird
        aktuell_gemachte_stiche = stiche_dieser_runde[aktiver_spieler.name]

        will_stich = aktuell_gemachte_stiche < geplante_stiche

        # finde alle erlaubten Karten
        moegliche_karten = finde_erlaubte_karten_für_Zug(aktiver_spieler.karten_auf_der_hand, bedien_farbe)

        #prüfen, welche höchste karte ist und , ob meine ggf größer
        #hoechste_karte = bestimme_hoechste_karte(stich_karten, bedien_farbe, trumpf_farbe)


        gelegte_karte = (schlaue_karte_auswaehlen
                         (moegliche_karten, aktuelle_gewinn_karte, stich_karten, bedien_farbe, trumpf_farbe, will_stich, spielstil=aktiver_spieler.spielstil))

        if bedien_farbe == "" and gelegte_karte.color != "":
            bedien_farbe = gelegte_karte.color

        # Jetzt prüfen, ob die neue Karte (vielleicht die erste Farbkarte nach einem Narren) führt
        if aktuelle_gewinn_karte is None or ist_staerker(gelegte_karte, aktuelle_gewinn_karte, bedien_farbe, trumpf_farbe):
            aktuelle_gewinn_karte = gelegte_karte
            gewinner = aktiver_spieler.name


        aktiver_spieler.karten_auf_der_hand.remove(gelegte_karte)
        stich_karten[aktiver_spieler.name] = gelegte_karte



    #print(f"Der Stich: {stich_karten}")
    #gewinner, karte = gewinner_des_stiches(stich_karten, bedien_farbe, trumpf_farbe)
    #print(f"Gewinner des Stiches ist: {gewinner} mit {karte}")

    return gewinner





def schlaue_karte_auswaehlen(karten, hoechste_stich_karte, stich_karten, bedien_farbe, trumpf_farbe, spielerliste, will_stich_machen=True, spielstil="normal"):

    gewinner_karten = []
    verlierer_karten = []

    for karte in karten:
        # Wenn noch keine Karte liegt, gewinnt man (außer mit Narr)
        if hoechste_stich_karte is None:
            if karte.value > 0:
                gewinner_karten.append(karte)
            else:
                verlierer_karten.append(karte)
        # Ansonsten: Prüfung gegen die aktuell beste Karte
        elif ist_staerker(karte, hoechste_stich_karte, bedien_farbe, trumpf_farbe):
            gewinner_karten.append(karte)
        else:
            verlierer_karten.append(karte)

    # 2. Strategie anwenden
    if will_stich_machen:
        if gewinner_karten:
            if spielstil == "aggressiv":
                if not stich_karten:
                    trumpf_karten = [karte for karte in gewinner_karten if karte.color == trumpf_farbe]
                    if trumpf_karten:
                        return max(trumpf_karten, key=lambda karte: karte.value)
                # AGGRESSIV: Nimm die HÖCHSTE Karte, die gewinnt (den "Sack zumachen")
                return max(gewinner_karten, key=lambda karte: karte.value)
            else:
                # NORMAL: Nimm die kleinste Karte, die gerade so sticht (Sparen)
                return min(gewinner_karten, key=lambda karte: karte.value)
        else:
            # Kann nicht gewinnen -> kleinste Karte wegwerfen
            normale_farben = [karte for karte in verlierer_karten if karte.color != trumpf_farbe and karte.value not in [0,14]]
            if normale_farben:
                return min(normale_farben, key=lambda karte: karte.value)
            return min(karten, key=lambda karte: karte.value)

    else:
        if verlierer_karten:
            zauberer_verlierer = [karte for karte in verlierer_karten if karte.value == 14]
            if zauberer_verlierer:
                return zauberer_verlierer[0]

            truempfe_in_verlierer = [karte for karte in verlierer_karten if karte.color == trumpf_farbe]

            if truempfe_in_verlierer:
                # Werfe den höchsten Trumpf ab, der gerade NICHT sticht
                return max(truempfe_in_verlierer, key=lambda k: k.value)

            # Wenn kein Trumpf zum Abwerfen da ist, nimm die höchste normale Karte
            return max(verlierer_karten, key=lambda k: k.value)
        else:
            # Muss leider gewinnen -> kleinste Karte opfern
            anzahl_karten_im_stich = len(stich_karten)
            noch_spieler_dran = anzahl_karten_im_stich < (len(spielerliste)-1)
            if noch_spieler_dran:
                return min(karten, key=lambda karte: karte.value)
            else:
                return max(karten, key=lambda karte: karte.value)


def ist_staerker(neue_karte, beste_bisher, bedien_farbe, trumpf_farbe):
    # 1. Zauberer-Regel: Der erste Zauberer im Stich gewinnt immer.
    # Wenn die Karte, die bereits führt, ein Zauberer (14) ist,
    # kann keine nachfolgende Karte sie mehr schlagen.
    if beste_bisher.value == 14:
        return False

    # Wenn die neue Karte ein Zauberer ist (und die beste bisher keiner war), führt sie jetzt.
    if neue_karte.value == 14:
        return True

    # 2. Narren-Regel: Ein Narr (0) kann niemals eine Karte schlagen, die bereits führt.
    if neue_karte.value == 0:
        return False

    # 3. Trumpf-Logik:
    # Neue Karte ist Trumpf, die beste bisherige aber nicht.
    if neue_karte.color == trumpf_farbe and beste_bisher.color != trumpf_farbe:
        return True
    # Beide sind Trumpf -> der höhere Wert gewinnt.
    if neue_karte.color == trumpf_farbe and beste_bisher.color == trumpf_farbe:
        return neue_karte.value > beste_bisher.value

    # 4. Bedienfarben-Logik:
    # Neue Karte bedient die Farbe, die beste bisherige ist aber weder Trumpf noch Bedienfarbe.
    if neue_karte.color == bedien_farbe and beste_bisher.color != bedien_farbe:
        # (Da wir oben Trumpf schon geprüft haben, wissen wir hier: beste_bisher ist kein Trumpf)
        return True
    # Beide haben die Bedienfarbe -> der höhere Wert gewinnt.
    if neue_karte.color == bedien_farbe and beste_bisher.color == bedien_farbe:
        return neue_karte.value > beste_bisher.value

    # 5. Alle anderen Fälle:
    # Wenn die neue Karte eine falsche Farbe hat (Abwurf) oder kleiner ist, gewinnt sie nicht.
    return False






def finde_erlaubte_karten_für_Zug(karten, bedien_farbe):
    if not bedien_farbe:
        return karten

    bedien_farbe_karten = [karte for karte in karten if karte.color == bedien_farbe]
    if not bedien_farbe_karten:
        return karten

    erlaubte_karten = [karte for karte in karten if karte.color == bedien_farbe or karte.color == ""]
    return erlaubte_karten



def wie_viele_gemachte_stiche(spieler, stichgewinner):
    anzahl_gemachte_stiche = stichgewinner.count(spieler.name)
    return anzahl_gemachte_stiche




def spiele_spielen(anzahl_spiele, spielerliste):
    for i in range (anzahl_spiele):
        starte_spiel(1, spielerliste)


def gewinn_wahrscheinlichkeiten(gewinner_liste, anzahl_spiele, spielerliste):
    wahrscheinlichkeiten = {spieler.name: gewinner_liste.count(spieler.name) / anzahl_spiele for spieler in spielerliste}

    df = pd.DataFrame(wahrscheinlichkeiten, index=["Gewinnchance"])

    #Für die Anzeige in der Konsole in Prozent umwandeln
    df_prozent = df.map(lambda x: f"{x * 100:.1f}%")

    #Speichern (df_prozent nutzen)
    export_mit_metadaten(df_prozent, "letzte_simulation", seed=42)

    return df_prozent



def export_mit_metadaten(df, dateiname, seed=42):
    """Speichert einen DataFrame mit Metadaten-Header in den reports-Ordner."""

    os.makedirs("reports", exist_ok=True) #erstelltOrdner reports falls er fehlt

    zeitstempel = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Header-Zeilen zusammen mit # am Anfang
    header = [
        f"# Projekt: Wizard Simulation",
        f"# Erstellungsdatum: {zeitstempel}",
        f"# Verwendeter Seed: {seed}",
        f"# Status: Finales Ergebnis",
        "#"
    ]

    pfad = f"reports/{dateiname}.csv"

    #Erst den Header schreiben, dann den DataFrame anhängen
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write("\n".join(header) + "\n")
        df.to_csv(f, index=True)

    print(f"Ergebnisse erfolgreich gespeichert unter: {pfad}")