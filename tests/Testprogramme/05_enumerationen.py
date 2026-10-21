from enum import Enum

class ModulStatus(Enum):
    NICHT_BEGONNEN = "Nicht begonnen"
    IN_BEARBEITUNG = "In Bearbeitung"
    ERGEBNIS_AUSSTEHEND = "Ergebnis ausstehend"
    BESTANDEN = "Bestanden"
    NICHT_BESTANDEN = "Nicht bestanden"

aktueller_status = ModulStatus.IN_BEARBEITUNG

print(aktueller_status)
print(aktueller_status.value)


class Pruefungsform(Enum):
    KLAUSUR = "Klausur"
    ADVANCED_WORKBOOK = "Advanced Workbook"
    PORTFOLIO = "Portfolio"
    PROJEKTBERICHT = "Projektbericht"
    FALLSTUDIE = "Fallstudie"
    FACHPRAESENTATION = "Fachpräsentation"
    SEMINARARBEIT = "Seminararbeit"
    BACHELORARBEIT = "Bachelorarbeit"
    KOLLOQUIUM = "Kolloquium"

ausgewaehlte_pruefungsform = Pruefungsform.PORTFOLIO
print(ausgewaehlte_pruefungsform.value)


class ZeitplanStatus(Enum):
    VORSPRUNG = "Vorsprung"
    IM_ZEITPLAN = "Im Zeitplan"
    IM_VERZUG = "Im Verzug"


zeitplan = ZeitplanStatus.IM_ZEITPLAN
print(zeitplan.value)