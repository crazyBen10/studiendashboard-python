"""Automatisierte Tests für das fachliche Domänenmodell."""

from datetime import date
import unittest

from modelle import (
    Lernabschnitt,
    Modul,
    ModulStatus,
    Pruefungsform,
    Studiengang,
    ZeitplanStatus,
)


class PruefungsleistungUndModulTest(unittest.TestCase):
    def setUp(self) -> None:
        self.modul = Modul(
            "TEST01",
            "Testmodul",
            5,
            Pruefungsform.KLAUSUR
        )

    def test_status_wird_aus_fachdaten_abgeleitet(self) -> None:
        self.assertEqual(self.modul.status, ModulStatus.NICHT_BEGONNEN)
        self.assertIsNone(self.modul.pruefungsleistung.ist_bestanden())

        self.modul.starten(date(2026, 4, 1))
        self.assertEqual(self.modul.status, ModulStatus.IN_BEARBEITUNG)

        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 15),
            None,
            None
        )
        self.assertEqual(self.modul.status, ModulStatus.ERGEBNIS_AUSSTEHEND)

        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 15),
            4.0,
            date(2026, 5, 20)
        )
        self.assertTrue(self.modul.pruefungsleistung.ist_bestanden())
        self.assertEqual(self.modul.status, ModulStatus.BESTANDEN)

        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 15),
            4.1,
            date(2026, 5, 20)
        )
        self.assertFalse(self.modul.pruefungsleistung.ist_bestanden())
        self.assertEqual(self.modul.status, ModulStatus.NICHT_BESTANDEN)

    def test_pruefungsdaten_bleiben_bei_fehler_unveraendert(self) -> None:
        self.modul.starten(date(2026, 4, 1))
        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 1),
            2.0,
            date(2026, 5, 5)
        )

        with self.assertRaises(ValueError):
            self.modul.pruefungsdaten_aktualisieren(
                date(2026, 5, 1),
                0.7,
                date(2026, 5, 5)
            )

        self.assertEqual(self.modul.pruefungsleistung.note, 2.0)
        self.assertEqual(
            self.modul.pruefungsleistung.ergebnisdatum,
            date(2026, 5, 5)
        )

    def test_datumsreihenfolge_wird_geprueft(self) -> None:
        self.modul.starten(date(2026, 4, 1))

        with self.assertRaises(ValueError):
            self.modul.pruefungsdaten_aktualisieren(
                date(2026, 5, 2),
                2.0,
                date(2026, 5, 1)
            )

    def test_lernfortschritt_und_zeitvergleich(self) -> None:
        self.modul.starten(date(2026, 4, 1))
        for lernabschnitt in self.modul.lernabschnitte[:3]:
            lernabschnitt.abschliessen()

        self.assertEqual(self.modul.berechne_lernfortschritt(), 50.0)
        self.assertEqual(
            self.modul.vergleiche_lernfortschritt_mit_bearbeitungszeit(
                date(2026, 4, 19)
            ),
            0.0
        )
        self.assertEqual(
            self.modul.ermittle_zeitplan_status(date(2026, 4, 19)),
            ZeitplanStatus.IM_ZEITPLAN
        )

    def test_planungsfortschritt_verwendet_sieben_schritte(self) -> None:
        self.modul.starten(date(2026, 4, 1))
        for lernabschnitt in self.modul.lernabschnitte:
            lernabschnitt.abschliessen()

        self.assertEqual(self.modul.berechne_planungsfortschritt(), 85.71)

        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 1),
            None,
            None
        )
        self.assertEqual(self.modul.berechne_planungsfortschritt(), 100.0)

        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 1),
            5.0,
            date(2026, 5, 5)
        )
        self.assertEqual(self.modul.berechne_planungsfortschritt(), 85.71)

    def test_restzeit_basiert_auf_sechs_wochen_moduldauer(self) -> None:
        self.modul.starten(date(2026, 9, 12))

        self.assertEqual(
            self.modul.berechne_restzeit_in_tagen(date(2026, 9, 12)),
            42
        )
        self.assertEqual(
            self.modul.berechne_restzeit_in_tagen(date(2026, 10, 14)),
            10
        )
        self.assertEqual(
            self.modul.berechne_restzeit_in_tagen(date(2026, 10, 25)),
            -1
        )

    def test_moduldauer_wird_aus_den_ects_abgeleitet(self) -> None:
        bachelorarbeit = Modul(
            "BACHELOR",
            "Bachelorarbeit",
            10,
            Pruefungsform.BACHELORARBEIT
        )
        praktikum = Modul(
            "PRAKTIKUM",
            "Praktikum",
            30,
            Pruefungsform.PRAXISREFLEXION
        )

        self.assertEqual(self.modul.geplante_dauer_in_tagen, 42)
        self.assertEqual(bachelorarbeit.geplante_dauer_in_tagen, 84)
        self.assertEqual(praktikum.geplante_dauer_in_tagen, 252)

    def test_modul_hat_genau_sechs_lernabschnitte(self) -> None:
        self.assertEqual(len(self.modul.lernabschnitte), 6)
        self.assertTrue(
            all(isinstance(abschnitt, Lernabschnitt)
                for abschnitt in self.modul.lernabschnitte)
        )

    def test_modul_kann_vollstaendig_zurueckgesetzt_werden(self) -> None:
        self.modul.starten(date(2026, 4, 1))
        for lernabschnitt in self.modul.lernabschnitte[:3]:
            lernabschnitt.abschliessen()
        self.modul.pruefungsdaten_aktualisieren(
            date(2026, 5, 15),
            2.0,
            date(2026, 5, 20)
        )

        self.modul.zuruecksetzen()

        self.assertIsNone(self.modul.startdatum)
        self.assertEqual(self.modul.status, ModulStatus.NICHT_BEGONNEN)
        self.assertEqual(self.modul.berechne_lernfortschritt(), 0.0)
        self.assertTrue(
            all(
                not lernabschnitt.ist_erledigt()
                for lernabschnitt in self.modul.lernabschnitte
            )
        )
        self.assertIsNone(self.modul.pruefungsleistung.abgabedatum)
        self.assertIsNone(self.modul.pruefungsleistung.note)
        self.assertIsNone(self.modul.pruefungsleistung.ergebnisdatum)


