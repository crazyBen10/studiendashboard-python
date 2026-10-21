from datetime import date
from enum import Enum


class ZeitplanStatus(Enum):
    VORSPRUNG = "Vorsprung"
    IM_ZEITPLAN = "Im Zeitplan"
    IM_VERZUG = "Im Verzug"


class Lernabschnitt:
    def __init__(self, nummer):
        self.nummer = nummer
        self.erledigt = False

    def abschliessen(self):
        self.erledigt = True


class Pruefungsleistung:
    def __init__(self):
        self.abgabedatum = None
        self.note = None

    def abgeben(self, datum):
        self.abgabedatum = datum

    def ergebnis_eintragen(self, note):
        self.note = note


class Modul:
    def __init__(
        self,
        name,
        ects,
        startdatum,
        geplante_dauer_in_tagen
    ):
        self.name = name
        self.ects = ects
        self.startdatum = startdatum
        self.geplante_dauer_in_tagen = geplante_dauer_in_tagen
        self.lernabschnitte = []
        self.pruefungsleistung = Pruefungsleistung()

        for nummer in range(1, 7):
            lernabschnitt = Lernabschnitt(nummer)
            self.lernabschnitte.append(lernabschnitt)

    def berechne_lernfortschritt(self):
        erledigte_abschnitte = 0

        for lernabschnitt in self.lernabschnitte:
            if lernabschnitt.erledigt:
                erledigte_abschnitte += 1

        return erledigte_abschnitte / 6 * 100

    def berechne_planungsfortschritt(self):
        if self.pruefungsleistung.abgabedatum is not None:
            return 100

        return self.berechne_lernfortschritt()

    def berechne_bearbeitungsfortschritt(self, heute):
        vergangene_tage = (heute - self.startdatum).days

        return (
            vergangene_tage
            / self.geplante_dauer_in_tagen
            * 100
        )

    def ermittle_zeitplanstatus(self, heute):
        planungsfortschritt = self.berechne_planungsfortschritt()
        bearbeitungsfortschritt = (
            self.berechne_bearbeitungsfortschritt(heute)
        )

        unterschied = (
            planungsfortschritt
            - bearbeitungsfortschritt
        )

        if unterschied > 5:
            return ZeitplanStatus.VORSPRUNG

        if unterschied < -5:
            return ZeitplanStatus.IM_VERZUG

        return ZeitplanStatus.IM_ZEITPLAN


class Studiengang:
    def __init__(self, name, startdatum, geplantes_enddatum):
        self.name = name
        self.startdatum = startdatum
        self.geplantes_enddatum = geplantes_enddatum
        self.ziel_ects = 180
        self.module = []

    def modul_hinzufuegen(self, modul):
        self.module.append(modul)

    def berechne_zeitfortschritt(self, heute):
        vergangene_tage = (heute - self.startdatum).days
        gesamte_tage = (
            self.geplantes_enddatum - self.startdatum
        ).days

        return vergangene_tage / gesamte_tage * 100

    def berechne_planungsfortschritt(self):
        fortschrittswert = 0

        for modul in self.module:
            modulfortschritt = (
                modul.berechne_planungsfortschritt()
            )

            fortschrittswert += (
                modul.ects * modulfortschritt / 100
            )

        return fortschrittswert / self.ziel_ects * 100

    def ermittle_zeitplanstatus(self, heute):
        planungsfortschritt = (
            self.berechne_planungsfortschritt()
        )
        zeitfortschritt = (
            self.berechne_zeitfortschritt(heute)
        )

        unterschied = planungsfortschritt - zeitfortschritt

        if unterschied > 5:
            return ZeitplanStatus.VORSPRUNG

        if unterschied < -5:
            return ZeitplanStatus.IM_VERZUG

        return ZeitplanStatus.IM_ZEITPLAN


heute = date.today()

studiengang = Studiengang(
    "Angewandte Künstliche Intelligenz",
    date(2026, 4, 1),
    date(2030, 4, 1)
)


modul_1 = Modul(
    "Artificial Intelligence",
    5,
    date(2026, 4, 1),
    42
)
modul_1.pruefungsleistung.abgeben(date(2026, 5, 13))
modul_1.pruefungsleistung.ergebnis_eintragen(2.3)


modul_2 = Modul(
    "Einführung in die Programmierung mit Python",
    5,
    date(2026, 5, 14),
    42
)
modul_2.pruefungsleistung.abgeben(date(2026, 6, 25))
modul_2.pruefungsleistung.ergebnis_eintragen(1.3)


modul_3 = Modul(
    "Mathematik: Analysis",
    5,
    date(2026, 6, 26),
    42
)
modul_3.pruefungsleistung.abgeben(date(2026, 8, 7))
modul_3.pruefungsleistung.ergebnis_eintragen(3.7)


modul_4 = Modul(
    "Wissenschaftliches Arbeiten",
    5,
    date(2026, 8, 8),
    42
)
modul_4.pruefungsleistung.abgeben(date(2026, 9, 11))


aktuelles_modul = Modul(
    "Objektorientierte Programmierung mit Python",
    5,
    date(2026, 9, 12),
    42
)

for nummer in range(3):
    aktuelles_modul.lernabschnitte[nummer].abschliessen()


studiengang.modul_hinzufuegen(modul_1)
studiengang.modul_hinzufuegen(modul_2)
studiengang.modul_hinzufuegen(modul_3)
studiengang.modul_hinzufuegen(modul_4)
studiengang.modul_hinzufuegen(aktuelles_modul)


print("Aktuelles Modul:")
print(
    "Lernfortschritt:",
    round(aktuelles_modul.berechne_lernfortschritt(), 2),
    "%"
)
print(
    "Bearbeitungsfortschritt:",
    round(
        aktuelles_modul.berechne_bearbeitungsfortschritt(heute),
        2
    ),
    "%"
)
print(
    "Zeitplanstatus:",
    aktuelles_modul.ermittle_zeitplanstatus(heute).value
)


print("\nGesamtes Studium:")
print(
    "Planungsfortschritt:",
    round(studiengang.berechne_planungsfortschritt(), 2),
    "%"
)
print(
    "Vergangene Studienzeit:",
    round(studiengang.berechne_zeitfortschritt(heute), 2),
    "%"
)
print(
    "Zeitplanstatus:",
    studiengang.ermittle_zeitplanstatus(heute).value
)