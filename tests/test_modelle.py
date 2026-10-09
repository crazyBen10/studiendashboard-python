from datetime import date

from modelle import Modul, Pruefungsform, Studiengang


studiengang = Studiengang(
    "B.Sc. Softwareentwicklung",
    date(2026, 4, 1),
    date(2030, 4, 1),
    180,
    2.0
)

modul = Modul(
    "TEST01",
    "Testmodul",
    5,
    42,
    Pruefungsform.KLAUSUR
)

studiengang.semester[0].modul_hinzufuegen(modul)

print("Semester:", len(studiengang.semester))
print("Module:", len(studiengang.alle_module()))
print("Status:", modul.ermittle_status().value)

studiengang.starte_modul(modul, date(2026, 4, 1))

for lernabschnitt in modul.lernabschnitte[:3]:
    lernabschnitt.abschliessen()

print("Status nach Start:", modul.ermittle_status().value)
print("Lernfortschritt:", modul.berechne_lernfortschritt())
print(
    "Zeitplanstatus des Moduls:",
    modul.ermittle_zeitplan_status(date(2026, 4, 22)).value
)

modul.pruefungsleistung.abgeben(date(2026, 5, 13))

print("Status nach Abgabe:", modul.ermittle_status().value)
print("Erreichte ECTS vor Bewertung:", studiengang.berechne_erreichte_ects())
print(
    "Planungsfortschritt des Studiums:",
    studiengang.berechne_planungsfortschritt()
)

modul.pruefungsleistung.ergebnis_eintragen(
    2.3,
    date(2026, 5, 20)
)

print("Status nach Bewertung:", modul.ermittle_status().value)
print("Erreichte ECTS:", studiengang.berechne_erreichte_ects())
print("Notendurchschnitt:", studiengang.berechne_notendurchschnitt())
print("Studienfortschritt:", studiengang.berechne_studienfortschritt())

modul_2 = Modul(
    "TEST02",
    "Zweites Testmodul",
    5,
    42,
    Pruefungsform.PORTFOLIO
)

modul_3 = Modul(
    "TEST03",
    "Drittes Testmodul",
    5,
    42,
    Pruefungsform.KLAUSUR
)

studiengang.semester[0].modul_hinzufuegen(modul_2)
studiengang.semester[0].modul_hinzufuegen(modul_3)

studiengang.starte_modul(modul_2, date(2026, 5, 21))

try:
    studiengang.starte_modul(modul_3, date(2026, 5, 22))
except ValueError as fehler:
    print("Erwartete Fehlermeldung:", fehler)

modul_2.pruefungsleistung.abgeben(date(2026, 6, 10))

studiengang.starte_modul(modul_3, date(2026, 6, 11))

print("Status Modul 2:", modul_2.ermittle_status().value)
print("Status Modul 3:", modul_3.ermittle_status().value)

testdatum = date(2026, 6, 11)

print(
    "Zeitfortschritt des Studiums:",
    studiengang.berechne_zeitfortschritt(testdatum)
)

print(
    "Planungsfortschritt des Studiums:",
    studiengang.berechne_planungsfortschritt()
)

print(
    "Zeitplanstatus des Studiums:",
    studiengang.ermittle_zeitplan_status(testdatum).value
)