class StudiengangTest(unittest.TestCase):
    def setUp(self) -> None:
        self.studiengang = Studiengang(
            "B.Sc. Angewandte Künstliche Intelligenz",
            date(2026, 4, 1),
            date(2030, 4, 1),
            180,
            2.0
        )

    def _modul(self, code: str, ects: int = 5) -> Modul:
        modul = Modul(
            code,
            f"Modul {code}",
            ects,
            Pruefungsform.PORTFOLIO
        )
        self.studiengang.semester[0].modul_hinzufuegen(modul)
        return modul

    def test_nur_ein_modul_darf_aktiv_sein(self) -> None:
        erstes = self._modul("TEST01")
        zweites = self._modul("TEST02")

        self.studiengang.starte_modul(erstes, date(2026, 4, 1))
        with self.assertRaises(ValueError):
            self.studiengang.starte_modul(zweites, date(2026, 4, 2))

        erstes.pruefungsdaten_aktualisieren(
            date(2026, 5, 1),
            None,
            None
        )
        self.studiengang.starte_modul(zweites, date(2026, 5, 2))
        self.assertEqual(zweites.status, ModulStatus.IN_BEARBEITUNG)

    def test_ects_und_notendurchschnitt_sind_abgeleitet(self) -> None:
        kleines_modul = self._modul("TEST01", ects=5)
        grosses_modul = self._modul("TEST02", ects=10)

        for modul, note in ((kleines_modul, 1.0), (grosses_modul, 3.0)):
            modul.starten(date(2026, 4, 1))
            modul.pruefungsdaten_aktualisieren(
                date(2026, 5, 1),
                note,
                date(2026, 5, 5)
            )

        self.assertEqual(self.studiengang.berechne_erreichte_ects(), 15)
        self.assertEqual(
            self.studiengang.berechne_notendurchschnitt(),
            2.0
        )
        self.assertTrue(self.studiengang.zielnote_erreicht())

    def test_ungueltige_ziele_werden_abgelehnt(self) -> None:
        with self.assertRaises(ValueError):
            Studiengang(
                "Test",
                date(2026, 4, 1),
                date(2026, 4, 1),
                180,
                2.0
            )
        with self.assertRaises(ValueError):
            Studiengang(
                "Test",
                date(2026, 4, 1),
                date(2030, 4, 1),
                0,
                2.0
            )


if __name__ == "__main__":
    unittest.main()
