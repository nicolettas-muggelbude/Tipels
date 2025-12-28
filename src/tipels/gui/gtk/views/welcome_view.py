"""
Tipels GTK GUI - Welcome View

Startseite mit Schnellzugriff und System-Status
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from tipels.utils.cups_helper import CupsHelper
from tipels.utils.sane_helper import SaneHelper


class WelcomeView(Gtk.Box):
    """
    Welcome/Startseite für Tipels.

    Zeigt:
    - Willkommenstext
    - Schnellzugriff-Buttons (Scannen, Installieren)
    - System-Status (CUPS, SANE, Geräteanzahl)
    """

    def __init__(self, logger):
        """
        Initialisiert WelcomeView.

        Args:
            logger: TipelsLogger-Instanz
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_margin_top(40)
        self.set_margin_bottom(40)
        self.set_margin_start(40)
        self.set_margin_end(40)

        self.logger = logger

        # UI aufbauen
        self._build_ui()

        self.logger.debug("WelcomeView erstellt")

    def _build_ui(self):
        """Baut die UI-Komponenten auf."""
        # Header
        header = Gtk.Label()
        header.set_markup("<span size='xx-large' weight='bold'>Willkommen bei Tipels</span>")
        header.set_halign(Gtk.Align.CENTER)
        self.pack_start(header, False, False, 0)

        # Subtitle
        subtitle = Gtk.Label(label="Drucker & Scanner einfach einrichten")
        subtitle.set_halign(Gtk.Align.CENTER)
        subtitle.get_style_context().add_class("dim-label")
        self.pack_start(subtitle, False, False, 0)

        # Spacer
        self.pack_start(Gtk.Box(), False, False, 10)

        # Action Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_halign(Gtk.Align.CENTER)

        # Scan Button
        scan_button = Gtk.Button()
        scan_button.get_style_context().add_class("welcome-action-button")
        scan_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scan_icon = Gtk.Image.new_from_icon_name("edit-find-symbolic", Gtk.IconSize.DIALOG)
        scan_label = Gtk.Label(label="Hardware scannen")
        scan_vbox.pack_start(scan_icon, False, False, 0)
        scan_vbox.pack_start(scan_label, False, False, 0)
        scan_button.add(scan_vbox)
        scan_button.connect("clicked", self._on_scan_clicked)
        button_box.pack_start(scan_button, False, False, 0)

        # Install Button
        install_button = Gtk.Button()
        install_button.get_style_context().add_class("welcome-action-button")
        install_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        install_icon = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.DIALOG)
        install_label = Gtk.Label(label="Gerät installieren")
        install_vbox.pack_start(install_icon, False, False, 0)
        install_vbox.pack_start(install_label, False, False, 0)
        install_button.add(install_vbox)
        install_button.connect("clicked", self._on_install_clicked)
        button_box.pack_start(install_button, False, False, 0)

        self.pack_start(button_box, False, False, 0)

        # Spacer
        self.pack_start(Gtk.Box(), True, True, 0)

        # Status Card
        status_frame = Gtk.Frame()
        status_frame.set_label("System-Status")
        status_frame.set_halign(Gtk.Align.CENTER)
        status_frame.set_size_request(400, -1)

        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_box.set_margin_top(10)
        status_box.set_margin_bottom(10)
        status_box.set_margin_start(20)
        status_box.set_margin_end(20)

        # CUPS Status
        self.cups_status_label = Gtk.Label()
        self.cups_status_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.cups_status_label, False, False, 0)

        # SANE Status
        self.sane_status_label = Gtk.Label()
        self.sane_status_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.sane_status_label, False, False, 0)

        # Drucker-Anzahl
        self.printer_count_label = Gtk.Label()
        self.printer_count_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.printer_count_label, False, False, 0)

        # Scanner-Anzahl
        self.scanner_count_label = Gtk.Label()
        self.scanner_count_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.scanner_count_label, False, False, 0)

        status_frame.add(status_box)
        self.pack_start(status_frame, False, False, 0)

        # Aktualisieren-Button
        refresh_button = Gtk.Button(label="Status aktualisieren")
        refresh_button.set_halign(Gtk.Align.CENTER)
        refresh_button.connect("clicked", lambda btn: self.update_status())
        self.pack_start(refresh_button, False, False, 0)

        # Gestaffelte Status-Aktualisierung
        self._check_availability()  # Sofort: CUPS/SANE Verfügbarkeit (schnell)
        GLib.timeout_add_seconds(3, self._update_printers)  # Nach 3s: Drucker
        GLib.timeout_add_seconds(6, self._update_scanners)  # Nach 6s: Scanner

    def _check_availability(self):
        """Prüft CUPS/SANE Verfügbarkeit (schnell, ohne Listen-Abfrage)."""
        try:
            # CUPS Verfügbarkeit
            cups = CupsHelper(self.logger)
            if cups.is_cups_available():
                self.cups_status_label.set_markup("✓ <b>CUPS</b> läuft")
            else:
                self.cups_status_label.set_markup("✗ <b>CUPS</b> nicht verfügbar")

            # SANE Verfügbarkeit
            sane = SaneHelper(self.logger)
            if sane.is_sane_available():
                self.sane_status_label.set_markup("✓ <b>SANE</b> verfügbar")
            else:
                self.sane_status_label.set_markup("✗ <b>SANE</b> nicht verfügbar")

            # Platzhalter für Listen (werden später aktualisiert)
            self.printer_count_label.set_markup("⏳ <b>Drucker</b> werden geladen...")
            self.scanner_count_label.set_markup("⏳ <b>Scanner</b> werden geladen...")
        except Exception as e:
            self.logger.error(f"Fehler bei Verfügbarkeits-Check: {e}")

    def _update_printers(self):
        """Aktualisiert Drucker-Liste (wird nach 3s aufgerufen)."""
        try:
            cups = CupsHelper(self.logger)
            if cups.is_cups_available():
                printers = cups.list_printers()
                count = len(printers)
                if count == 0:
                    self.printer_count_label.set_markup("⚠ <b>0 Drucker</b> installiert")
                else:
                    self.printer_count_label.set_markup(f"✓ <b>{count} Drucker</b> installiert")
            else:
                self.printer_count_label.set_markup("⚠ <b>0 Drucker</b> installiert")
        except Exception as e:
            self.logger.error(f"Fehler beim Drucker-Update: {e}")
            self.printer_count_label.set_markup("✗ <b>Fehler</b> beim Laden")
        return False  # Timer nicht wiederholen

    def _update_scanners(self):
        """Aktualisiert Scanner-Liste (wird nach 6s aufgerufen)."""
        try:
            sane = SaneHelper(self.logger)
            if sane.is_sane_available():
                scanners = sane.list_scanners()
                count = len(scanners)
                if count == 0:
                    self.scanner_count_label.set_markup("⚠ <b>0 Scanner</b> installiert")
                else:
                    self.scanner_count_label.set_markup(f"✓ <b>{count} Scanner</b> installiert")
            else:
                self.scanner_count_label.set_markup("⚠ <b>0 Scanner</b> installiert")
        except Exception as e:
            self.logger.error(f"Fehler beim Scanner-Update: {e}")
            self.scanner_count_label.set_markup("✗ <b>Fehler</b> beim Laden")
        return False  # Timer nicht wiederholen

    def _show_placeholder_status(self):
        """Zeigt Platzhalter-Status an (ohne Hardware-Abfrage)."""
        self.cups_status_label.set_markup("ℹ <b>CUPS</b> - Status nicht geladen")
        self.sane_status_label.set_markup("ℹ <b>SANE</b> - Status nicht geladen")
        self.printer_count_label.set_markup("ℹ <b>Drucker</b> - Nicht abgefragt")
        self.scanner_count_label.set_markup("ℹ <b>Scanner</b> - Nicht abgefragt")

    def update_status(self):
        """Manuelles Status-Update (wird vom Button aufgerufen)."""
        self._check_availability()
        self._update_printers()
        self._update_scanners()

    def _on_scan_clicked(self, button):
        """Handler für Scan-Button."""
        self.logger.debug("Scan-Button geklickt")
        # Signal an MainWindow senden
        self.get_toplevel().switch_to_view("scan")

    def _on_install_clicked(self, button):
        """Handler für Install-Button."""
        self.logger.debug("Install-Button geklickt")
        # Signal an MainWindow senden
        self.get_toplevel().switch_to_view("install")
