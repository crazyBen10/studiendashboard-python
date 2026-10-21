class Modul:
    def __init__(self, name):
        self.name = name

class Semester:
    def __init__(self, nummer):
        self.nummer = nummer
        self.module = []

    def modul_hinzufuegen(self, modul):
        self.module.append(modul)

module_2 = Modul("Mathematik: Analysis")
semester_1 = Semester(1)

semester_1.modul_hinzufuegen(module_2)

print(semester_1.module[0].name)