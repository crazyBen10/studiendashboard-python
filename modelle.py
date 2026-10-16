"""Fachliche Klassen und Enumerationen des Studiendashboards."""

from datetime import date
from enum import Enum
from math import isfinite


MINDESTNOTE = 1.0
BESTEHENSGRENZE = 4.0
HOECHSTNOTE = 5.0
ZEITPLAN_TOLERANZ_PROZENT = 5.0
TAGE_PRO_FUENF_ECTS = 42


def _pruefe_text(wert: str, feldname: str) -> str:
    """Prüft ein verpflichtendes Textfeld und gibt es bereinigt zurück."""

    if not isinstance(wert, str) or not wert.strip():
        raise ValueError(f"{feldname} darf nicht leer sein.")
    return wert.strip()


def _pruefe_positive_ganzzahl(wert: int, feldname: str) -> int:
    """Prüft eine positive Ganzzahl."""

    if isinstance(wert, bool) or not isinstance(wert, int) or wert <= 0:
        raise ValueError(f"{feldname} muss eine positive Ganzzahl sein.")
    return wert


def _pruefe_datum(wert: date, feldname: str) -> date:
    """Prüft, ob ein Wert ein Datum ist."""

    if not isinstance(wert, date):
        raise TypeError(f"{feldname} muss ein Datum sein.")
    return wert


def _pruefe_note(wert: float, feldname: str = "Die Note") -> float:
    """Prüft eine Note im Wertebereich von 1,0 bis 5,0."""

    if isinstance(wert, bool) or not isinstance(wert, (int, float)):
        raise TypeError(f"{feldname} muss eine Zahl sein.")

    note = float(wert)
    if not isfinite(note) or not MINDESTNOTE <= note <= HOECHSTNOTE:
        raise ValueError(
            f"{feldname} muss zwischen {MINDESTNOTE:.1f} und "
            f"{HOECHSTNOTE:.1f} liegen."
        )
    return note

#------------------------------------------------------------------------------------------------------------------------
# Alle Enumerationen, die in der Anwendung verwendet werden, sind hier definiert.
#------------------------------------------------------------------------------------------------------------------------


class ModulStatus(Enum):
    """Beschreibt die möglichen Bearbeitungszustände eines Moduls."""

    NICHT_BEGONNEN = "Nicht begonnen"
    IN_BEARBEITUNG = "In Bearbeitung"
    ERGEBNIS_AUSSTEHEND = "Ergebnis ausstehend"
    BESTANDEN = "Bestanden"
    NICHT_BESTANDEN = "Nicht bestanden"


class Pruefungsform(Enum):
    """Enthält alle möglichen Prüfungsformen eines Moduls."""

    KLAUSUR = "Klausur"
    ADVANCED_WORKBOOK = "Advanced Workbook"
    PORTFOLIO = "Portfolio"
    PROJEKTBERICHT = "Projektbericht"
    FALLSTUDIE = "Fallstudie"
    FACHPRAESENTATION = "Fachpräsentation"
    SEMINARARBEIT = "Seminararbeit"
    BACHELORARBEIT = "Bachelorarbeit"
    KOLLOQUIUM = "Kolloquium"
    PRAXISREFLEXION = "Praxisreflexion"
    NOCH_NICHT_FESTGELEGT = "Noch nicht festgelegt"


class ZeitplanStatus(Enum):
    """Beschreibt den zeitlichen Stand des Studiums oder eines Moduls."""

    VORSPRUNG = "Vorsprung"
    IM_ZEITPLAN = "Im Zeitplan"
    IM_VERZUG = "Im Verzug"


#------------------------------------------------------------------------------------------------------------------------
# Lernabschnitt 
#------------------------------------------------------------------------------------------------------------------------


