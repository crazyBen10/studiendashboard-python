from enum import Enum
from datetime import date


class ModulStatus(Enum):
    NICHT_BEGONNEN = "Nicht begonnen"
    IN_BEARBEITUNG = "In Bearbeitung"
    ERGEBNIS_AUSSTEHEND = "Ergebnis ausstehend"
    BESTANDEN = "Bestanden"
    NICHT_BESTANDEN = "Nicht bestanden"

class Pruefungsleistung:
    def __init__(self):
        self.abgabedatum = None
        self.note = None

class Modul:
    def __init__(self, name):
        self.name = name
        self.startdatum = None
        self.pruefungsleistung = Pruefungsleistung()

    def ermittle_status(self):
        if self.startdatum is None:
            return ModulStatus.NICHT_BEGONNEN
        if self.pruefungsleistung.abgabedatum is None:
            return ModulStatus.IN_BEARBEITUNG
        if self.pruefungsleistung.note is None:
            return ModulStatus.ERGEBNIS_AUSSTEHEND
        if self.pruefungsleistung.note <= 4.0:
            return ModulStatus.BESTANDEN
        if self.pruefungsleistung.note > 4.0:
            return ModulStatus.NICHT_BESTANDEN

modul_1 = Modul("Mathematik: Analysis")
print(modul_1.ermittle_status().value)

modul_1.startdatum = date.today()
print(modul_1.ermittle_status().value)

modul_1.pruefungsleistung.abgabedatum = date.today()
print(modul_1.ermittle_status().value)

modul_1.pruefungsleistung.note = 2.3
print(modul_1.ermittle_status().value)

modul_1.pruefungsleistung.note = 4.3
print(modul_1.ermittle_status().value)