"""Fachliche Klassen und Enumerationen des Studiendashboards."""

from datetime import date
from enum import Enum

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

    def __init__(self, nummer: int, bezeichnung: str):
        """Erstellt einen noch nicht erledigten Lernabschnitt."""

        self.__nummer = nummer
        self.__bezeichnung = bezeichnung
        self.__erledigt = False

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

        self.__pruefungsform = pruefungsform
        self.__abgabedatum: date | None = None
        self.__ergebnisdatum: date | None = None
        self.__note: float | None = None

    def abgeben(self, abgabedatum: date) -> None:
        """Markiert die Prüfungsleistung als abgegeben."""

        self.__abgabedatum = abgabedatum

    def ergebnis_eintragen(self, note: float, datum: date) -> None:
        """Trägt das Ergebnis der Prüfungsleistung ein."""

        if not self.ist_abgegeben():
            raise ValueError("Die Prüfungsleistung muss zuerst abgegeben werden, bevor ein Ergebnis eingetragen werden kann.")
        
        if 1.0 <= note <= 5.0:
            self.__ergebnisdatum = datum
            self.__note = note
        else:
            raise ValueError("Die Note muss zwischen 1.0 und 5.0 liegen.")

    def ist_abgegeben(self) -> bool:
        """Gibt zurück, ob die Prüfungsleistung abgegeben wurde."""

        return self.__abgabedatum is not None

    def ist_bewertet(self) -> bool:
        """Gibt zurück, ob die Prüfungsleistung bewertet wurde."""

        return self.__note is not None

    def ist_bestanden(self) -> bool | None:
        """Gibt zurück, ob die Prüfungsleistung bestanden wurde."""

        if self.__note is not None and self.__note <= 4.0:
            return True
        elif self.__note is not None and self.__note > 4.0:
            return False
        else:
            return None

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

    def __init__(self, kurscode: str, name: str, ects: int, geplante_dauer_in_tagen: int, pruefungsform: Pruefungsform):
        """Erstellt ein noch nicht begonnenes Modul."""

        self.__kurscode = kurscode
        self.__name = name
        self.__ects = ects
        self.__geplante_dauer_in_tagen = geplante_dauer_in_tagen
        self.__pruefungsleistung = Pruefungsleistung(pruefungsform)
        self.__lernabschnitte: list[Lernabschnitt] = []
        self.__lernabschnitte_erstellen()
        self.__startdatum: date | None = None


    def __lernabschnitte_erstellen(self) -> None:
        """Erstellt automatisch die 6 Lernabschnitte des Moduls."""
        
        for nummer in range(1, 7):
            bezeichnung = f"Lernabschnitt {nummer}"
            lernabschnitt = Lernabschnitt(nummer, bezeichnung)
            self.__lernabschnitte.append(lernabschnitt)



    def starten(self, datum: date) -> None:
        """Startet das Modul mit dem angegeben Datum."""

        if self.__startdatum is not None:
            raise ValueError("Das Modul wurde bereits gestartet.")
        self.__startdatum = datum



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

        if self.__startdatum is None:
            return 0.0

        vergangene_tage = (heute - self.__startdatum).days

        if vergangene_tage < 0:
            return 0.0  # Das Startdatum liegt in der Zukunft
        else:
            bearbeitungsfortschritt = (vergangene_tage / self.__geplante_dauer_in_tagen) * 100
            return round(bearbeitungsfortschritt, 2)



    def ermittle_status(self) -> ModulStatus:
        """Ermittelt den aktuellen Status des Moduls."""

        # Wenn es kein Startdatum gibt, ist das Modul noch nicht begonnen
        if self.__startdatum is None:
            return ModulStatus.NICHT_BEGONNEN
        # wenn das modul abgegeben wurde aber noch nicht bewertet wurde, ist das ergebnis ausstehend
        elif self.__pruefungsleistung.ist_abgegeben() and not self.__pruefungsleistung.ist_bewertet():
            return ModulStatus.ERGEBNIS_AUSSTEHEND
        # wenn das modul bewertet wurde, wird überprüft ob es bestanden wurde oder nicht
        elif self.__pruefungsleistung.ist_bewertet():
            if self.__pruefungsleistung.ist_bestanden():
                return ModulStatus.BESTANDEN
            else:
                return ModulStatus.NICHT_BESTANDEN
        # übrig bleibt nur noch der fall, dass es in bearbeitung ist
        else:
            return ModulStatus.IN_BEARBEITUNG



    def ermittle_zeitplan_status(self, heute: date) -> ZeitplanStatus:
        """Ermittelt den Zeitplanstatus anhand von Fortschritt und vergangener Zeit."""

        planungsfortschritt = self.berechne_planungsfortschritt()
        bearbeitungsfortschritt = self.berechne_bearbeitungsfortschritt(heute)

        # Planungsfortschriit - Bearbeitungsfortschritt = ZeitplanStatus
        differenz = planungsfortschritt - bearbeitungsfortschritt

        if differenz > 5:
            return ZeitplanStatus.VORSPRUNG
        elif -5 <= differenz <= 5:
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

        self.__nummer = nummer
        self.__bezeichnung = bezeichnung
        self.__module: list[Modul] = []


    def modul_hinzufuegen(self, modul: Modul) -> None:
        """Fügt ein Modul dem Semester hinzu."""

        self.__module.append(modul)


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

        self.__name = name
        self.__startdatum = startdatum
        self.__geplantes_enddatum = geplantes_enddatum
        self.__ziel_ects = ziel_ects
        self.__zielnote = zielnote
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


    def hat_aktives_modul(self) -> bool:
        """Gibt zurück ob Studiengang ein aktives Modul hat, falls ja darf kein weiteres gestartet werden.
        Falls das Modul bereits abgegeben wurde (ModulStatus - ERGEBNIS_AUSSTEHEND), darf ein neues gestartet werden."""

        for modul in self.alle_module():
            if modul.ermittle_status() == ModulStatus.IN_BEARBEITUNG:
                return True
        return False


    def starte_modul(self, modul: Modul, datum: date) -> None:
        """Startet ein Modul des Studiengangs, falls kein anderes Modul aktiv ist."""

        if modul not in self.alle_module():
            raise ValueError("Das Modul gehört nicht zu diesem Studiengang.")
        if not Studiengang.hat_aktives_modul(self):
            modul.starten(datum)
        else:
            raise ValueError("Es darf nur ein Modul gleichzeitig bearbeitet werden.")


    def berechne_erreichte_ects(self) -> int:
        """Berechnet die erreichten ECTS-Punkte des Studiengangs."""

        erreichte_ects = 0
        for modul in self.alle_module():
            if modul.ermittle_status() == ModulStatus.BESTANDEN:
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

        noten = []
        for modul in self.alle_module():
            if modul.ermittle_status() == ModulStatus.BESTANDEN:
                note = modul.pruefungsleistung.note
                if note is not None:
                    noten.append(note)

        if len(noten) == 0:
            return None

        notendurchschnitt = sum(noten) / len(noten)

        return round(notendurchschnitt, 2)


    def berechne_zeitfortschritt(self, heute: date) -> float:
        """Berechnet den Fortschritt der vergangenen Zeit im Verhältnis zu der gesamten Zeit"""
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


    def ermittle_zeitplan_status(self, heute: date) -> ZeitplanStatus:
        """Ermittelt den Zeitplanstatus anhand von Fortschritt und vergangener Zeit."""

        planungsfortschritt = self.berechne_planungsfortschritt()
        zeitfortschritt = self.berechne_zeitfortschritt(heute)

        # Planungsfortschritt - Zeitfortschritt = ZeitplanStatus
        differenz = planungsfortschritt - zeitfortschritt

        if differenz > 5:
            return ZeitplanStatus.VORSPRUNG
        elif -5 <= differenz <= 5:
            return ZeitplanStatus.IM_ZEITPLAN
        else:
            return ZeitplanStatus.IM_VERZUG

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