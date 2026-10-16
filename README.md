# Studiendashboard

Prototyp eines persönlichen Studiendashboards für das Portfolio im Kurs
„Objektorientierte und funktionale Programmierung mit Python“.

## Voraussetzungen

- Windows 10 oder Windows 11
- Python 3.13
- keine zusätzlichen Python-Bibliotheken

## Programm starten

1. Dieses Projekt herunterladen oder klonen.
2. Den Projektordner öffnen.
3. `main.py` mit Python ausführen.

## Projektaufbau

- `main.py`: startet das Programm
- `modelle.py`: enthält die fachlichen Klassen und Enumerationen
- `datenverwaltung.py`: lädt und speichert die JSON-Daten
- `benutzeroberflaeche.py`: enthält die Tkinter-Benutzeroberfläche
- `daten/studiendaten.json`: enthält die gespeicherten Studiendaten
- `tests/`: enthält Tests der wichtigsten Funktionen

## Fachliches Modell

- Modulstatus und Bestehen werden aus Start-, Abgabe- und Bewertungsdaten
  abgeleitet und nicht separat gespeichert.
- Note, Abgabedatum und Ergebnisdatum sind optional. Eine Note benötigt immer
  ein Ergebnisdatum und eine vorherige Abgabe.
- ECTS, Notendurchschnitt sowie der Vergleich von Lernfortschritt und Zeit
  werden bei Bedarf berechnet.
- Für die Planung besitzt ein 5-ECTS-Modul eine Bearbeitungsdauer von 42
  Tagen. Die Dauer wird proportional aus den ECTS abgeleitet: 10 ECTS ergeben
  84 Tage und 30 ECTS ergeben 252 Tage.
- Der Studienverlaufsplan umfasst 30 Module mit insgesamt 180 ECTS. Noch nicht
  gewählte Wahlpflichtmodule sind eindeutig als Platzhalter gekennzeichnet.
- Modulstatus und Prüfungsform werden durch Enumerationen begrenzt.

## Tests ausführen

Im Projektordner kann die vollständige Testsuite ohne Zusatzbibliotheken mit
folgendem Befehl gestartet werden:

```text
python -m unittest discover -s tests -v
```
