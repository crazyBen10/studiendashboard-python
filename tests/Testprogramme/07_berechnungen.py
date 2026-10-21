class Modul:
    def __init__(self, name, ects):
        self.name = name
        self.note = None
        self.ects = ects

class Studiengang:
    def __init__(self):
        self.ziel_ects = 180
        self.module = []

    def modul_hinzufuegen(self, modul):
        self.module.append(modul)

    def berechne_erreichte_ects(self):
        erreichte_ects = 0
        for modul in self.module:
            if modul.note is not None and modul.note <= 4.0:
                erreichte_ects += modul.ects
        return erreichte_ects
    
    def berechne_studienfortschritt(self):
        studienfortschritt = round((self.berechne_erreichte_ects() / self.ziel_ects * 100),2)
        return studienfortschritt
    
    def berechne_notendurchschnitt(self):
        noten = []
        for modul in self.module:
            if modul.note is not None and modul.note <= 4.0:
                noten.append(modul.note)
        if not noten:
            return None
        else:
            return round((sum(noten) / len(noten)),2)

angewandte_ki = Studiengang()
modul_1 = Modul("Einführung in die Programmierung mit Python", 5)
modul_2 = Modul("Mathematik: Analysis", 5)
modul_3 = Modul("Artificial Intelligence", 5)

modul_1.note = 1.3
modul_2.note = 2.3
modul_3.note = 3.7

angewandte_ki.modul_hinzufuegen(modul_1)
angewandte_ki.modul_hinzufuegen(modul_2)
angewandte_ki.modul_hinzufuegen(modul_3)

print(angewandte_ki.berechne_erreichte_ects())
print(angewandte_ki.berechne_notendurchschnitt())
print(f"{angewandte_ki.berechne_studienfortschritt()} %")