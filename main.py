from src.wizard_logic import lade_spieler_aus_config, spiele_spielen, gewinner_liste, gewinn_wahrscheinlichkeiten, lade_spieler_aus_config

if __name__ == "__main__":
    print("Wizard-Simulation startet")

    spielerliste = lade_spieler_aus_config()

    anzahl_spiele = int(input("Anzahl Spiele: "))

    spiele_spielen(anzahl_spiele, spielerliste)

    stats = gewinn_wahrscheinlichkeiten(gewinner_liste, anzahl_spiele, spielerliste)
    print("\n Die Simulation ist beendet")
    print(51*"-")
    print(stats)