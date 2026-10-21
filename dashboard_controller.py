"""Ablaufsteuerung zwischen Benutzeroberfläche, Fachmodell und Speicherung."""

from datetime import date
from typing import TYPE_CHECKING

from datenverwaltung import Datenverwaltung
from modelle import (
    Lernabschnitt,
    Modul,
    ModulStatus,
    Pruefungsleistung,
    Studiengang,
)

if TYPE_CHECKING:
    from benutzeroberflaeche import DashboardGUI


class DashboardController:
    """Steuert das Dashboard, ohne Darstellungslogik zu enthalten."""

    def __init__(
        self,
        studiengang: Studiengang,
        datenverwaltung: Datenverwaltung
    ) -> None:
        """Verbindet das Fachmodell mit der Datenverwaltung."""

        self.__studiengang = studiengang
        self.__datenverwaltung = datenverwaltung
        self.__gui: DashboardGUI | None = None
        self.__ausgewaehltes_modul: Modul | None = None

    def starten(self) -> None:
        """Erstellt und startet die grafische Benutzeroberfläche."""

        # Der lokale Import verhindert eine zyklische Abhängigkeit zwischenb Controller und GUI. 
        # Die GUI kennt den Controller nur als Schnittstelle.
        from benutzeroberflaeche import DashboardGUI

        self.__gui = DashboardGUI(self)
        self.__gui.starten()

    def modul_auswaehlen(self, modul: Modul) -> None:
        """Merkt das ausgewählte Modul für die Hervorhebung im Dashboard."""

        self.__pruefe_modulzugehoerigkeit(modul)
        self.__ausgewaehltes_modul = modul

    def modulaenderungen_speichern(
        self,
        modul: Modul,
        neues_startdatum: date | None,
        lernstatus: list[tuple[Lernabschnitt, bool]],
        abgabedatum: date | None,
        note: float | None,
        ergebnisdatum: date | None
    ) -> None:
        """Validiert, übernimmt und speichert Änderungen an einem Modul."""

        self.__pruefe_modulzugehoerigkeit(modul)
        self.__pruefe_lernstatus(modul, lernstatus)
        Pruefungsleistung.validiere_daten(
            abgabedatum,
            note,
            ergebnisdatum
        )

        fachliche_aenderung = (
            any(
                erledigt != lernabschnitt.ist_erledigt()
                for lernabschnitt, erledigt in lernstatus
            )
            or any(
                wert is not None
                for wert in (abgabedatum, note, ergebnisdatum)
            )
        )

        if modul.startdatum is None:
            if neues_startdatum is None and fachliche_aenderung:
                raise ValueError(
                    "Das Modul muss vor der Bearbeitung gestartet werden."
                )
            if neues_startdatum is not None:
                self.__studiengang.starte_modul(modul, neues_startdatum)
        elif neues_startdatum is None:
            raise ValueError("Für ein gestartetes Modul fehlt das Startdatum.")
        elif neues_startdatum != modul.startdatum:
            modul.startdatum_aendern(neues_startdatum)

        for lernabschnitt, erledigt in lernstatus:
            if erledigt:
                lernabschnitt.abschliessen()
            else:
                lernabschnitt.zuruecksetzen()

        modul.pruefungsdaten_aktualisieren(
            abgabedatum,
            note,
            ergebnisdatum
        )
        self.speichern()
        self.dashboard_aktualisieren()

    def lernabschnitt_abschliessen(
        self,
        modul: Modul,
        lernabschnitt: Lernabschnitt
    ) -> None:
        """Schließt einen Lernabschnitt ab und speichert den neuen Stand."""

        self.__pruefe_modulzugehoerigkeit(modul)
        if lernabschnitt not in modul.lernabschnitte:
            raise ValueError("Der Lernabschnitt gehört nicht zu diesem Modul.")
        if modul.startdatum is None:
            raise ValueError(
                "Das Modul muss vor der Bearbeitung gestartet werden."
            )
        lernabschnitt.abschliessen()
        self.speichern()
        self.dashboard_aktualisieren()

    def pruefung_abgeben(self, modul: Modul, datum: date) -> None:
        """Trägt die Abgabe einer Prüfungsleistung ein und speichert sie."""

        self.__pruefe_modulzugehoerigkeit(modul)
        modul.pruefungsdaten_aktualisieren(datum, None, None)
        self.speichern()
        self.dashboard_aktualisieren()

    def pruefung_eintragen(
        self,
        modul: Modul,
        note: float,
        datum: date
    ) -> None:
        """Trägt ein Prüfungsergebnis ein und speichert es."""

        self.__pruefe_modulzugehoerigkeit(modul)
        modul.pruefungsleistung.ergebnis_eintragen(note, datum)
        self.speichern()
        self.dashboard_aktualisieren()

    def modul_zuruecksetzen(self, modul: Modul) -> None:
        """Setzt ein Modul vollständig zurück und speichert den Stand."""

        self.__pruefe_modulzugehoerigkeit(modul)
        modul.zuruecksetzen()
        self.speichern()
        self.dashboard_aktualisieren()

    def speichern(self) -> None:
        """Speichert den aktuellen Studiengang."""

        self.__datenverwaltung.speichern(self.__studiengang)

    def beenden(self) -> None:
        """Sichert den aktuellen Stand vor dem Beenden der Oberfläche."""

        self.speichern()

    def dashboard_aktualisieren(self) -> None:
        """Fordert die GUI auf, alle angezeigten Werte neu aufzubauen."""

        if self.__gui is not None:
            self.__gui.dashboard_anzeigen()

    def aktuelles_modul(self) -> Modul | None:
        """Ermittelt das für die Hauptansicht relevanteste Modul."""

        module = self.__studiengang.alle_module()
        prioritaeten = (
            ModulStatus.IN_BEARBEITUNG,
            ModulStatus.ERGEBNIS_AUSSTEHEND,
            ModulStatus.NICHT_BEGONNEN,
        )

        for status in prioritaeten:
            for modul in module:
                if modul.status == status:
                    return modul

        return module[-1] if module else None

    def __pruefe_modulzugehoerigkeit(self, modul: Modul) -> None:
        """Verhindert Änderungen an fremden Modulobjekten."""

        if modul not in self.__studiengang.alle_module():
            raise ValueError("Das Modul gehört nicht zu diesem Studiengang.")

    @staticmethod
    def __pruefe_lernstatus(
        modul: Modul,
        lernstatus: list[tuple[Lernabschnitt, bool]]
    ) -> None:
        """Prüft die vom Bearbeitungsformular übergebenen Lernabschnitte."""

        if len(lernstatus) != len(modul.lernabschnitte):
            raise ValueError("Der Lernstatus ist unvollständig.")
        if {id(eintrag[0]) for eintrag in lernstatus} != {
            id(lernabschnitt) for lernabschnitt in modul.lernabschnitte
        }:
            raise ValueError("Der Lernstatus enthält fremde Lernabschnitte.")
        if not all(isinstance(erledigt, bool) for _, erledigt in lernstatus):
            raise TypeError("Der Lernstatus muss Wahrheitswerte enthalten.")

    @property
    def studiengang(self) -> Studiengang:
        """Gibt den verwalteten Studiengang zurück."""

        return self.__studiengang

    @property
    def ausgewaehltes_modul(self) -> Modul | None:
        """Gibt das aktuell ausgewählte Modul zurück."""

        return self.__ausgewaehltes_modul
