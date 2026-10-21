"""Tests für die Ablaufsteuerung des Studiendashboards."""

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from benutzeroberflaeche import DashboardGUI
from dashboard_controller import DashboardController
from datenverwaltung import Datenverwaltung
from modelle import Modul, ModulStatus, Pruefungsform, Studiengang


class DashboardControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporaerer_ordner = TemporaryDirectory()
        dateipfad = Path(self.temporaerer_ordner.name) / "studiendaten.json"
        self.datenverwaltung = Datenverwaltung(dateipfad)
        self.studiengang = Studiengang(
            "Teststudiengang",
            date(2026, 4, 1),
            date(2030, 4, 1),
            180,
            2.0
        )
        self.modul = Modul(
            "TEST01",
            "Testmodul",
            5,
            Pruefungsform.KLAUSUR
        )
        self.studiengang.semester[0].modul_hinzufuegen(self.modul)
        self.controller = DashboardController(
            self.studiengang,
            self.datenverwaltung
        )

    def tearDown(self) -> None:
        self.temporaerer_ordner.cleanup()

    def test_start_und_lernfortschritt_werden_gespeichert(self) -> None:
        lernstatus = [
            (lernabschnitt, index == 0)
            for index, lernabschnitt in enumerate(self.modul.lernabschnitte)
        ]

        self.controller.modulaenderungen_speichern(
            self.modul,
            date(2026, 4, 1),
            lernstatus,
            None,
            None,
            None
        )

        self.assertEqual(self.modul.status, ModulStatus.IN_BEARBEITUNG)
        self.assertEqual(self.modul.berechne_lernfortschritt(), 16.67)
        self.assertTrue(self.datenverwaltung.datei_vorhanden())

    def test_bearbeitung_ohne_modulstart_wird_abgelehnt(self) -> None:
        lernstatus = [
            (lernabschnitt, index == 0)
            for index, lernabschnitt in enumerate(self.modul.lernabschnitte)
        ]

        with self.assertRaisesRegex(ValueError, "gestartet"):
            self.controller.modulaenderungen_speichern(
                self.modul,
                None,
                lernstatus,
                None,
                None,
                None
            )

        self.assertEqual(self.modul.status, ModulStatus.NICHT_BEGONNEN)

    def test_controller_verwaltet_modulauswahl_und_zuruecksetzen(self) -> None:
        self.controller.modul_auswaehlen(self.modul)
        self.assertIs(self.controller.ausgewaehltes_modul, self.modul)

        self.modul.starten(date(2026, 4, 1))
        self.modul.lernabschnitte[0].abschliessen()
        self.controller.modul_zuruecksetzen(self.modul)

        self.assertEqual(self.modul.status, ModulStatus.NICHT_BEGONNEN)
        self.assertEqual(self.modul.berechne_lernfortschritt(), 0.0)

    def test_aktuelles_modul_folgt_fachlicher_prioritaet(self) -> None:
        zweites_modul = Modul(
            "TEST02",
            "Zweites Testmodul",
            5,
            Pruefungsform.KLAUSUR
        )
        self.studiengang.semester[0].modul_hinzufuegen(zweites_modul)

        self.assertIs(self.controller.aktuelles_modul(), self.modul)

        zweites_modul.starten(date(2026, 4, 1))
        self.assertIs(self.controller.aktuelles_modul(), zweites_modul)

        zweites_modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 1),
            None,
            None
        )
        self.assertIs(self.controller.aktuelles_modul(), zweites_modul)

    def test_beenden_speichert_den_studiengang(self) -> None:
        self.controller.beenden()

        self.assertTrue(self.datenverwaltung.datei_vorhanden())

    def test_leeres_optionales_datum_wird_zu_none(self) -> None:
        einlesen = (
            DashboardGUI._DashboardGUI__optionales_datum_einlesen
        )

        self.assertIsNone(einlesen("   ", "Das Abgabedatum"))
        self.assertEqual(
            einlesen("03.05.2026", "Das Abgabedatum"),
            date(2026, 5, 3)
        )


if __name__ == "__main__":
    unittest.main()
