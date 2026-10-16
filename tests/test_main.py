"""Tests für die Anlage des vollständigen Studienverlaufsplans."""

import unittest

from main import ergaenze_studienmodule, erstelle_neuen_studiengang


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


if __name__ == "__main__":
    unittest.main()