class Lernabschnitt:
    """Repräsentiert einen einzelnen Lernabschnitt eines Moduls."""

    def __init__(self, nummer: int, bezeichnung: str, erledigt: bool = False):
        """Erstellt einen noch nicht erledigten Lernabschnitt."""

        self.__nummer = _pruefe_positive_ganzzahl(nummer, "Die Nummer")
        self.__bezeichnung = _pruefe_text(bezeichnung, "Die Bezeichnung")
        if not isinstance(erledigt, bool):
            raise TypeError("Der Erledigt-Status muss ein Wahrheitswert sein.")
        self.__erledigt = erledigt

    def abschliessen(self) -> None:
        """Markiert den Lernabschnitt als erledigt."""

        self.__erledigt = True

    def zuruecksetzen(self) -> None:
        """Markiert den Lernabschnitt wieder als nicht erledigt."""

        self.__erledigt = False

    def ist_erledigt(self) -> bool:
        """Gibt zurück, ob der Lernabschnitt erledigt ist."""

        return self.__erledigt

    @property
    def nummer(self) -> int:
        """Gibt die Nummer des Lernabschnitts zurück."""

        return self.__nummer
    
    @property
    def bezeichnung(self) -> str:
        """Gibt die Bezeichnung des Lernabschnitts zurück."""

        return self.__bezeichnung


#------------------------------------------------------------------------------------------------------------------------
# Pruefungsleistung 
#------------------------------------------------------------------------------------------------------------------------


class Pruefungsleistung:
    """Repräsentiert die Prüfungsleistung eines Moduls."""

    def __init__(self, pruefungsform: Pruefungsform):
        """Erstellt eine noch nicht abgegebene und unbewertete Prüfungsleistung."""

        if not isinstance(pruefungsform, Pruefungsform):
            raise TypeError("Die Prüfungsform muss ein Wert aus Pruefungsform sein.")
        self.__pruefungsform = pruefungsform
        self.__abgabedatum: date | None = None
        self.__ergebnisdatum: date | None = None
        self.__note: float | None = None

    @staticmethod
    def validiere_daten(
        abgabedatum: date | None,
        note: float | None,
        ergebnisdatum: date | None
    ) -> tuple[date | None, float | None, date | None]:
        """Validiert zusammengehörige Prüfungsdaten ohne Zustandsänderung."""

        if abgabedatum is not None:
            _pruefe_datum(abgabedatum, "Das Abgabedatum")
        if ergebnisdatum is not None:
            _pruefe_datum(ergebnisdatum, "Das Ergebnisdatum")
        if note is None and ergebnisdatum is not None:
            raise ValueError("Zum Ergebnisdatum muss auch eine Note vorliegen.")
        if note is not None and ergebnisdatum is None:
            raise ValueError("Zu einer Note muss auch ein Ergebnisdatum vorliegen.")
        if note is not None and abgabedatum is None:
            raise ValueError("Vor der Bewertung muss eine Abgabe vorliegen.")

        validierte_note = None if note is None else _pruefe_note(note)
        if (
            abgabedatum is not None
            and ergebnisdatum is not None
            and ergebnisdatum < abgabedatum
        ):
            raise ValueError(
                "Das Ergebnisdatum darf nicht vor dem Abgabedatum liegen."
            )
        return abgabedatum, validierte_note, ergebnisdatum

    def daten_aktualisieren(
        self,
        abgabedatum: date | None,
        note: float | None,
        ergebnisdatum: date | None
    ) -> None:
        """Aktualisiert alle optionalen Prüfungsdaten atomar."""

        abgabedatum, note, ergebnisdatum = self.validiere_daten(
            abgabedatum,
            note,
            ergebnisdatum
        )
        self.__abgabedatum = abgabedatum
        self.__note = note
        self.__ergebnisdatum = ergebnisdatum

    def abgeben(self, abgabedatum: date) -> None:
        """Trägt oder ändert das Abgabedatum."""

        self.daten_aktualisieren(
            abgabedatum,
            self.__note,
            self.__ergebnisdatum
        )

    def abgabe_zuruecksetzen(self) -> None:
        """Entfernt Abgabe und Bewertung der Prüfungsleistung."""

        self.daten_aktualisieren(None, None, None)

    def ergebnis_zuruecksetzen(self) -> None:
        """Entfernt Ergebnisdatum und Note, behält aber die Abgabe bei."""

        self.daten_aktualisieren(self.__abgabedatum, None, None)

    def ergebnis_eintragen(self, note: float, datum: date) -> None:
        """Trägt das Ergebnis der Prüfungsleistung ein."""

        self.daten_aktualisieren(self.__abgabedatum, note, datum)

    def ist_abgegeben(self) -> bool:
        """Gibt zurück, ob die Prüfungsleistung abgegeben wurde."""

        return self.__abgabedatum is not None

    def ist_bewertet(self) -> bool:
        """Gibt zurück, ob die Prüfungsleistung bewertet wurde."""

        return self.__note is not None

    def ist_bestanden(self) -> bool | None:
        """Gibt zurück, ob die Prüfungsleistung bestanden wurde."""

        if self.__note is None:
            return None
        return self.__note <= BESTEHENSGRENZE

    @property
    def pruefungsform(self) -> Pruefungsform:
        """Gibt die Prüfungsform der Prüfungsleistung zurück."""

        return self.__pruefungsform
    
    @property
    def abgabedatum(self) -> date | None:
        """Gibt das Abgabedatum der Prüfungsleistung zurück."""

        return self.__abgabedatum

    @property
    def ergebnisdatum(self) -> date | None:
        """Gibt das Ergebnisdatum der Prüfungsleistung zurück."""

        return self.__ergebnisdatum

    @property
    def note(self) -> float | None:
        """Gibt die Note der Prüfungsleistung zurück."""

        return self.__note


