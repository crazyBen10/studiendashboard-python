"""Startpunkt und Initialisierung des Studiendashboards."""

from datetime import date
from pathlib import Path

from dashboard_controller import DashboardController
from datenverwaltung import Datenverwaltung
from modelle import Modul, Pruefungsform, Studiengang


def erstelle_neuen_studiengang() -> Studiengang:
    """Erstellt den fest vorgegebenen Studiengang beim ersten Programmstart."""

    return Studiengang(
        "B.Sc. Angewandte Künstliche Intelligenz",
        date(2026, 4, 1),
        date(2030, 4, 1),
        180,
        2.0
    )


def ergaenze_studienmodule(studiengang: Studiengang) -> None:
    """Ergänzt den Studienverlaufsplan, ohne vorhandene Daten zu ersetzen."""

    modulplan = (
        (1, "DLBDSEAIS01-01_D", "Artificial Intelligence", 5, Pruefungsform.KLAUSUR),
        (1, "DLBDSIPWP01_D", "Einführung in die Programmierung mit Python", 5, Pruefungsform.KLAUSUR),
        (1, "DLBBIMD01", "Mathematik: Analysis", 5, Pruefungsform.KLAUSUR),
        (1, "DLBWIRITT01", "Einführung in das wissenschaftliche Arbeiten für IT und Technik", 5, Pruefungsform.ADVANCED_WORKBOOK),
        (1, "DLBDSOOFPP01_D", "Projekt: Objektorientierte und funktionale Programmierung mit Python", 5, Pruefungsform.PORTFOLIO),
        (2, "AKI-S2-STAT-DESK", "Statistik - Wahrscheinlichkeit und deskriptive Statistik", 5, Pruefungsform.KLAUSUR),
        (2, "AKI-S2-STAT-IND", "Statistik - Induktive Statistik", 5, Pruefungsform.KLAUSUR),
        (2, "AKI-S2-CLOUD", "Cloud Computing", 5, Pruefungsform.KLAUSUR),
        (2, "AKI-S2-LINALG", "Mathematik: Lineare Algebra", 5, Pruefungsform.KLAUSUR),
        (3, "AKI-S3-NLP", "Einführung in NLP", 5, Pruefungsform.KLAUSUR),
        (3, "AKI-S3-NLP-PROJEKT", "Projekt: NLP", 5, Pruefungsform.PROJEKTBERICHT),
        (3, "AKI-S3-ML-SUP", "Maschinelles Lernen - Supervised Learning", 5, Pruefungsform.KLAUSUR),
        (3, "AKI-S3-ML-UNSUP", "Maschinelles Lernen - Unsupervised Learning und Feature Engineering", 5, Pruefungsform.FALLSTUDIE),
        (3, "AKI-S3-DEEP", "Neuronale Netze und Deep Learning", 5, Pruefungsform.FACHPRAESENTATION),
        (4, "AKI-S4-CV", "Einführung in Computer Vision", 5, Pruefungsform.KLAUSUR),
        (4, "AKI-S4-CV-PROJEKT", "Projekt: Computer Vision", 5, Pruefungsform.PROJEKTBERICHT),
        (4, "AKI-S4-RL", "Einführung in das Reinforcement Learning", 5, Pruefungsform.KLAUSUR),
        (4, "AKI-S4-DATENSCHUTZ", "Einführung in Datenschutz und IT-Sicherheit", 5, Pruefungsform.KLAUSUR),
        (5, "AKI-S5-ETHIK", "Seminar: Ethische Innovation", 5, Pruefungsform.SEMINARARBEIT),
        (5, "AKI-S5-CLOUD-PROJEKT", "Projekt: Cloud Programming", 5, Pruefungsform.PORTFOLIO),
        (5, "AKI-S5-EDGE", "Projekt: Edge AI", 5, Pruefungsform.PROJEKTBERICHT),
        (5, "AKI-WPA-1", "Wahlpflichtbereich A - Modul 1 (Auswahl ergänzen)", 5, Pruefungsform.NOCH_NICHT_FESTGELEGT),
        (5, "AKI-WPA-2", "Wahlpflichtbereich A - Modul 2 (Auswahl ergänzen)", 5, Pruefungsform.NOCH_NICHT_FESTGELEGT),
        (6, "AKI-WPB-1", "Wahlpflichtbereich B - Modul 1 (Auswahl ergänzen)", 5, Pruefungsform.NOCH_NICHT_FESTGELEGT),
        (6, "AKI-WPB-2", "Wahlpflichtbereich B - Modul 2 (Auswahl ergänzen)", 5, Pruefungsform.NOCH_NICHT_FESTGELEGT),
        (6, "AKI-WPC-1", "Wahlpflichtbereich C - Modul 1 (Auswahl ergänzen)", 5, Pruefungsform.NOCH_NICHT_FESTGELEGT),
        (6, "AKI-WPC-2", "Wahlpflichtbereich C - Modul 2 (Auswahl ergänzen)", 5, Pruefungsform.NOCH_NICHT_FESTGELEGT),
        (7, "AKI-S7-MODEL", "Model Engineering", 5, Pruefungsform.FALLSTUDIE),
        (7, "AKI-S7-BACHELOR", "Bachelorarbeit", 10, Pruefungsform.BACHELORARBEIT),
        (8, "AKI-S8-PRAKTIKUM", "Praktikum: Bachelor Data Science und KI", 30, Pruefungsform.PRAXISREFLEXION),
    )

    vorhandene_module = {
        modul.kurscode: (semester, modul)
        for semester in studiengang.semester
        for modul in semester.module
    }
    for semester_nummer, kurscode, name, ects, pruefungsform in modulplan:
        zielsemester = studiengang.semester[semester_nummer - 1]
        if kurscode in vorhandene_module:
            bisheriges_semester, vorhandenes_modul = vorhandene_module[kurscode]
            if bisheriges_semester is not zielsemester:
                bisheriges_semester.modul_entfernen(vorhandenes_modul)
                zielsemester.modul_hinzufuegen(vorhandenes_modul)
            continue
        zielsemester.modul_hinzufuegen(
            Modul(kurscode, name, ects, pruefungsform)
        )


class Anwendung:
    """Initialisiert Datenhaltung, Fachmodell, Controller und Oberfläche."""

    def __init__(self, dateipfad: str | Path | None = None) -> None:
        """Legt den Speicherpfad für die Studiendaten fest."""

        self.__dateipfad = (
            Path(dateipfad)
            if dateipfad is not None
            else Path(__file__).parent / "daten" / "studiendaten.json"
        )

    def starten(self) -> None:
        """Lädt die Daten und startet das Dashboard über den Controller."""

        datenverwaltung = Datenverwaltung(self.__dateipfad)
        studiengang = datenverwaltung.laden()

        if studiengang is None:
            studiengang = erstelle_neuen_studiengang()

        ergaenze_studienmodule(studiengang)
        datenverwaltung.speichern(studiengang)

        controller = DashboardController(studiengang, datenverwaltung)
        controller.starten()


def main() -> None:
    """Erzeugt die Anwendung und startet sie."""

    Anwendung().starten()


if __name__ == "__main__":
    main()
