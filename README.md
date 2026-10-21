# Studiendashboard

Dieses Projekt ist der Prototyp eines persönlichen Studiendashboards für das
Portfolio im Kurs „Objektorientierte und funktionale Programmierung mit
Python“. Die grafische Benutzeroberfläche stellt den Studienfortschritt dar und
ermöglicht es, Module, Lernabschnitte und Prüfungsergebnisse zu verwalten.

## Voraussetzungen

- Windows 10 oder Windows 11
- Python 3.13
- Keine zusätzlichen Python-Bibliotheken erforderlich

## Programm starten

1. Dieses Projekt herunterladen oder klonen.
2. Ein Terminal im Projektordner öffnen.
3. Das Programm starten:

```text
python main.py
```

## Projektaufbau

- `main.py`: startet das Programm
- `dashboard_controller.py`: steuert Auswahl, Änderungen und Speicherung
- `modelle.py`: enthält die fachlichen Klassen und Enumerationen
- `datenverwaltung.py`: lädt und speichert die Daten im JSON-Format
- `benutzeroberflaeche.py`: enthält die Tkinter-Darstellung und die
  Aufbereitung der Benutzereingaben
- `daten/studiendaten.json`: enthält die gespeicherten Studiendaten
- `tests/`: enthält Tests der wichtigsten Funktionen

## Fachliches Modell

- Modulstatus und Bestehen werden aus Start-, Abgabe- und Bewertungsdaten
  abgeleitet und nicht separat gespeichert.
- Note, Abgabedatum und Ergebnisdatum sind optional. Eine Note benötigt immer
  ein Ergebnisdatum und eine vorherige Abgabe.
- ECTS, Notendurchschnitt sowie der Vergleich von Lernfortschritt und
  verstrichener Zeit werden bei Bedarf berechnet.
- Der Planungsfortschritt eines Moduls besteht aus sechs Lernabschnitten und
  einem Prüfungsschritt. Nach einer nicht bestandenen Prüfung ist der
  Prüfungsschritt bis zur erneuten Abgabe wieder offen.
- Für die Planung besitzt ein 5-ECTS-Modul eine Bearbeitungsdauer von 42
  Tagen. Die Dauer wird proportional aus den ECTS abgeleitet: 10 ECTS ergeben
  84 Tage und 30 ECTS ergeben 252 Tage.
- Der Studienverlaufsplan umfasst 30 Module mit insgesamt 180 ECTS. Noch nicht
  gewählte Wahlpflichtmodule sind eindeutig als Platzhalter gekennzeichnet.
- Modulstatus und Prüfungsform werden durch Enumerationen begrenzt.

## Architektur

- `Anwendung` initialisiert Datenverwaltung, Studiengang und Controller.
- `DashboardController` verbindet Benutzeroberfläche, Fachmodell und Speicherung.
- `DashboardGUI` stellt die Daten dar und bereitet Formulareingaben auf.
- Die Fachklassen führen Status- und Fortschrittsberechnungen durch.

## Tests ausführen

Im Projektordner kann die vollständige Testsuite ohne Zusatzbibliotheken mit
folgendem Befehl gestartet werden:

```text
python -m unittest discover -s tests -v
```

## Hinweis zu den Beispieldaten

Die mitgelieferten Studiendaten sind vollständig fiktiv und dienen
ausschließlich dazu, die Funktionen und unterschiedlichen Zustände des
Dashboard-Prototyps zu demonstrieren. Sie enthalten keine realen
Prüfungsergebnisse. Einzelne Module können in der Anwendung über die Funktion
„Modul zurücksetzen“ zurückgesetzt werden.
