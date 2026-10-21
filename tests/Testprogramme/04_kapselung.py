class Pruefungsleistung:
    def __init__(self):
        self.__note = None

    def ergebnis_eintragen(self, note):
        if 1.0 <= note <= 5.0:
            self.__note = note
        else:
            print("Fehlermeldung")

    def note_anzeigen(self):
        return self.__note

pruefung_1 = Pruefungsleistung()

pruefung_1.ergebnis_eintragen(2.3)
print(pruefung_1.note_anzeigen())

pruefung_1.ergebnis_eintragen(5.5)
print(pruefung_1.note_anzeigen())