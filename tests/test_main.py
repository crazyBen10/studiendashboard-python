"""Tests für die Anlage des vollständigen Studienverlaufsplans."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from main import Anwendung, ergaenze_studienmodule, erstelle_neuen_studiengang


class StudienverlaufsplanTest(unittest.TestCase):
    def test_modulplan_ist_vollstaendig_und_wiederholbar(self) -> None:
        studiengang = erstelle_neuen_studiengang()

        ergaenze_studienmodule(studiengang)
        ergaenze_studienmodule(studiengang)

        self.assertEqual(len(studiengang.alle_module()), 30)
        self.assertEqual(
            sum(modul.ects for modul in studiengang.alle_module()),
            180
        )
        self.assertEqual(
            [sum(modul.ects for modul in semester.module)
             for semester in studiengang.semester],
            [25, 20, 25, 20, 25, 20, 15, 30]
        )

        module_nach_name = {
            modul.name: modul for modul in studiengang.alle_module()
        }
        self.assertEqual(
            module_nach_name["Bachelorarbeit"].geplante_dauer_in_tagen,
            84
        )
        self.assertEqual(
            module_nach_name[
                "Praktikum: Bachelor Data Science und KI"
            ].geplante_dauer_in_tagen,
            252
        )

    def test_anwendung_initialisiert_und_startet_controller(self) -> None:
        with TemporaryDirectory() as ordner:
            dateipfad = Path(ordner) / "studiendaten.json"

            with patch("main.DashboardController") as controller_klasse:
                Anwendung(dateipfad).starten()

            self.assertTrue(dateipfad.exists())
            controller_klasse.assert_called_once()
            controller_klasse.return_value.starten.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
