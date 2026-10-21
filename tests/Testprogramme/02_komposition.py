class Lernabschnitt:
    def __init__(self, nummer):
        self.nummer = nummer
        self.erledigt = False


class Modul:
    def __init__(self, name):
        self.name = name
        self.lernabschnitte = []
        self.lernabschnitt_erstellen()

    def lernabschnitt_erstellen(self):
        for nummer in range(1,7):
            lernabschnitt = Lernabschnitt(nummer)
            self.lernabschnitte.append(lernabschnitt)

modul_1 = Modul("Einführung in die Programmierung mit Python")
print(len(modul_1.lernabschnitte))