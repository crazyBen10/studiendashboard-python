"""Grafische Benutzeroberfläche des Studiendashboards mit Tkinter.

Die Datei ist ausschließlich für Darstellung und Benutzerinteraktion
verantwortlich. Fachliche Berechnungen werden an die Modellklassen delegiert;
das dauerhafte Speichern übernimmt die ``Datenverwaltung``.
"""

# ``date`` liefert das heutige Datum für Fortschrittsberechnungen. 
# Mit ``datetime`` werden Datumsangaben aus den Eingabefeldern eingelesen.
from datetime import date, datetime
from typing import TYPE_CHECKING

# Tkinter stellt alle Fenster und Steuerelemente bereit. ``messagebox`` wird
# separat importiert, damit Validierungsfehler als Dialog angezeigt werden.
import tkinter as tk
from tkinter import messagebox

# Die Oberfläche arbeitet mit der Speicherklasse und den fachlichen
# Modellobjekten, statt Berechnungs- oder Persistenzlogik selbst nachzubauen.
from modelle import *

if TYPE_CHECKING:
    from dashboard_controller import DashboardController


class DashboardGUI:
    """Stellt die Studiendaten in einer grafischen Benutzeroberfläche dar."""

    # Zentrale Farbpalette des Dashboards. Dadurch verwenden alle Widgets
    # dieselben Farben und das Erscheinungsbild kann an einer Stelle geändert
    # werden, ohne jeden einzelnen Erzeugungsblock suchen zu müssen.
    HINTERGRUND = "#07182B"
    KARTE = "#07182B"
    KARTE_HELL = "#0B263E"
    RAHMEN = "#185071"
    TEXT = "#FFFFFF"
    TEXT_SEKUNDAER = "#AFC7E8"
    BLAU = "#168CFF"
    GRUEN = "#00DF8F"
    ORANGE = "#FF9818"
    GRAU = "#7892AE"
    ROT = "#D62424"

    def __init__(
        self,
        controller: "DashboardController"
    ) -> None:
        """Erstellt das Hauptfenster und verbindet es mit dem Controller."""

        # Die übergebenen Objekte bleiben die gemeinsame Datenquelle aller
        # Ansichten. Es werden bewusst keine Kopien angelegt, damit Änderungen
        # aus dem Formular sofort im gesamten Dashboard sichtbar werden.
        self.__controller = controller

        # Das Tk-Hauptfenster erhält Titel, Start- und Mindestgröße sowie die Grundfarbe. 
        # Über das WM-Protokoll wird auch beim Schließen über das Fenstersymbol zuerst die Speicherroutine ausgeführt.
        self.__hauptfenster = tk.Tk()
        self.__hauptfenster.title("Studiendashboard")
        self.__hauptfenster.geometry("1920x1080")
        self.__hauptfenster.minsize(1100, 650)
        self.__hauptfenster.configure(bg=self.HINTERGRUND)
        self.__hauptfenster.protocol("WM_DELETE_WINDOW", self.__beenden)

        # Die linke Spalte behält ihre Breite. Der rechte Bereich wächst mit.
        self.__hauptfenster.grid_rowconfigure(0, weight=1)
        self.__hauptfenster.grid_columnconfigure(0, weight=0)
        self.__hauptfenster.grid_columnconfigure(1, weight=1)

        # Nach der Fenstereinrichtung wird die komplette erste Ansicht erzeugt.
        self.dashboard_anzeigen()

    def starten(self) -> None:
        """Startet die Ereignisschleife der Benutzeroberfläche."""

        # Ab hier wartet Tkinter auf Maus-, Tastatur- und Fensterereignisse.
        # Der Aufruf blockiert, bis das Hauptfenster geschlossen wird.
        self.__hauptfenster.mainloop()

    def dashboard_anzeigen(self) -> None:
        """Baut die Dashboard-Ansicht mit den aktuellen Daten neu auf."""

        # Alle bisherigen Widgets werden entfernt. 
        # Der vollständige Neuaufbau ist hier übersichtlicher als zahlreiche Einzelwerte zu 
        # synchronisieren und garantiert nach einer Bearbeitung einen konsistenten Bildschirm.
        for element in self.__hauptfenster.winfo_children():
            element.destroy()

        # Zuerst entsteht die Navigation links, danach der Inhaltsbereich rechts.
        self.__erstelle_modulbereich()
        self.__erstelle_hauptbereich()

    def __beenden(self) -> None:
        """Meldet das Beenden an den Controller und schließt das Fenster."""

        self.__controller.beenden()
        self.__hauptfenster.destroy()



    def __erstelle_modulbereich(self) -> None:
        """Erstellt den linken Bereich für die scrollbare Modulliste."""

        # Der äußere Rahmen bildet eine feste Navigationsspalte. Die eigentliche
        # Modulliste darf darin vertikal wachsen, verändert aber nicht die Breite.
        modulbereich = tk.Frame(
            self.__hauptfenster,
            width=316,
            bg=self.HINTERGRUND,
            highlightthickness=0
        )

        # ´´sticky='nsew´´ lässt die Spalte die gesamte Fensterhöhe ausfüllen.
        modulbereich.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=0,
            pady=0
        )

        # Verhindert, dass der Inhalt die festgelegte Breite verändert.
        modulbereich.grid_propagate(False)

        # Die Linie trennt die Navigation vom übrigen Dashboard.
        tk.Frame(modulbereich, width=2, bg=self.RAHMEN).place(
            relx=1.0,
            rely=0,
            relheight=1.0,
            anchor="ne"
        )

        # Die Überschrift bleibt oberhalb des scrollbaren Listeninhalts stehen.
        ueberschrift = tk.Label(
            modulbereich,
            text="Meine Module",
            font=("Segoe UI", 22, "bold"),
            bg=self.HINTERGRUND,
            fg=self.TEXT
        )

        ueberschrift.pack(
            anchor="w",
            padx=32,
            pady=(34, 24)
        )

        # Die Legende wird mit ``side='bottom'`` zuerst am unteren Rand
        # reserviert, sodass sie beim Scrollen der Module immer sichtbar bleibt.
        self.__erstelle_statuslegende(modulbereich)

        # Dieser Zwischenrahmen nimmt den gesamten verbleibenden Raum zwischen
        # Überschrift und Legende ein und enthält Canvas plus Scrollbar.
        listenbereich = tk.Frame(
            modulbereich,
            bg=self.HINTERGRUND
        )
        listenbereich.pack(
            fill="both",
            expand=True,
            padx=(31, 8),
            pady=(0, 5)
        )

        # Tkinter-Frames sind selbst nicht scrollbar. Deshalb liegt die
        # tatsächliche Modulliste als Fenster in einem scrollbaren Canvas.
        canvas = tk.Canvas(
            listenbereich,
            bg=self.HINTERGRUND,
            highlightthickness=0
        )

        # Die Scrollbar steuert die vertikale Ansicht des Canvas. Umgekehrt wird
        # weiter unten der Schieber über ``yscrollcommand`` synchronisiert.
        scrollbar = tk.Scrollbar(
            listenbereich,
            orient="vertical",
            command=canvas.yview,
            width=20,
            bg=self.BLAU,
            activebackground="#59AFFF",
            troughcolor=self.KARTE_HELL,
            relief="flat",
            borderwidth=0
        )

        # In diesem inneren Frame werden Semesterüberschriften und Modulzeilen
        # ganz normal untereinander angeordnet.
        modulliste = tk.Frame(
            canvas,
            bg=self.HINTERGRUND
        )

        # "create_window" bettet den Frame als Canvas-Objekt ein. Die Kennung
        # wird benötigt, um seine Breite bei einer Größenänderung anzupassen.
        modullisten_fenster = canvas.create_window(
            (0, 0),
            window=modulliste,
            anchor="nw"
        )

        def scrollbereich_aktualisieren(event) -> None:
            """Passt den scrollbaren Bereich an den Inhalt an."""

            # Nach jeder Größenänderung des inneren Frames umfasst die Scroll-
            # Region wieder die Begrenzung aller enthaltenen Elemente.
            canvas.configure(scrollregion=canvas.bbox("all"))


        def listenbreite_aktualisieren(event) -> None:
            """Passt die Modulliste an die Breite des Canvas an."""

            # Ohne diese Anpassung behielte das eingebettete Fenster seine
            # angeforderte Breite und würde beim Vergrößern nicht mitwachsen.
            canvas.itemconfigure(
                modullisten_fenster,
                width=event.width -20
            )

        def mit_mausrad_scrollen(event) -> str:
            """Scrollt die Modulliste mit dem Mausrad."""

            richtung = -1 if event.delta > 0 else 1
            canvas.yview_scroll(richtung * 1, "units") # Geschwindigkeit steuern
            return "break"


        def mausrad_binden(widget: tk.Widget) -> None:
            """Aktiviert das Mausrad für ein Widget und dessen Unterelemente."""

            widget.bind("<MouseWheel>", mit_mausrad_scrollen)

            for unterelement in widget.winfo_children():
                mausrad_binden(unterelement)


        # Die beiden Configure-Ereignisse halten Inhaltsgröße und sichtbare
        # Breite automatisch synchron, auch wenn sich das Fenster verändert.
        modulliste.bind(
            "<Configure>",
            scrollbereich_aktualisieren
        )

        canvas.bind(
            "<Configure>",
            listenbreite_aktualisieren
        )

        # Bewegungen des Canvas aktualisieren zusätzlich die Position des
        # Scrollbar-Schiebers.
        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        # Canvas und Scrollbar werden nebeneinander in den Listenbereich gelegt.
        # nur der Canvas erhält den zusätzlich verfügbaren Platz.
        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Das Kennzeichen ermöglicht nach der Schleife eine verständliche
        # Leerzustandsmeldung, wenn noch kein Semester Module enthält.
        module_vorhanden = False

        # Die Modellhierarchie Studiengang -> Semester -> Modul wird direkt in dieselbe visuelle Gruppierung übersetzt. 
        # Leere Semester erscheinen nicht, weil eine Überschrift ohne Einträge keinen Mehrwert hätte.
        for semester in self.__controller.studiengang.semester:
            if len(semester.module) == 0:
                continue

            module_vorhanden = True

            # Jedes belegte Semester beginnt mit einer beschrifteten Trennzeile.
            semester_ueberschrift = tk.Label(
                modulliste,
                text=semester.bezeichnung,
                font=("Segoe UI", 11, "bold"),
                bg=self.HINTERGRUND,
                fg="#B9CBFF"
            )
            semester_ueberschrift.pack(
                anchor="w",
                pady=(12, 7)
            )

            tk.Frame(
                modulliste,
                height=2,
                bg=self.RAHMEN
            ).pack(fill="x")

            # Innerhalb des Semesters erhält jedes Modul eine eigene anklickbare Zeile. 
            # Statusfarbe und -symbol stammen aus zentralen Hilfsmethoden.
            for modul in semester.module:
                ausgewaehlt = (
                    modul is self.__controller.ausgewaehltes_modul
                )
                hintergrund = "#0D2A44" if ausgewaehlt else self.HINTERGRUND
                status = modul.status
                statusfarbe = self.__statusfarbe(status)

                # Der Zeilenrahmen bündelt Statussymbol und Modulschaltfläche.
                modulzeile = tk.Frame(modulliste, bg=hintergrund)
                modulzeile.pack(fill="x")

                # Der Kreis kommuniziert den fachlich abgeleiteten Modulstatus zusätzlich zur Farbe mit einem Symbol.
                self.__erstelle_symbolkreis(
                    modulzeile,
                    statusfarbe,
                    self.__statussymbol(status),
                    30,
                    10
                ).pack(side="left", padx=(2, 13), pady=9)

                # Für jeden Button wird eine eigene Callback-Funktion erzeugt.
                # Der Standardparameter hält das Modul der aktuellen
                # Schleifenrunde fest. Ohne ihn würden später alle Funktionen auf
                # das zuletzt durchlaufene Modul verweisen.
                def modul_anklicken(
                    ausgewaehltes_modul: Modul = modul
                ) -> None:
                    """Öffnet das Modul, das zu diesem Button gehört."""

                    self.__modul_auswaehlen(ausgewaehltes_modul) # siehe Zeile 425

                modul_button = tk.Button(
                    modulzeile,
                    text=modul.name,
                    command=modul_anklicken,
                    font=("Segoe UI", 10),
                    bg=hintergrund,
                    fg=self.TEXT_SEKUNDAER,
                    activebackground="#0D2A44",
                    activeforeground=self.TEXT,
                    anchor="w",
                    justify="left",
                    wraplength=190,
                    relief="flat",
                    borderwidth=0,
                    padx=0,
                    pady=8
                )
                modul_button.pack(
                    side="left",
                    fill="both",
                    expand=True
                )

                # Eine dünne Linie grenzt aufeinanderfolgende Module ab.
                tk.Frame(
                    modulliste,
                    height=2,
                    bg=self.RAHMEN
                ).pack(fill="x")

        # Bei vollständig leerem Studiengang ersetzt ein Hinweis die Modulliste.
        if not module_vorhanden:
            hinweis = tk.Label(
                modulliste,
                text="Noch keine Module vorhanden.",
                font=("Segoe UI", 11),
                bg=self.HINTERGRUND,
                fg=self.TEXT_SEKUNDAER
            )
            hinweis.pack(
                anchor="w",
                pady=20
            )
        # Das Mausrad funktioniert über der gesamten linken Modulspalte.
        mausrad_binden(modulbereich)

    def __erstelle_statuslegende(self, elternelement: tk.Widget) -> None:
        """Erstellt die Statuslegende unterhalb der Modulliste."""

        # Der Rahmen wird am unteren Rand der Navigationsspalte verankert und
        # bleibt dadurch unabhängig von der Länge der Modulliste sichtbar.
        legende = tk.Frame(elternelement, bg=self.HINTERGRUND)
        legende.pack(side="bottom", fill="x", padx=32, pady=(5, 14))

        # Die feste Reihenfolge führt von erledigten über aktive und bewertete
        # bis zu noch nicht begonnenen Modulen.
        eintraege = (
            (ModulStatus.BESTANDEN, "Bestanden"),
            (ModulStatus.IN_BEARBEITUNG, "In Bearbeitung"),
            (ModulStatus.ERGEBNIS_AUSSTEHEND, "Ergebnis ausstehend"),
            (ModulStatus.NICHT_BESTANDEN, "Nicht bestanden"),
            (ModulStatus.NICHT_BEGONNEN, "Nicht begonnen")
        )

        # Jede Legendenzeile verwendet dieselben Farb- und Symbolzuordnungen wie
        # die echte Modulliste, damit beide Darstellungen konsistent bleiben.
        for status, text in eintraege:
            zeile = tk.Frame(legende, bg=self.HINTERGRUND)
            zeile.pack(anchor="w", pady=2)
            self.__erstelle_symbolkreis(
                zeile,
                self.__statusfarbe(status),
                self.__statussymbol(status),
                20,
                10
            ).pack(side="left", padx=(0, 10)) # Beschriftung rechts neben dem Symbolkreis in der Legende
            tk.Label(
                zeile,
                text=text,
                font=("Segoe UI", 8),
                bg=self.HINTERGRUND,
                fg=self.TEXT_SEKUNDAER
            ).pack(side="left")

    def __modul_auswaehlen(self, modul: Modul) -> None:
        """Speichert die Auswahl und öffnet das Bearbeitungsfenster."""

        # Die Referenz dient später der farblichen Hervorhebung
        # Anschließend wird für genau dieses Modul der modale Bearbeitungsdialog geöffnet.
        self.__controller.modul_auswaehlen(modul)
        self.__oeffne_bearbeitungsfenster(modul)

