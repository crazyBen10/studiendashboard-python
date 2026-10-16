"""Automatisierte Tests für die JSON-Datenverwaltung."""

from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from datenverwaltung import Datenfehler, Datenverwaltung
from modelle import Modul, ModulStatus, Pruefungsform, Studiengang


class DatenverwaltungTest(unittest.TestCase):
    def _erstelle_studiengang(self) -> Studiengang:
        studiengang = Studiengang(
            "B.Sc. Angewandte Künstliche Intelligenz",
            date(2026, 4, 1),
            date(2030, 4, 1),
            180,
            2.0
        )
        modul = Modul(
            "DLBDSOOFPP01",
            "Objektorientierte und funktionale Programmierung mit Python",
            5,
            Pruefungsform.PORTFOLIO
        )
        studiengang.semester[0].modul_hinzufuegen(modul)
        studiengang.starte_modul(modul, date(2026, 4, 1))
        modul.lernabschnitte[0].abschliessen()
        modul.lernabschnitte[1].abschliessen()
        modul.pruefungsdaten_aktualisieren(
            date(2026, 6, 1),
            2.3,
            date(2026, 6, 10)
        )
        return studiengang

    def test_speichern_und_laden(self) -> None:
        with TemporaryDirectory() as temporaerer_ordner:
            dateipfad = Path(temporaerer_ordner) / "studiendaten.json"
            datenverwaltung = Datenverwaltung(dateipfad)
            datenverwaltung.speichern(self._erstelle_studiengang())

            geladener_studiengang = datenverwaltung.laden()

            self.assertIsNotNone(geladener_studiengang)
            assert geladener_studiengang is not None
            self.assertEqual(
                geladener_studiengang.name,
                "B.Sc. Angewandte Künstliche Intelligenz"
            )
            self.assertEqual(len(geladener_studiengang.semester), 8)
            self.assertEqual(len(geladener_studiengang.alle_module()), 1)

            modul = geladener_studiengang.alle_module()[0]
            self.assertEqual(modul.startdatum, date(2026, 4, 1))
            self.assertEqual(modul.berechne_lernfortschritt(), 33.33)
            self.assertEqual(
                modul.pruefungsleistung.pruefungsform,
                Pruefungsform.PORTFOLIO
            )
            self.assertEqual(modul.pruefungsleistung.note, 2.3)
            self.assertEqual(modul.status, ModulStatus.BESTANDEN)

    def test_abgeleitete_werte_werden_nicht_gespeichert(self) -> None:
        with TemporaryDirectory() as temporaerer_ordner:
            dateipfad = Path(temporaerer_ordner) / "studiendaten.json"
            Datenverwaltung(dateipfad).speichern(self._erstelle_studiengang())
            daten = json.loads(dateipfad.read_text(encoding="utf-8"))

            self.assertEqual(daten["schema_version"], 2)
            modul = daten["semester"][0]["module"][0]
            self.assertNotIn("status", modul)
            self.assertNotIn("bestanden", modul["pruefungsleistung"])

    def test_ungueltiges_json_wird_verstaendlich_gemeldet(self) -> None:
        with TemporaryDirectory() as temporaerer_ordner:
            dateipfad = Path(temporaerer_ordner) / "studiendaten.json"
            dateipfad.write_text("{ungueltig", encoding="utf-8")

            with self.assertRaises(Datenfehler):
                Datenverwaltung(dateipfad).laden()


if __name__ == "__main__":
    unittest.main()