#------------------------------------------------------------------------------------------------------------------------
# Modul 
#------------------------------------------------------------------------------------------------------------------------

class Modul:
    """Repräsentiert ein Modul eines Studiengangs."""

    def __init__(
        self,
        kurscode: str,
        name: str,
        ects: int,
        pruefungsform: Pruefungsform,
        lernabschnitte: list[Lernabschnitt] | None = None
    ):
        """Erstellt ein noch nicht begonnenes Modul."""

        self.__kurscode = _pruefe_text(kurscode, "Der Kurscode")
        self.__name = _pruefe_text(name, "Der Modulname")
        self.__ects = _pruefe_positive_ganzzahl(ects, "Die ECTS-Punkte")
        self.__geplante_dauer_in_tagen = round(
            self.__ects / 5 * TAGE_PRO_FUENF_ECTS
        )
        self.__pruefungsleistung = Pruefungsleistung(pruefungsform)
        self.__lernabschnitte: list[Lernabschnitt] = []
        if lernabschnitte is None:
            self.__lernabschnitte_erstellen()
        else:
            if len(lernabschnitte) != 6:
                raise ValueError("Ein Modul muss genau 6 Lernabschnitte besitzen.")
            if not all(
                isinstance(lernabschnitt, Lernabschnitt)
                for lernabschnitt in lernabschnitte
            ):
                raise TypeError(
                    "Alle Lernabschnitte müssen Lernabschnitt-Objekte sein."
                )
            nummern = sorted(
                lernabschnitt.nummer
                for lernabschnitt in lernabschnitte
            )
            if nummern != list(range(1, 7)):
                raise ValueError(
                    "Die Lernabschnitte müssen eindeutig von 1 bis 6 "
                    "nummeriert sein."
                )
            self.__lernabschnitte = sorted(
                lernabschnitte,
                key=lambda lernabschnitt: lernabschnitt.nummer
            )
        self.__startdatum: date | None = None


    def __lernabschnitte_erstellen(self) -> None:
        """Erstellt automatisch die 6 Lernabschnitte des Moduls."""
        
        for nummer in range(1, 7):
            bezeichnung = f"Lernabschnitt {nummer}"
            lernabschnitt = Lernabschnitt(nummer, bezeichnung)
            self.__lernabschnitte.append(lernabschnitt)



    def starten(self, datum: date) -> None:
        """Startet das Modul mit dem angegeben Datum."""

        _pruefe_datum(datum, "Das Startdatum")
        if self.__startdatum is not None:
            raise ValueError("Das Modul wurde bereits gestartet.")
        self.__startdatum = datum

    def startdatum_aendern(self, datum: date) -> None:
        """Ändert das Startdatum eines bereits gestarteten Moduls."""

        _pruefe_datum(datum, "Das Startdatum")
        if self.__startdatum is None:
            raise ValueError("Das Modul wurde noch nicht gestartet.")

        self.__startdatum = datum

    def zuruecksetzen(self) -> None:
        """Setzt das Modul vollständig auf den Zustand „nicht begonnen“ zurück.

        Neben dem Startdatum werden auch der Lernfortschritt und sämtliche
        optionalen Prüfungsdaten entfernt. Dadurch kann der abgeleitete
        Modulstatus anschließend keine widersprüchlichen Restdaten enthalten.
        """

        self.__pruefungsleistung.abgabe_zuruecksetzen()
        for lernabschnitt in self.__lernabschnitte:
            lernabschnitt.zuruecksetzen()
        self.__startdatum = None

    def pruefungsdaten_aktualisieren(
        self,
        abgabedatum: date | None,
        note: float | None,
        ergebnisdatum: date | None
    ) -> None:
        """Validiert und aktualisiert die Prüfungsdaten des Moduls atomar."""

        if any(wert is not None for wert in (abgabedatum, note, ergebnisdatum)):
            if self.__startdatum is None:
                raise ValueError(
                    "Das Modul muss vor der Prüfungsabgabe gestartet werden."
                )
        self.__pruefungsleistung.daten_aktualisieren(
            abgabedatum,
            note,
            ergebnisdatum
        )



    def berechne_lernfortschritt(self) -> float:
        """Berechnet den Lernfortschritt des Moduls in Prozent."""

        if len(self.__lernabschnitte) == 0:
            return 0.0

        fertige_lernabschnitte = 0

        for lernabschnitt in self.__lernabschnitte:
            if lernabschnitt.ist_erledigt():
                fertige_lernabschnitte += 1

        lernfortschritt = (fertige_lernabschnitte / len(self.__lernabschnitte)) * 100

        return round(lernfortschritt, 2)



    def berechne_planungsfortschritt(self) -> float:
        """Berechnet den Fortschritt des Moduls für die Zeitplanung."""

        if self.__pruefungsleistung.ist_abgegeben():
            return 100.0
        # Wenn das Modul noch nicht abgegeben wurde, berechne den Fortschritt basierend auf den erledigten Lernabschnitten
        return self.berechne_lernfortschritt()



    def berechne_bearbeitungsfortschritt(self, heute: date) -> float:
        """Berechnet den Bearbeitungsfortschritt des Moduls in Prozent."""

        _pruefe_datum(heute, "Das Vergleichsdatum")
        if self.__startdatum is None:
            return 0.0

        vergangene_tage = (heute - self.__startdatum).days

        vergangene_tage = max(0, vergangene_tage)
        bearbeitungsfortschritt = (
            vergangene_tage / self.__geplante_dauer_in_tagen
        ) * 100
        return round(bearbeitungsfortschritt, 2)

    def berechne_restzeit_in_tagen(self, heute: date) -> int | None:
        """Berechnet die verbleibenden Tage der Modulplanung.

        Ein negatives Ergebnis gibt an, um wie viele Tage die geplante
        Bearbeitungsdauer bereits überschritten wurde. Vor dem Modulstart
        ist noch keine Restzeit bestimmbar.
        """

        _pruefe_datum(heute, "Das Vergleichsdatum")
        if self.__startdatum is None:
            return None

        vergangene_tage = max(0, (heute - self.__startdatum).days)
        return self.__geplante_dauer_in_tagen - vergangene_tage

    def vergleiche_lernfortschritt_mit_bearbeitungszeit(
        self,
        heute: date
    ) -> float:
        """Gibt Planungsfortschritt minus vergangene Bearbeitungszeit zurück."""

        return round(
            self.berechne_planungsfortschritt()
            - self.berechne_bearbeitungsfortschritt(heute),
            2
        )



    def bestimme_status(self) -> ModulStatus:
        """Ermittelt den aktuellen Status des Moduls."""

        # Wenn es kein Startdatum gibt, ist das Modul noch nicht begonnen
        if self.__startdatum is None:
            return ModulStatus.NICHT_BEGONNEN
        # wenn das modul bewertet wurde, wird überprüft ob es bestanden wurde oder nicht
        elif self.__pruefungsleistung.ist_bewertet():
            if self.__pruefungsleistung.ist_bestanden():
                return ModulStatus.BESTANDEN
            else:
                return ModulStatus.NICHT_BESTANDEN
        elif self.__pruefungsleistung.ist_abgegeben():
            return ModulStatus.ERGEBNIS_AUSSTEHEND
        else:
            return ModulStatus.IN_BEARBEITUNG

    def ermittle_status(self) -> ModulStatus:
        """Kompatibilitätsname für die UML-Methode ``bestimme_status``."""

        return self.bestimme_status()



    def ermittle_zeitplan_status(self, heute: date) -> ZeitplanStatus:
        """Ermittelt den Zeitplanstatus anhand von Fortschritt und vergangener Zeit."""

        differenz = self.vergleiche_lernfortschritt_mit_bearbeitungszeit(heute)

        if differenz > ZEITPLAN_TOLERANZ_PROZENT:
            return ZeitplanStatus.VORSPRUNG
        elif differenz >= -ZEITPLAN_TOLERANZ_PROZENT:
            return ZeitplanStatus.IM_ZEITPLAN
        else:
            return ZeitplanStatus.IM_VERZUG



    @property
    def kurscode(self) -> str:
        """Gibt den Kurscode des Moduls zurück."""
        return self.__kurscode
    
    @property
    def name(self) -> str:
        """Gibt den Namen des Moduls zurück."""
        return self.__name

    @property
    def ects(self) -> int:
        """Gibt die ECTS-Punkte des Moduls zurück."""
        return self.__ects

    @property
    def geplante_dauer_in_tagen(self) -> int:
        """Gibt die geplante Dauer des Moduls in Tagen zurück."""
        return self.__geplante_dauer_in_tagen

    @property
    def startdatum(self) -> date | None:
        """Gibt das Startdatum des Moduls zurück."""
        return self.__startdatum

    @property
    def status(self) -> ModulStatus:
        """Gibt das abgeleitete Statusattribut aus dem UML-Modell zurück."""

        return self.bestimme_status()

    @property
    def pruefungsleistung(self) -> Pruefungsleistung:
        """Gibt die Prüfungsleistung des Moduls zurück."""
        return self.__pruefungsleistung

    @property
    def lernabschnitte(self) -> list[Lernabschnitt]:
        """Gibt eine Kopie der Lernabschnittsliste zurück."""
        return self.__lernabschnitte.copy()