#------------------------------------------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------------------------------------------

    def __erstelle_hauptbereich(self) -> None:
        """Erstellt Kopfbereich, Fortschrittskarte und Statuskarten."""

        # Der rechte Hauptbereich wächst mit dem Fenster und erhält rundum etwas
        # Abstand zur Navigationsspalte und zu den Fensterrändern.
        hauptbereich = tk.Frame(
            self.__hauptfenster,
            bg=self.HINTERGRUND
        )
        hauptbereich.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(21, 28),
            pady=(24, 31)
        )
        # Zeile 0 reserviert Platz für den Kopf; Zeile 1 nimmt den restlichen Raum ein. 
        # Die einzige Spalte darf horizontal mitwachsen.
        hauptbereich.grid_rowconfigure(0, minsize=87)
        hauptbereich.grid_rowconfigure(1, weight=1)
        hauptbereich.grid_columnconfigure(0, weight=1)

        # Der Kopf wird getrennt erzeugt, da er über beiden Inhaltskarten liegt.
        self.__erstelle_kopfbereich(hauptbereich)


        # Der Inhaltsrahmen teilt den verfügbaren Platz im Verhältnis 3:1:
        # links der große Fortschritt, rechts die zwei kompakten Statuskarten.
        inhalt = tk.Frame(
            hauptbereich,
            bg=self.HINTERGRUND
        )
        inhalt.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(10, 0)
        )
        inhalt.grid_rowconfigure(0, weight=1)
        inhalt.grid_columnconfigure(0, weight=3)
        inhalt.grid_columnconfigure(1, weight=1)

        # Beide Unterbereiche füllen ihre jeweiligen Grid-Spalten vollständig.
        self.__erstelle_fortschrittskarte(inhalt)
        self.__erstelle_statuskarten(inhalt)

    def __erstelle_kopfbereich(self, elternelement: tk.Widget) -> None:
        """Erstellt Titel, Datum und ECTS-Fortschritt im Kopfbereich."""

        # Der Kopf nutzt zwei Spalten: Der Studiengang steht links, während die
        # kompakten Fortschrittsinformationen rechtsbündig angeordnet werden.
        kopfbereich = tk.Frame(
            elternelement,
            bg=self.HINTERGRUND
        )
        kopfbereich.grid(
            row=0,
            column=0,
            sticky="ew"
        )
        kopfbereich.grid_columnconfigure(0, weight=1)

        # Ein eigener Rahmen hält den langen Studiengangnamen unabhängig von den Kennzahlen auf der rechten Seite.
        titelbereich = tk.Frame(
            kopfbereich,
            bg=self.HINTERGRUND
        )
        titelbereich.grid(
            row=0,
            column=0,
            sticky="w",
            padx=0
        )

        # Der Name wird direkt aus dem Modell gelesen, damit die Anzeige nicht
        # durch einen separat gepflegten Oberflächentext abweichen kann.
        tk.Label(
            titelbereich,
            text=self.__controller.studiengang.name,
            font=("Segoe UI", 32, "bold"),
            bg=self.HINTERGRUND,
            fg=self.TEXT
        ).pack(anchor="w")

        # Datum, ECTS, Balken und Prozentwert bilden den rechten Kennzahlenblock.
        fortschrittsbereich = tk.Frame(
            kopfbereich,
            bg=self.HINTERGRUND
        )
        fortschrittsbereich.grid(
            row=0,
            column=1,
            sticky="e",
            padx=0
        )

        # Beide Werte sind fachlich abgeleitet. Die GUI ruft deshalb die Methoden
        # des Studiengangs auf, statt bestandene Module selbst auszuwerten.
        erreichte_ects = (
            self.__controller.studiengang.berechne_erreichte_ects()
        )
        studienfortschritt = (
            self.__controller.studiengang.berechne_studienfortschritt()
        )

        # Das tagesaktuelle Datum macht deutlich, auf welchen Stand sich die angezeigten Fortschrittswerte beziehen.
        tk.Label(
            fortschrittsbereich,
            text=date.today().strftime("Stand: %d.%m.%Y"),
            font=("Segoe UI", 11),
            bg=self.HINTERGRUND,
            fg=self.TEXT_SEKUNDAER
        ).pack(anchor="e", pady=(0, 20))

        # Der absolute ECTS-Wert ergänzt die relative Darstellung im Balken.
        tk.Label(
            fortschrittsbereich,
            text=(
                f"{erreichte_ects} von {self.__controller.studiengang.ziel_ects} "
                "ECTS-Punkten"
            ),
            font=("Segoe UI", 11),
            bg=self.HINTERGRUND,
            fg=self.TEXT
        ).pack(anchor="w")

        # Der wiederverwendbare Balken visualisiert denselben Prozentwert.
        self.__erstelle_fortschrittsbalken(
            fortschrittsbereich,
            studienfortschritt,
            270
        ).pack(anchor="w", pady=(5, 0))

        # Der exakte Wert wird mit deutschem Dezimalkomma unter dem Balken gezeigt.
        tk.Label(
            fortschrittsbereich,
            text=f"{studienfortschritt:.2f} %".replace(".", ","),
            font=("Segoe UI", 10),
            bg=self.HINTERGRUND,
            fg=self.TEXT_SEKUNDAER
        ).pack(anchor="e")

    def __erstelle_fortschrittsbalken(
        self,
        elternelement: tk.Widget,
        fortschritt: float,
        breite: int
    ) -> tk.Canvas:
        """Erstellt einen einfachen horizontalen Fortschrittsbalken."""

        # Die Canvas-Grundfläche übernimmt zugleich die Farbe des noch nicht erreichten Balkenanteils.
        balken = tk.Canvas(
            elternelement,
            width=breite,
            height=14,
            bg=self.RAHMEN,
            highlightthickness=0
        )

        # Das Begrenzen schützt die Zeichnung vor negativen Werten oder einer Füllung über die vorgegebene Breite hinaus.
        sichtbarer_fortschritt = max(0.0, min(100.0, fortschritt))
        fuellbreite = breite * sichtbarer_fortschritt / 100

        # Das grüne Rechteck beginnt links und endet an der berechneten Position.
        balken.create_rectangle(
            0,
            0,
            fuellbreite,
            14,
            fill=self.GRUEN,
            outline=""
        )

        # Die aufrufende Methode entscheidet selbst, wo der fertige Canvas liegt.
        return balken

