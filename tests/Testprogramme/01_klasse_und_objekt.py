class Lernabschnitt:
    def __init__(self, nummer, bezeichnung):
        self.nummer = nummer
        self.bezeichnung = bezeichnung
        self.erledigt = False

    def abschliessen(self):
        self.erledigt = True

lernabschnitt_1 = Lernabschnitt(1, "Lernabschnitt 1")

print(lernabschnitt_1.bezeichnung, lernabschnitt_1.erledigt)

lernabschnitt_1.abschliessen()

print(lernabschnitt_1.bezeichnung, lernabschnitt_1.erledigt)