#------------------------------------------------------------------------------------------------------------------------
# Semester 
#------------------------------------------------------------------------------------------------------------------------

class Semester:
    """Repräsentiert ein Semester eines Studiengangs."""

    def __init__(self, nummer: int, bezeichnung: str):
        """Erstellt ein Semester mit der angegebenen Nummer und Bezeichnung."""

        self.__nummer = _pruefe_positive_ganzzahl(nummer, "Die Semesternummer")
        self.__bezeichnung = _pruefe_text(
            bezeichnung,
            "Die Semesterbezeichnung"
        )
        self.__module: list[Modul] = []


    def modul_hinzufuegen(self, modul: Modul) -> None:
        """Fügt ein Modul dem Semester hinzu."""

        if not isinstance(modul, Modul):
            raise TypeError("Es können nur Modul-Objekte hinzugefügt werden.")
        if any(vorhanden.kurscode == modul.kurscode for vorhanden in self.__module):
            raise ValueError(
                f"Der Kurscode {modul.kurscode} ist bereits vorhanden."
            )
        self.__module.append(modul)

    def modul_entfernen(self, modul: Modul) -> None:
        """Entfernt ein vorhandenes Modul aus diesem Semester."""

        if modul not in self.__module:
            raise ValueError("Das Modul gehört nicht zu diesem Semester.")
        self.__module.remove(modul)


    @property
    def nummer(self) -> int:
        """Gibt die Nummer des Semesters zurück."""
        return self.__nummer
    
    @property
    def bezeichnung(self) -> str:
        """Gibt die Bezeichnung des Semesters zurück."""
        return self.__bezeichnung

    @property
    def module(self) -> list[Modul]:
        """Gibt eine Kopie der Modulliste zurück."""
        return self.__module.copy()