#---------------------------------------------------------------------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def __erstelle_fortschrittskarte(self, elternelement: tk.Widget) -> None:
        """Erstellt die große Karte mit Studien- und Zeitfortschritt."""

        # Die Karte belegt die linke Inhaltsspalte. 
        # Rahmenfarbe und ein Pixel Hervorhebung sorgen für die Abgrenzung zum gleichfarbigen Hintergrund.
        karte = tk.Frame(
            elternelement,
            bg=self.KARTE,
            highlightthickness=1,
            highlightbackground=self.RAHMEN
        )
        karte.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7)
        )
        # Nur die Canvas-Zeile wächst; die Überschrift behält ihre benötigte Höhe.
        karte.grid_rowconfigure(1, weight=1)
        karte.grid_columnconfigure(0, weight=1)

        # Die Kartenüberschrift liegt als eigenes Element oberhalb der Grafik.
        tk.Label(
            karte,
            text="Studienfortschritt",
            font=("Segoe UI", 19, "bold"),
            bg=self.KARTE,
            fg=self.TEXT
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=29,
            pady=(18, 0)
        )

        # Der Canvas füllt den restlichen Kartenraum. 
        # Seine endgültigen Maße sind erst nach dem Layout bekannt, daher erfolgt das Zeichnen ereignisbasiert.
        kreis = tk.Canvas(
            karte,
            bg=self.KARTE,
            highlightthickness=0
        )
        kreis.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=10
        )

        # Die drei Kennzahlen stammen aus dem fachlichen Modell: ECTS-basierter Planungsfortschritt, verstrichene Studienzeit und Notendurchschnitt.
        planungsfortschritt = (
            self.__controller.studiengang.berechne_planungsfortschritt()
        )
        zeitfortschritt = (
            self.__controller.studiengang.berechne_zeitfortschritt(
                date.today()
            )
        )
        notendurchschnitt = (
            self.__controller.studiengang.berechne_notendurchschnitt()
        )

        # Ohne bewertete Prüfungen wird ein Platzhalter angezeigt. 
        # Andernfalls signalisiert Grün oder Orange, ob die hinterlegte Zielnote erreicht ist.
        if notendurchschnitt is None:
            notentext = "--"
            notenfarbe = self.GRAU
        else:
            notentext = f"{notendurchschnitt:.1f}".replace(".", ",")
            if self.__controller.studiengang.zielnote_erreicht():
                notenfarbe = self.GRUEN
            else:
                notenfarbe = self.ORANGE

        def fortschrittskreise_zeichnen(event) -> None:
            """Zeichnet beide Kreise passend zur aktuellen Kartengröße."""

            # Vor jedem Neuzeichnen werden alte Canvas-Elemente entfernt. 
            # Das verhindert übereinanderliegende Grafiken nach Größenänderungen.
            kreis.delete("all")

            # Mittelpunkt und Radius werden aus der aktuellen Canvas-Größe bestimmt.
            # Kleine Verschiebungen gleichen die seitliche Beschriftung und die optische vertikale Ausrichtung innerhalb der Karte aus.
            mitte_x = event.width / 2
            mitte_y = event.height / 2
            radius = max(90, min(event.width, event.height) / 2 - 28)
            innerer_radius = radius - 56


            # Der innere Ring stellt den bereits verstrichenen Anteil der geplanten gesamten Studienzeit dar.
            # Seine dunklere Kontur bleibt als noch offener Anteil sichtbar.
            self.__zeichne_kreis(
                kreis,
                mitte_x,
                mitte_y,
                radius,
                zeitfortschritt,
                self.BLAU,
                50,
                "#1559B5"
            )
            # Der äußere, breite Ring zeigt den fachlichen Planungsfortschritt.
            self.__zeichne_kreis(
                kreis,
                mitte_x,
                mitte_y,
                innerer_radius,
                planungsfortschritt,
                self.GRUEN,
                50,
                "#0E5D48"
            )

            # In der Kreismitte steht der Notendurchschnitt als wichtigste
            # Kennzahl; ein zweiter Text erklärt seine Bedeutung.
            kreis.create_text(
                mitte_x,
                mitte_y - 15,
                text=f"Ø {notentext}",
                fill=notenfarbe,
                font=("Segoe UI", 48, "bold")
            )
            kreis.create_text(
                mitte_x,
                mitte_y + 37,
                text="Notendurchschnitt",
                fill=self.TEXT_SEKUNDAER,
                font=("Segoe UI", 14)
            )
            # Die kleine Beschriftung ordnet dem äußeren Ring seinen konkreten
            # Prozentwert zu und sitzt relativ zum Radius.
            kreis.create_text(
                mitte_x + radius * 0.8,
                mitte_y - radius * 0.95,
                text=(f"{zeitfortschritt:.1f} %\nverstrichene\nStudienzeit").replace(".", ","),
                fill=self.BLAU,
                font=("Segoe UI", 12, "bold"),
                justify="left",
                anchor="nw"
            )

        # ``<Configure>`` wird beim ersten Anzeigen und bei jeder Änderung der
        # Canvas-Größe ausgelöst; so bleibt die Grafik responsiv zentriert.
        kreis.bind("<Configure>", fortschrittskreise_zeichnen)

    def __zeichne_kreis(
        self,
        canvas: tk.Canvas,
        mitte_x: float,
        mitte_y: float,
        radius: float,
        fortschritt: float,
        farbe: str,
        linienbreite: int,
        hintergrundfarbe: str
    ) -> None:
        """Zeichnet den Hintergrund und den Fortschrittsbogen eines Kreises."""

        # Aus Mittelpunkt und Radius entsteht die rechteckige Begrenzung, die
        # Tkinter sowohl für das Oval als auch für den Kreisbogen erwartet.
        koordinaten = (
            mitte_x - radius,
            mitte_y - radius,
            mitte_x + radius,
            mitte_y + radius
        )

        # Zuerst wird ein vollständiger, dunkler Ring als offener Anteil gezeichnet.
        canvas.create_oval(
            *koordinaten,
            outline=hintergrundfarbe,
            width=linienbreite
        )

        # Auch Kreiswerte werden auf 0 bis 100 Prozent begrenzt. 3,6 Grad pro
        # Prozent wandeln den Wert in den Winkel eines Vollkreises um. 
        # Das negative Vorzeichen lässt den Bogen von oben im Uhrzeigersinn laufen.
        sichtbarer_fortschritt = max(0.0, min(100.0, fortschritt))
        canvas.create_arc(
            *koordinaten,
            start=90,
            extent=-3.6 * sichtbarer_fortschritt,
            style="arc",
            outline=farbe,
            width=linienbreite
        )

    def __erstelle_statuskarten(self, elternelement: tk.Widget) -> None:
        """Erstellt die Karten für das aktuelle Modul und den Zeitplan."""

        # Die rechte Inhaltsspalte wird vertikal in zwei Karten geteilt. Das
        # Gewichtsverhältnis 57:43 gibt der ausführlicheren Modulkarte mehr Raum.
        seitenbereich = tk.Frame(
            elternelement,
            bg=self.HINTERGRUND
        )
        seitenbereich.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0)
        )
        seitenbereich.grid_rowconfigure(0, weight=57)
        seitenbereich.grid_rowconfigure(1, weight=43)
        seitenbereich.grid_columnconfigure(0, weight=1)

        # Die beiden spezialisierten Methoden füllen jeweils eine Grid-Zeile.
        self.__erstelle_modulkarte(seitenbereich)
        self.__erstelle_zeitplankarte(seitenbereich)

    def __erstelle_modulkarte(self, elternelement: tk.Widget) -> None:
        """Erstellt eine Karte mit dem derzeit relevanten Modul."""

        # Die obere rechte Karte erhält denselben visuellen Rahmen wie die große
        # Fortschrittskarte und lässt nach unten Platz zur Zeitplankarte.
        karte = tk.Frame(
            elternelement,
            bg=self.KARTE,
            highlightthickness=1,
            highlightbackground=self.RAHMEN
        )
        karte.grid(
            row=0,
            column=0,
            sticky="nsew",
            pady=(0, 7)
        )

        # Im Kartenkopf stehen Überschrift und – sofern ein Modul existiert –
        # die Schaltfläche zum Öffnen des Bearbeitungsdialogs nebeneinander.
        kopf = tk.Frame(karte, bg=self.KARTE)
        kopf.pack(fill="x", padx=17, pady=(14, 7))

        tk.Label(
            kopf,
            text="Aktuelles Modul",
            font=("Segoe UI", 18, "bold"),
            bg=self.KARTE,
            fg=self.TEXT
        ).pack(side="left")

        # Die Hilfsmethode entscheidet anhand einer festgelegten Priorität,
        # welches Modul für die Person momentan am relevantesten ist.
        modul = self.__controller.aktuelles_modul()

        # Ohne Modul darf kein Bearbeiten-Button entstehen, weil kein Zielobjekt übergeben werden könnte.
        if modul is not None:
            def modul_bearbeiten() -> None:
                """Öffnet das aktuell angezeigte Modul zur Bearbeitung."""

                self.__modul_auswaehlen(modul)

            tk.Button(
                kopf,
                text="Bearbeiten",
                command=modul_bearbeiten,
                font=("Segoe UI", 10, "bold"),
                bg=self.KARTE,
                fg=self.BLAU,
                activebackground=self.KARTE_HELL,
                activeforeground=self.TEXT,
                relief="flat",
                borderwidth=0,
                cursor="hand2"
            ).pack(side="right")

        # Eine Trennlinie separiert den Kopf vom dynamischen Karteninhalt.
        tk.Frame(karte, height=2, bg=self.RAHMEN).pack(
            fill="x",
            padx=17
        )

        # Ein Studiengang ohne Module erhält einen klaren Leerzustand. 
        # Das frühe ``return`` verhindert anschließend jeden Zugriff auf ``None``.
        if modul is None:
            tk.Label(
                karte,
                text="Es sind noch keine Module vorhanden.",
                font=("Segoe UI", 11),
                bg=self.KARTE,
                fg=self.TEXT_SEKUNDAER,
                wraplength=330,
                justify="left"
            ).pack(anchor="w", padx=22, pady=20)
            return

        # Der Lernfortschritt wird aus den Zuständen aller Lernabschnitte
        # abgeleitet und sowohl grafisch als auch als Text ausgegeben.
        erledigte_abschnitte = sum(
            1
            for lernabschnitt in modul.lernabschnitte
            if lernabschnitt.ist_erledigt()
        )

        # Der Modulname steht oberhalb der eigentlichen Fortschrittsanzeige.
        tk.Label(
            karte,
            text=modul.name,
            font=("Segoe UI", 14, "bold"),
            bg=self.KARTE,
            fg=self.TEXT,
            wraplength= 500,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(12, 4))

        # Kreisdiagramm und absolute Abschnittszahl werden in einer gemeinsamen
        # Zeile angeordnet, damit beide Darstellungen direkt vergleichbar sind.
        fortschrittsbereich = tk.Frame(karte, bg=self.KARTE)
        fortschrittsbereich.pack(fill="x", padx=22, pady=(3, 8))

        # Der Canvas hat hier eine feste Größe, da die kompakte Karte nicht genug
        # Platz für ein frei skalierendes Kreisdiagramm bietet.
        kreis = tk.Canvas(
            fortschrittsbereich,
            width=125,
            height=120,
            bg=self.KARTE,
            highlightthickness=0
        )
        kreis.pack(side="left")
        self.__zeichne_modulfortschritt(kreis, modul)

        # Rechts neben dem Kreis wird derselbe Stand als „erledigt von gesamt“ formuliert.
        # das verbessert die Verständlichkeit ohne Farberkennung.
        tk.Label(
            fortschrittsbereich,
            text=(
                f"{erledigte_abschnitte} von {len(modul.lernabschnitte)} "
                "Lernabschnitten"
            ),
            font=("Segoe UI", 10),
            bg=self.KARTE,
            fg=self.TEXT,
            wraplength=135,
            justify="left"
        ).pack(side="left", padx=(12, 0))

        # Die zweite Trennlinie grenzt die zeitliche Einschätzung optisch ab.
        tk.Frame(karte, height=2, bg=self.RAHMEN).pack(
            fill="x",
            padx=17,
            pady=(8, 8)
        )

        # Die Restzeit berücksichtigt auch Sonderzustände wie „nicht gestartet“
        # oder „Ergebnis ausstehend“ und kommt aus der folgenden Hilfsmethode.
        tk.Label(
            karte,
            text=f"Geplante Restzeit:  {self.__restzeit_text(modul)}",
            font=("Segoe UI", 10),
            bg=self.KARTE,
            fg=self.TEXT_SEKUNDAER
        ).pack(anchor="w", padx=22, pady=(0, 12))

    def __zeichne_modulfortschritt(
        self,
        canvas: tk.Canvas,
        modul: Modul
    ) -> None:
        """Zeichnet die sechs Lernabschnitte als Kreisstücke."""

        # Aus Gesamtzahl und erledigten Abschnitten wird der Wert in der Mitte berechnet. 
        # Die Nullprüfung schützt vor einer Division durch null, falls
        # künftig einmal ein Modul ohne Lernabschnitte modelliert wird.
        anzahl = len(modul.lernabschnitte)
        erledigt = sum(
            1 for lernabschnitt in modul.lernabschnitte
            if lernabschnitt.ist_erledigt()
        )
        if anzahl == 0:
            prozent = 0.0
        else:
            prozent = erledigt / anzahl * 100

        # Der Vollkreis wird gleichmäßig auf alle Abschnitte verteilt. Zwischen
        # zwei Segmenten bleiben fünf Grad frei, damit sie unterscheidbar sind.
        winkel = 360 / max(1, anzahl)
        for nummer in range(anzahl):
            # Erledigte Segmente erscheinen blau, offene in einer dunkleren Farbe.
            farbe = self.BLAU if nummer < erledigt else "#244D6B"
            canvas.create_arc(
                19,
                14,
                111,
                106,
                start=90 - nummer * winkel,
                extent=-(winkel - 5),
                style="arc",
                outline= farbe,
                width=18
            )

        # Die Prozentzahl in der Mitte fasst die einzelnen Segmente zusammen.
        canvas.create_text(
            65,
            60,
            text=f"{prozent:.0f} %",
            fill=self.TEXT,
            font=("Segoe UI", 15, "bold")
        )

    @staticmethod
    def __restzeit_text(modul: Modul) -> str:
        """Berechnet eine kurze Restzeitangabe für das aktuelle Modul."""

        # Abgeschlossene oder noch nicht planbare Statusfälle erhalten direkt
        # eine verbale Beschreibung; dafür wäre eine Wochenangabe irreführend.
        if modul.status == ModulStatus.BESTANDEN:
            return "Abgeschlossen"
        if modul.status == ModulStatus.NICHT_BESTANDEN:
            return "Nicht bestanden"
        if modul.status == ModulStatus.ERGEBNIS_AUSSTEHEND:
            return "Ergebnis ausstehend"
        if modul.startdatum is None:
            return "Noch nicht gestartet"

        # Nur ein gestartetes, laufendes Modul besitzt eine berechenbare Restzeit.
        # Die fachliche Differenzberechnung verbleibt im Modulmodell.
        resttage = modul.berechne_restzeit_in_tagen(date.today())
        if resttage is None:
            return "Noch nicht gestartet"

        # Negative Resttage werden verständlich als Überschreitung ausgegeben.
        if resttage < 0:
            return f"{abs(resttage)} Tage über Plan"

        # Positive Tage werden auf volle Wochen aufgerundet. So werden auch
        # einzelne verbleibende Tage nicht fälschlich als null Wochen angezeigt.
        wochen = max(1, (resttage + 6) // 7)
        einheit = "Woche" if wochen == 1 else "Wochen"
        return f"{wochen} {einheit}"

    def __erstelle_zeitplankarte(self, elternelement: tk.Widget) -> None:
        """Erstellt die Karte mit dem Zeitplanstatus des Studiums."""

        # Die untere rechte Karte schließt mit etwas Abstand an die Modulkarte an.
        karte = tk.Frame(
            elternelement,
            bg=self.KARTE,
            highlightthickness=1,
            highlightbackground=self.RAHMEN
        )
        karte.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(7, 0)
        )

        # Das Modell vergleicht fachlich Lern- und Zeitfortschritt. Die GUI ordnet
        # dem Ergebnis lediglich einen gut lesbaren Erklärungstext zu.
        zeitplanstatus = self.__controller.studiengang.ermittle_zeitplan_status(
            date.today()
        )
        statusmeldungen = {
            ZeitplanStatus.VORSPRUNG: "Du liegst vor deinem geplanten Zeitplan.",
            ZeitplanStatus.IM_ZEITPLAN: "Du liegst mit deinem Studium im geplanten Zeitrahmen.",
            ZeitplanStatus.IM_VERZUG: "Dein Fortschritt liegt hinter dem Zeitplan."
        }

        # Die Überschrift benennt die zentrale Datumsinformation der Karte.
        tk.Label(
            karte,
            text="Geplantes Studienende",
            font=("Segoe UI", 16, "bold"),
            bg=self.KARTE,
            fg=self.TEXT
        ).pack(anchor="w", padx=22, pady=(18, 10))

        # Kalendersymbol und formatiertes Enddatum stehen gemeinsam in einer Zeile.
        datumszeile = tk.Frame(karte, bg=self.KARTE)
        datumszeile.pack(fill="x", padx=22)
        tk.Label(
            datumszeile,
            text="▦",
            font=("Segoe UI Symbol", 22),
            bg=self.KARTE,
            fg="#B9CBFF"
        ).pack(side="left", padx=(0, 14))
        tk.Label(
            datumszeile,
            text=self.__formatiere_datum(
                self.__controller.studiengang.geplantes_enddatum
            ),
            font=("Segoe UI", 21, "bold"),
            bg=self.KARTE,
            fg=self.TEXT
        ).pack(side="left")

        # Die Linie trennt das Zieldatum von seiner aktuellen Bewertung.
        tk.Frame(karte, height=2, bg=self.RAHMEN).pack(
            fill="x",
            padx=17,
            pady=(8, 10)
        )

        # Die Statuszeile besteht aus farbigem Symbol und einem Textblock. 
        # Bei Verzug wird ein Warnzeichen, sonst ein bestätigender Haken verwendet.
        statuszeile = tk.Frame(karte, bg=self.KARTE)
        statuszeile.pack(fill="x", padx=22)
        self.__erstelle_symbolkreis(
            statuszeile,
            self.__statusfarbe(zeitplanstatus),
            "✓" if zeitplanstatus != ZeitplanStatus.IM_VERZUG else "!",
            42,
            18
        ).pack(side="left", padx=(0, 14))

        # Ein eigener Rahmen stapelt Statusbezeichnung und Erläuterung rechts vom
        # Symbol und lässt den Text bei breiteren Fenstern mitwachsen.
        statusinhalt = tk.Frame(statuszeile, bg=self.KARTE)
        statusinhalt.pack(side="left", fill="x", expand=True)

        # Die Enum-Bezeichnung übernimmt die jeweilige Statusfarbe.
        tk.Label(
            statusinhalt,
            text=zeitplanstatus.value,
            font=("Segoe UI", 14, "bold"),
            bg=self.KARTE,
            fg=self.__statusfarbe(zeitplanstatus)
        ).pack(anchor="w")

        # Darunter erklärt ein vollständiger Satz die Bedeutung des Status.
        tk.Label(
            statusinhalt,
            text=statusmeldungen[zeitplanstatus],
            font=("Segoe UI", 10),
            bg=self.KARTE,
            fg=self.TEXT_SEKUNDAER,
            wraplength=230,
            justify="left"
        ).pack(anchor="w", pady=(3, 10))

    def __erstelle_symbolkreis(
        self,
        elternelement: tk.Widget,
        farbe: str,
        symbol: str,
        groesse: int,
        schriftgroesse: int
    ) -> tk.Canvas:
        """Erstellt einen farbigen Kreis mit einem Symbol in der Mitte."""

        # Die Hintergrundfarbe wird vom Elternelement übernommen. 
        # Dadurch lässt sich die Hilfsmethode sowohl in der Navigation als auch in Karten nutzen.
        kreis = tk.Canvas(
            elternelement,
            width=groesse,
            height=groesse,
            bg=elternelement.cget("bg"),
            highlightthickness=0
        )
        # Das Oval füllt beinahe den ganzen Canvas
        # Je ein Pixel Rand verhindert ein Abschneiden an der Zeichenfläche.
        kreis.create_oval(
            1,
            1,
            groesse - 1,
            groesse - 1,
            fill=farbe,
            outline=""
        )
        # Symbol und Kreis teilen denselben Mittelpunkt.
        kreis.create_text(
            groesse / 2,
            groesse / 2,
            text=symbol,
            fill=self.TEXT,
            font=("Segoe UI", schriftgroesse, "bold")
        )
        # Position und Layout übernimmt jeweils die aufrufende Methode.
        return kreis

    def __statusfarbe(
        self,
        status: ModulStatus | ZeitplanStatus
    ) -> str:
        """Gibt die zur Statusanzeige passende Farbe zurück."""

        # Positive Modul- und Zeitplanstatus werden einheitlich grün angezeigt.
        if status in (
            ModulStatus.BESTANDEN,
            ZeitplanStatus.VORSPRUNG,
            ZeitplanStatus.IM_ZEITPLAN
        ):
            return self.GRUEN

        # Orange kennzeichnet Zustände, die Aufmerksamkeit oder Warten erfordern.
        if status in (
            ModulStatus.ERGEBNIS_AUSSTEHEND,
            ZeitplanStatus.IM_VERZUG
        ):
            return self.ORANGE

        # Rot kennzeichnet ein nicht bestandenes Modul.
        if status == ModulStatus.NICHT_BESTANDEN:
            return self.ROT

        # Blau hebt den normalen aktiven Arbeitszustand hervor.
        if status == ModulStatus.IN_BEARBEITUNG:
            return self.BLAU

        # Übrig bleibt insbesondere „nicht begonnen“, das neutral grau erscheint.
        return self.GRAU

    @staticmethod
    def __statussymbol(status: ModulStatus) -> str:
        """Zeigt keinen Text innerhalb der farbigen Statuskreise an."""

        return ""

    @staticmethod
    def __formatiere_datum(datum: date) -> str:
        """Formatiert ein Datum für die Anzeige als Tag.Monat.Jahr."""

        # Intern bleiben Datumswerte echte ``date``-Objekte; nur die Anzeige
        # verwendet die im deutschen Sprachraum übliche Schreibweise.
        return datum.strftime("%d.%m.%Y")

    @staticmethod
    def __datum_einlesen(text: str, feldname: str) -> date:
        """Wandelt eine Eingabe im Format Tag.Monat.Jahr in ein Datum um."""

        # ``strptime`` prüft gleichzeitig Format und kalendarische Gültigkeit.
        try:
            return datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError as fehler:
            # Die technische Parsermeldung wird durch eine feldbezogene und für
            # die Benutzerin oder den Benutzer verständliche Meldung ersetzt.
            raise ValueError(
                f"{feldname} muss im Format TT.MM.JJJJ eingegeben werden."
            ) from fehler

    @classmethod
    def __optionales_datum_einlesen(
        cls,
        text: str,
        feldname: str
    ) -> date | None:
        """Gibt bei leerer Eingabe ``None``, sonst ein geprüftes Datum zurück."""

        bereinigter_text = text.strip()
        if not bereinigter_text:
            return None
        return cls.__datum_einlesen(bereinigter_text, feldname)

    def __oeffne_bearbeitungsfenster(self, modul: Modul) -> None:
        """Öffnet ein Formular zum Bearbeiten eines Moduls."""

        # Das Formular liegt in einem eigenen Toplevel-Fenster (sagt nur das Hauptfenster im Hintergrund ist). 
        # ``transient`` ordnet es dem Hauptfenster zu; 
        # ``grab_set`` macht es modal, sodass bis zum Schließen keine widersprüchliche zweite Bearbeitung möglich ist.
        fenster = tk.Toplevel(self.__hauptfenster)
        fenster.title(f"Modul bearbeiten - {modul.name}")
        fenster.geometry("650x760")
        fenster.minsize(600, 680)
        fenster.configure(bg=self.HINTERGRUND)
        fenster.transient(self.__hauptfenster)
        fenster.grab_set()

        # Ein gepolsterter Inhaltsrahmen schafft einheitliche Außenabstände für
        # alle folgenden Formularbereiche.
        inhalt = tk.Frame(
            fenster,
            bg=self.HINTERGRUND
        )
        inhalt.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=22
        )

        # Modulname und kompakte Metadaten bilden den unveränderlichen Dialogkopf.
        tk.Label(
            inhalt,
            text=modul.name,
            font=("Segoe UI", 19, "bold"),
            bg=self.HINTERGRUND,
            fg=self.TEXT,
            wraplength=570,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            inhalt,
            text=(
                f"{modul.kurscode}   |   {modul.ects} ECTS   |   {modul.status.value}"
            ),
            font=("Segoe UI", 10),
            bg=self.HINTERGRUND,
            fg=self.TEXT_SEKUNDAER
        ).pack(anchor="w", pady=(5, 16))

        # Der erste Formularblock verwaltet das Startdatum. Derselbe Hilfsrahmen
        # wird später auch für Lernabschnitte und Prüfungsdaten verwendet.
        startbereich = self.__erstelle_formularbereich(
            inhalt,
            "Modulstart"
        )

        # Tkinter-Variablen verbinden Widgets mit auslesbaren Python-Werten.
        # Bei einem bereits gestarteten Modul wird das vorhandene Datum vorbelegt,
        # sonst das heutige Datum als sinnvoller Vorschlag.
        starten_var = tk.BooleanVar(value=False)
        startdatum_var = tk.StringVar(
            value=(
                self.__formatiere_datum(modul.startdatum)
                if modul.startdatum is not None
                else self.__formatiere_datum(date.today())
            )
        )

        # Noch nicht gestartete Module benötigen eine ausdrückliche Bestätigung.
        # Dadurch startet allein das Öffnen und Speichern des Dialogs kein Modul.
        if modul.startdatum is None:
            tk.Checkbutton(
                startbereich,
                text="Dieses Modul starten",
                variable=starten_var,
                font=("Segoe UI", 10),
                bg=self.KARTE,
                fg=self.TEXT,
                activebackground=self.KARTE,
                activeforeground=self.TEXT,
                selectcolor=self.KARTE_HELL
            ).grid(row=0, column=0, sticky="w", padx=14, pady=10)

            startdatum_entry = self.__erstelle_eingabefeld(
                startbereich,
                "Startdatum (TT.MM.JJJJ)",
                startdatum_var,
                1
            )
        else:
            # Bei laufenden Modulen kann das gespeicherte Startdatum direkt in
            # der ersten Zeile geprüft und bei Bedarf korrigiert werden.
            startdatum_entry = self.__erstelle_eingabefeld(
                startbereich,
                "Startdatum (TT.MM.JJJJ)",
                startdatum_var,
                0
            )

        # Der zweite Block bildet die fachlichen Lernabschnitte als Checkboxen ab.
        lernbereich = self.__erstelle_formularbereich(
            inhalt,
            "Lernabschnitte"
        )

        # Neben jedem Modellobjekt wird seine zugehörige BooleanVar gespeichert.
        # Diese Paare erlauben beim Speichern den Vergleich von alt und neu.
        lernabschnitt_variablen = []

        # Anzahl und Bezeichnungen kommen vollständig aus dem Modulmodell; der
        # Dialog funktioniert daher auch bei einer später veränderten Abschnittszahl.
        for zeile, lernabschnitt in enumerate(modul.lernabschnitte):
            erledigt_var = tk.BooleanVar(
                value=lernabschnitt.ist_erledigt()
            )
            lernabschnitt_variablen.append(
                (lernabschnitt, erledigt_var)
            )

            # Der bestehende Erledigt-Status bestimmt die Anfangsauswahl.
            tk.Checkbutton(
                lernbereich,
                text=lernabschnitt.bezeichnung,
                variable=erledigt_var,
                font=("Segoe UI", 10),
                bg=self.KARTE,
                fg=self.TEXT,
                activebackground=self.KARTE,
                activeforeground=self.TEXT,
                selectcolor=self.KARTE_HELL
            ).grid(
                row=zeile,
                column=0,
                sticky="w",
                padx=14,
                pady=3
            )

        # Der dritte Block erfasst die optionalen Daten der Prüfungsleistung.
        # Leere Felder stehen fachlich für „noch nicht abgegeben/bewertet“.
        pruefungsbereich = self.__erstelle_formularbereich(
            inhalt,
            "Prüfungsleistung"
        )

        # Vorhandene Werte werden in Anzeigezeichenfolgen umgewandelt. 
        # Dabei wird die Note mit deutschem Dezimalkomma und ein fehlender Wert leer gezeigt.
        pruefungsleistung = modul.pruefungsleistung

        # Ist bereits ein Abgabedatum vorhanden, wird es für das Eingabefeld
        # formatiert. Andernfalls beginnt das Feld leer.
        if pruefungsleistung.abgabedatum is not None:
            angezeigtes_abgabedatum = self.__formatiere_datum(
                pruefungsleistung.abgabedatum
            )
        else:
            angezeigtes_abgabedatum = ""

        abgabedatum_var = tk.StringVar(
            value=angezeigtes_abgabedatum
        )

        # Eine vorhandene Note wird zuerst in Text umgewandelt. Für die deutsche
        # Schreibweise ersetzt das Komma anschließend den Dezimalpunkt.
        if pruefungsleistung.note is not None:
            angezeigte_note = str(pruefungsleistung.note).replace(".", ",")
        else:
            angezeigte_note = ""

        note_var = tk.StringVar(
            value=angezeigte_note
        )

        # Das Ergebnisdatum wird wie das Abgabedatum formatiert. Solange noch
        # kein Ergebnis vorliegt, bleibt auch dieses Eingabefeld leer.
        if pruefungsleistung.ergebnisdatum is not None:
            angezeigtes_ergebnisdatum = self.__formatiere_datum(
                pruefungsleistung.ergebnisdatum
            )
        else:
            angezeigtes_ergebnisdatum = ""

        ergebnisdatum_var = tk.StringVar(
            value=angezeigtes_ergebnisdatum
        )

        # Alle drei Eingabezeilen verwenden denselben Helfer und unterscheiden
        # sich nur in Beschriftung, gebundener Variable und Grid-Zeile.
        abgabe_entry = self.__erstelle_eingabefeld(
            pruefungsbereich,
            "Abgabedatum (TT.MM.JJJJ)",
            abgabedatum_var,
            0
        )
        note_entry = self.__erstelle_eingabefeld(
            pruefungsbereich,
            "Note (1,0 bis 5,0)",
            note_var,
            1
        )
        ergebnis_entry = self.__erstelle_eingabefeld(
            pruefungsbereich,
            "Ergebnisdatum (TT.MM.JJJJ)",
            ergebnisdatum_var,
            2
        )

        # Am Dialogende stehen die Aktionen rechtsbündig in einem eigenen Rahmen.
        schaltflaechen = tk.Frame(
            inhalt,
            bg=self.HINTERGRUND
        )
        schaltflaechen.pack(fill="x", pady=(16, 0))

        # Nur ein bereits gestartetes Modul kann zurückgesetzt werden. Der Button
        # steht getrennt von Speichern und Abbrechen auf der linken Seite, weil
        # die Aktion den bisherigen Fortschritt vollständig verwirft.
        if modul.startdatum is not None:
            tk.Button(
                schaltflaechen,
                text="Modul zurücksetzen",
                command=lambda: self.__modul_zuruecksetzen(modul, fenster),
                font=("Segoe UI", 10, "bold"),
                bg="#C13B3B",
                fg=self.TEXT,
                activebackground="#A92F2F",
                activeforeground=self.TEXT,
                relief="flat",
                padx=16,
                pady=8
            ).pack(side="left")

        # „Abbrechen“ verwirft die unverarbeiteten Tkinter-Variablen, indem 
        # das Dialogfenster geschlossen wird ohne zu speichern.
        tk.Button(
            schaltflaechen,
            text="Abbrechen",
            command=fenster.destroy,
            font=("Segoe UI", 10),
            bg=self.RAHMEN,
            fg=self.TEXT,
            activebackground=self.KARTE_HELL,
            activeforeground=self.TEXT,
            relief="flat",
            padx=16,
            pady=8
        ).pack(side="right", padx=(8, 0))

        # Die Speicherschaltfläche übergibt alle Formularvariablen und speichert alle Änderungen ab
        tk.Button(
            schaltflaechen,
            text="Änderungen speichern",
            command=lambda: self.__formular_absenden(
                modul,
                starten_var,
                startdatum_var,
                lernabschnitt_variablen,
                abgabedatum_var,
                note_var,
                ergebnisdatum_var,
                fenster
            ),
            font=("Segoe UI", 10, "bold"),
            bg=self.GRUEN,
            fg="#03261A",
            activebackground="#00BE79",
            activeforeground="#03261A",
            relief="flat",
            padx=16,
            pady=8
        ).pack(side="right")

        # Der Tastaturfokus beginnt im Startdatum, dem ersten editierbaren Feld.
        startdatum_entry.focus_set()

    def __modul_zuruecksetzen(
        self,
        modul: Modul,
        fenster: tk.Toplevel
    ) -> None:
        """Setzt ein Modul nach ausdrücklicher Bestätigung vollständig zurück."""

        # Die Sicherheitsabfrage nennt alle betroffenen Daten, damit die Person
        # die Folgen der nicht einzeln rückgängig zu machenden Aktion kennt.
        bestaetigt = messagebox.askyesno(
            "Modul zurücksetzen",
            (
                f'Möchtest du „{modul.name}“ wirklich zurücksetzen?\n\n'
                "Startdatum, Lernfortschritt und Prüfungsdaten werden gelöscht."
            ),
            icon="warning",
            parent=fenster
        )
        if not bestaetigt:
            return

        # Der Controller setzt das Modell zurück, speichert es und aktualisiert
        # anschließend die Anzeige.
        self.__controller.modul_zuruecksetzen(modul)
        fenster.destroy()

    def __erstelle_formularbereich(
        self,
        elternelement: tk.Widget,
        titel: str
    ) -> tk.Frame:
        """Erstellt einen optisch abgegrenzten Bereich im Formular."""

        # Das LabelFrame zeichnet Titel und Begrenzung in einem Widget. 
        # Einheitliche Farben und Innenabstände halten alle Formulargruppen optisch konsistent.
        bereich = tk.LabelFrame(
            elternelement,
            text=titel,
            font=("Segoe UI", 11, "bold"),
            bg=self.KARTE,
            fg=self.TEXT,
            highlightthickness=1,
            highlightbackground=self.RAHMEN,
            bd=0,
            padx=4,
            pady=4
        )
        # Die Gruppe nutzt die gesamte Dialogbreite. Ihre einzige Grid-Spalte
        # wächst, damit die später eingefügten Eingabezeilen ebenfalls mitwachsen.
        bereich.pack(
            fill="x",
            pady=5
        )
        bereich.grid_columnconfigure(0, weight=1)

        # Die aufrufende Methode füllt den vorbereiteten Bereich mit Widgets.
        return bereich

    def __erstelle_eingabefeld(
        self,
        elternelement: tk.Widget,
        beschriftung: str,
        variable: tk.StringVar,
        zeile: int
    ) -> tk.Entry:
        """Erstellt eine Beschriftung mit dem dazugehörigen Eingabefeld."""

        # Pro Feld wird ein eigener Zeilenrahmen angelegt. Darin bleibt die
        # Beschriftung links, während das Eingabefeld den freien Raum erhält.
        zeilenbereich = tk.Frame(
            elternelement,
            bg=self.KARTE
        )
        zeilenbereich.grid(
            row=zeile,
            column=0,
            sticky="ew",
            padx=14,
            pady=5
        )
        zeilenbereich.grid_columnconfigure(1, weight=1)

        # Die Beschriftung erklärt Inhalt und gegebenenfalls das Eingabeformat.
        tk.Label(
            zeilenbereich,
            text=beschriftung,
            font=("Segoe UI", 10),
            bg=self.KARTE,
            fg=self.TEXT_SEKUNDAER
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        # ``textvariable`` synchronisiert den sichtbaren Inhalt automatisch mit
        # der übergebenen StringVar, die später zentral ausgelesen wird.
        eingabefeld = tk.Entry(
            zeilenbereich,
            textvariable=variable,
            font=("Segoe UI", 10),
            bg="#EAF2FF",
            fg="#07182B",
            disabledbackground=self.RAHMEN,
            disabledforeground=self.TEXT_SEKUNDAER,
            relief="flat"
        )
        eingabefeld.grid(row=0, column=1, sticky="ew", ipady=4)

        # Die Referenz wird zurückgegeben, damit beispielsweise der Tastaturfokus
        # gezielt auf dieses Feld gesetzt werden kann.
        return eingabefeld

    def __formular_absenden(
        self,
        modul: Modul,
        starten_var: tk.BooleanVar,
        startdatum_var: tk.StringVar,
        lernabschnitt_variablen: list,
        abgabedatum_var: tk.StringVar,
        note_var: tk.StringVar,
        ergebnisdatum_var: tk.StringVar,
        fenster: tk.Toplevel
    ) -> None:
        """Liest Formulareingaben und übergibt sie an den Controller."""

        # Alle erwartbaren Eingabefehler werden gemeinsam abgefangen und im
        # geöffneten Dialog angezeigt; das Fenster bleibt dann zur Korrektur offen.
        try:
            if modul.startdatum is None:
                if starten_var.get():
                    neues_startdatum = self.__datum_einlesen(
                        startdatum_var.get().strip(),
                        "Das Startdatum"
                    )
                else:
                    neues_startdatum = None
            else:
                neues_startdatum = self.__datum_einlesen(
                    startdatum_var.get().strip(),
                    "Das Startdatum"
                )

            # Optionale Datumsfelder werden nur bei vorhandener Eingabe geparst.
            abgabedatum = self.__optionales_datum_einlesen(
                abgabedatum_var.get(),
                "Das Abgabedatum"
            )
            note_text = note_var.get().strip()
            note = (
                float(note_text.replace(",", "."))
                if note_text
                else None
            )
            ergebnisdatum = self.__optionales_datum_einlesen(
                ergebnisdatum_var.get(),
                "Das Ergebnisdatum"
            )
            lernstatus = [
                (lernabschnitt, variable.get())
                for lernabschnitt, variable in lernabschnitt_variablen
            ]

            # Fachliche Validierung, Zustandsänderung, Speicherung und
            # Aktualisierung liegen vollständig beim Controller.
            self.__controller.modulaenderungen_speichern(
                modul,
                neues_startdatum,
                lernstatus,
                abgabedatum,
                note,
                ergebnisdatum
            )
            fenster.destroy()

        except (TypeError, ValueError) as fehler:
            # Sowohl Konvertierungsfehler als auch fachliche Validierungsfehler
            # erscheinen im Kontext des Dialogs statt die Anwendung zu beenden.
            messagebox.showerror(
                "Eingabe prüfen",
                str(fehler),
                parent=fenster
            )
