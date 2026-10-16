"""Laden und Speichern der Studiendaten im JSON-Format."""

from datetime import date
import json
from pathlib import Path

from modelle import (
    Lernabschnitt,
    Modul,
    Pruefungsform,
    Pruefungsleistung,
    Semester,
    Studiengang,
)


class Datenfehler(ValueError):
    """Kennzeichnet ungültige oder unvollständige gespeicherte Daten."""


class Datenverwaltung:
    """
    Speichert und lädt die Studiendaten im JSON-Format.

    Da eigene Python-Objekte nicht direkt als JSON gespeichert werden können,
    werden sie vorher in dictionarys umgewandelt und beim laden wieder
    als Objekte hergestellt.
    """

    SCHEMA_VERSION = 2

    def __init__(self, dateipfad: str | Path):
        """Erstellt die Datenverwaltung für den angegebenen Dateipfad."""

        self.__dateipfad = Path(dateipfad)


    def datei_vorhanden(self) -> bool:
        """Gibt zurück, ob die angegebene Datendatei vorhanden ist."""

        return self.__dateipfad.exists()

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Als nächstes erstellen wir Methoden die dazu dienen unsere Daten in die richtige Form (Dictionarys) umzuwandeln damit wir sie auch in JSON speichern können
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __lernabschnitt_in_dict(self,lernabschnitt: Lernabschnitt) -> dict:
        """Wandelt einen Lernabschnitt für die JSON-Speicherung in ein Dictionary um."""

        return {
            "nummer": lernabschnitt.nummer,
            "bezeichnung": lernabschnitt.bezeichnung,
            "erledigt": lernabschnitt.ist_erledigt()
        }

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __pruefungsleistung_in_dict(self, pruefungsleistung: Pruefungsleistung) -> dict:
        """Wandelt die Pruefungsleistung für die JSON-Speicherung in ein Dictionary um."""

        abgabedatum = None
        ergebnisdatum = None

        if pruefungsleistung.abgabedatum is not None:
            abgabedatum = pruefungsleistung.abgabedatum.isoformat()
        if pruefungsleistung.ergebnisdatum is not None:
            ergebnisdatum = pruefungsleistung.ergebnisdatum.isoformat()

        return {
            "pruefungsform": pruefungsleistung.pruefungsform.name,
            "abgabedatum": abgabedatum,
            "ergebnisdatum": ergebnisdatum,
            "note": pruefungsleistung.note
        }

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __modul_in_dict(self, modul: Modul) -> dict:
        """Wandelt ein Modul für die JSON-Speicherung in ein Dictionary um."""

        startdatum = None

        if modul.startdatum is not None:
            startdatum = modul.startdatum.isoformat()

        lernabschnitt_daten = []

        for lernabschnitt in modul.lernabschnitte:
            lernabschnitt_daten.append(self.__lernabschnitt_in_dict(lernabschnitt))

        return {
            "kurscode": modul.kurscode,
            "name": modul.name,
            "ects": modul.ects,
            "startdatum": startdatum,
            "geplante_dauer_in_tagen": modul.geplante_dauer_in_tagen,
            "lernabschnitte": lernabschnitt_daten,
            "pruefungsleistung": self.__pruefungsleistung_in_dict(modul.pruefungsleistung)
        }

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------


    def __semester_in_dict(self, semester: Semester) -> dict:
        """Wandelt ein Semester für die JSON-Speicherung in ein Dictionary um"""

        alle_module = []

        for modul in semester.module:
            alle_module.append(self.__modul_in_dict(modul))

        return {
            "nummer": semester.nummer,
            "bezeichnung": semester.bezeichnung,
            "module": alle_module
        }

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __studiengang_in_dict(self, studiengang: Studiengang) -> dict:
        """Wandelt den Studiengang für die JSON-Speicherung in ein Dictionary um"""

        startdatum = None
        geplantes_enddatum = None

        if studiengang.startdatum is not None:
            startdatum = studiengang.startdatum.isoformat()
        if studiengang.geplantes_enddatum is not None:
            geplantes_enddatum = studiengang.geplantes_enddatum.isoformat()

        alle_semester = []

        for semester in studiengang.semester:
            alle_semester.append(self.__semester_in_dict(semester))

        return {
            "schema_version": self.SCHEMA_VERSION,
            "name": studiengang.name ,
            "startdatum": startdatum ,
            "geplantes_enddatum": geplantes_enddatum ,
            "ziel_ects": studiengang.ziel_ects ,
            "zielnote": studiengang.zielnote ,
            "semester": alle_semester
        }

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def speichern(self, studiengang: Studiengang) -> None:
        """Speichert den Studiengang in einer JSON-Datei."""

        daten = self.__studiengang_in_dict(studiengang)

        self.__dateipfad.parent.mkdir(parents=True, exist_ok=True)

        temporaerer_pfad = self.__dateipfad.with_suffix(
            self.__dateipfad.suffix + ".tmp"
        )
        try:
            with temporaerer_pfad.open("w", encoding="utf-8") as json_datei:
                json.dump(daten, json_datei, indent=4, ensure_ascii=False)
                json_datei.write("\n")
            temporaerer_pfad.replace(self.__dateipfad)
        except OSError:
            temporaerer_pfad.unlink(missing_ok=True)
            raise

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __dict_in_lernabschnitt(self, daten: dict) -> Lernabschnitt:
        """
        Erstellt aus gespeicherten Daten wieder einen Lernabschnitt.

        Der gespeicherte Erledigt-Status wird übernommen, damit ein bereits
        abgeschlossener Lernabschnitt nach dem Laden weiterhin erledigt ist.
        """

        return Lernabschnitt(
            daten["nummer"],
            daten["bezeichnung"],
            daten["erledigt"]
        )

    def __dict_in_modul(self, daten: dict) -> Modul:
        """Erstellt aus einem Dictionary wieder ein vollständiges Modul."""

        pruefungsdaten = daten["pruefungsleistung"]

        pruefungsform = Pruefungsform[
            pruefungsdaten["pruefungsform"]
        ]

        lernabschnitte = [
            self.__dict_in_lernabschnitt(lernabschnitt_daten)
            for lernabschnitt_daten in daten["lernabschnitte"]
        ]

        modul = Modul(
            daten["kurscode"],
            daten["name"],
            daten["ects"],
            pruefungsform,
            lernabschnitte
        )

        # Stellt das Startdatum wieder her.
        if daten["startdatum"] is not None:
            startdatum = date.fromisoformat(daten["startdatum"])
            modul.starten(startdatum)

        abgabedatum = (
            date.fromisoformat(pruefungsdaten["abgabedatum"])
            if pruefungsdaten["abgabedatum"] is not None
            else None
        )
        ergebnisdatum = (
            date.fromisoformat(pruefungsdaten["ergebnisdatum"])
            if pruefungsdaten["ergebnisdatum"] is not None
            else None
        )
        modul.pruefungsdaten_aktualisieren(
            abgabedatum,
            pruefungsdaten["note"],
            ergebnisdatum
        )

        return modul

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __dict_in_semester(self, daten: dict) -> Semester:
        """Erstellt aus einem Dictionary wieder ein Semester."""

        semester = Semester(
            daten["nummer"],
            daten["bezeichnung"]
        )

        for modul_daten in daten["module"]:
            modul = self.__dict_in_modul(modul_daten)
            semester.modul_hinzufuegen(modul)

        return semester

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def __dict_in_studiengang(self, daten: dict) -> Studiengang:
        """Erstellt aus einem Dictionary wieder einen Studiengang."""

        startdatum = date.fromisoformat(daten["startdatum"])
        geplantes_enddatum = date.fromisoformat(
            daten["geplantes_enddatum"]
        )

        studiengang = Studiengang(
            daten["name"],
            startdatum,
            geplantes_enddatum,
            daten["ziel_ects"],
            daten["zielnote"]
        )

        for semester_daten in daten["semester"]:
            gespeichertes_semester = self.__dict_in_semester(
                semester_daten
            )

            semester_nummer = gespeichertes_semester.nummer
            vorhandenes_semester = studiengang.semester[
                semester_nummer - 1
            ]

            for modul in gespeichertes_semester.module:
                vorhandenes_semester.modul_hinzufuegen(modul)

        return studiengang

#-----------------------------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------------------------

    def laden(self) -> Studiengang | None:
        """Lädt den gespeicherten Studiengang aus der JSON-Datei."""

        if not self.datei_vorhanden():
            return None

        try:
            with self.__dateipfad.open("r", encoding="utf-8") as json_datei:
                daten = json.load(json_datei)
        except (OSError, json.JSONDecodeError) as fehler:
            raise Datenfehler(
                f"Die Studiendaten konnten nicht gelesen werden: {fehler}"
            ) from fehler

        if not daten:
            return None

        if not isinstance(daten, dict):
            raise Datenfehler("Die Studiendatei muss ein JSON-Objekt enthalten.")

        try:
            return self.__dict_in_studiengang(daten)
        except (KeyError, TypeError, ValueError) as fehler:
            raise Datenfehler(
                f"Die gespeicherten Studiendaten sind ungültig: {fehler}"
            ) from fehler