#------------------------------------------------------------------------------------------------------------------------
# Semester 
#------------------------------------------------------------------------------------------------------------------------


class Studiengang:
    """Repräsentiert einen Studiengang."""

    def __init__(self, name: str, startdatum: date, geplantes_enddatum: date, ziel_ects: int, zielnote: float):
        """Erstellt einen Studiengang mit den angegebenen Parametern."""

        self.__name = _pruefe_text(name, "Der Studiengangsname")
        self.__startdatum = _pruefe_datum(startdatum, "Das Startdatum")
        self.__geplantes_enddatum = _pruefe_datum(
            geplantes_enddatum,
            "Das geplante Enddatum"
        )
        if self.__geplantes_enddatum <= self.__startdatum:
            raise ValueError("Das geplante Enddatum muss nach dem Startdatum liegen.")
        self.__ziel_ects = _pruefe_positive_ganzzahl(
            ziel_ects,
            "Die Ziel-ECTS"
        )
        self.__zielnote = _pruefe_note(zielnote, "Die Zielnote")
        if self.__zielnote > BESTEHENSGRENZE:
            raise ValueError("Die Zielnote muss eine bestandene Note sein.")
        self.__semester: list[Semester] = []
        self.__semester_erstellen()
        

    def __semester_erstellen(self) -> None:
        """Erstellt automatisch 8 Semester für den Studiengang.""" 

        for nummer in range(1, 9):
            bezeichnung = f"Semester {nummer}"
            semester = Semester(nummer, bezeichnung)
            self.__semester.append(semester)


    def alle_module(self) -> list[Modul]:
        """Gibt eine Liste aller Module des Studiengangs zurück."""

        alle_module = []
        for semester in self.__semester:
            alle_module.extend(semester.module)
        return alle_module


    def hat_aktives_modul(
        self,
        zu_startendes_modul: Modul | None = None
    ) -> bool:
        """Gibt zurück ob Studiengang ein aktives Modul hat, falls ja darf kein weiteres gestartet werden.
        Falls das Modul bereits abgegeben wurde (ModulStatus - ERGEBNIS_AUSSTEHEND), darf ein neues gestartet werden."""

        for vorhandenes_modul in self.alle_module():
            if (
                vorhandenes_modul is not zu_startendes_modul
                and vorhandenes_modul.status == ModulStatus.IN_BEARBEITUNG
            ):
                return True
        return False


    def starte_modul(self, modul: Modul, datum: date) -> None:
        """Startet ein Modul des Studiengangs, falls kein anderes Modul aktiv ist."""

        if modul not in self.alle_module():
            raise ValueError("Das Modul gehört nicht zu diesem Studiengang.")
        if self.hat_aktives_modul(zu_startendes_modul=modul):
            raise ValueError("Es darf nur ein Modul gleichzeitig bearbeitet werden.")
        modul.starten(datum)


    def berechne_erreichte_ects(self) -> int:
        """Berechnet die erreichten ECTS-Punkte des Studiengangs."""

        erreichte_ects = 0
        for modul in self.alle_module():
            if modul.status == ModulStatus.BESTANDEN:
                erreichte_ects += modul.ects
        return erreichte_ects


    def berechne_studienfortschritt(self) -> float:
        """Berechnet den Studienfortschritt in Prozent basierend auf den erreichten ECTS-Punkten und dem Ziel-ECTS."""

        erreichte_ects = self.berechne_erreichte_ects()
        ziel_ects = self.__ziel_ects

        if ziel_ects == 0:
            return 0.0  # Vermeidet Division durch Null, falls Ziel-ECTS 0 ist

        return round(erreichte_ects / ziel_ects * 100, 2)


    def berechne_planungsfortschritt(self) -> float:
        """Berechnet den Fortschritt des Studiengangs für die Zeitplanung."""

        if self.__ziel_ects == 0:
            return 0.0  # Vermeidet Division durch Null, falls Ziel-ECTS 0 ist

        planungs_ects = 0.0

        # Berechnung des gewichteten Planungsfortschritts basierend auf den ECTS-Punkten der Module
        for modul in self.alle_module():
            modulfortschritt = modul.berechne_planungsfortschritt()
            planungs_ects += modulfortschritt / 100 * modul.ects

        return round(planungs_ects / self.__ziel_ects * 100, 2)


    def berechne_notendurchschnitt(self) -> float | None:
        """Berechnet den Notendurchschnitt des Studiengangs basierend auf den bewerteten Modulen."""

        benotete_module = [
            modul
            for modul in self.alle_module()
            if modul.status == ModulStatus.BESTANDEN
            and modul.pruefungsleistung.note is not None
        ]

        if not benotete_module:
            return None

        ects_summe = sum(modul.ects for modul in benotete_module)
        gewichtete_noten = sum(
            modul.pruefungsleistung.note * modul.ects
            for modul in benotete_module
            if modul.pruefungsleistung.note is not None
        )
        return round(gewichtete_noten / ects_summe, 2)


    def berechne_zeitfortschritt(self, heute: date) -> float:
        """Berechnet den Fortschritt der vergangenen Zeit im Verhältnis zu der gesamten Zeit"""
        _pruefe_datum(heute, "Das Vergleichsdatum")
        enddatum = self.__geplantes_enddatum
        startdatum = self.__startdatum

        gesamte_tage = (enddatum - startdatum).days
        if gesamte_tage <= 0:
            raise ValueError("Das Enddatum muss nach dem Startdatum sein")
        
        vergangene_tage = (heute - startdatum).days

        if vergangene_tage < 0:
            return 0.0
        else: 
            return round(vergangene_tage / gesamte_tage * 100, 2)

    def vergleiche_fortschritt_mit_studienzeit(self, heute: date) -> float:
        """Gibt Planungsfortschritt minus vergangene Studienzeit zurück."""

        return round(
            self.berechne_planungsfortschritt()
            - self.berechne_zeitfortschritt(heute),
            2
        )


    def ermittle_zeitplan_status(self, heute: date) -> ZeitplanStatus:
        """Ermittelt den Zeitplanstatus anhand von Fortschritt und vergangener Zeit."""

        differenz = self.vergleiche_fortschritt_mit_studienzeit(heute)

        if differenz > ZEITPLAN_TOLERANZ_PROZENT:
            return ZeitplanStatus.VORSPRUNG
        elif differenz >= -ZEITPLAN_TOLERANZ_PROZENT:
            return ZeitplanStatus.IM_ZEITPLAN
        else:
            return ZeitplanStatus.IM_VERZUG

    def zielnote_erreicht(self) -> bool | None:
        """Vergleicht den aktuellen Notendurchschnitt mit der Zielnote."""

        durchschnitt = self.berechne_notendurchschnitt()
        if durchschnitt is None:
            return None
        return durchschnitt <= self.__zielnote

    @property
    def name(self) -> str:
        """Gibt den Namen zurück"""
        return self.__name

    @property
    def startdatum(self) -> date:
        """Gibt das Startdatum zurück"""
        return self.__startdatum

    @property
    def geplantes_enddatum(self) -> date:
        """Gibt das geplante Enddatum zurück zurück"""
        return self.__geplantes_enddatum

    @property
    def ziel_ects(self) -> int:
        """Gibt Ziel ECTS zurück"""
        return self.__ziel_ects

    @property
    def zielnote(self) -> float:
        """Gibt Zielnote zurück"""
        return self.__zielnote

    @property
    def semester(self) -> list[Semester]:
        """Gibt eine Kopie der Semester wieder"""
        return self.__semester.copy()
