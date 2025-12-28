"""
Tipels GTK GUI - Application

Gtk.Application Subclass für Tipels
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, Gio

from tipels import __version__
from tipels.core.logger import TipelsLogger
from tipels.core.config import TipelsConfig


class TipelsApplication(Gtk.Application):
    """
    Hauptanwendung für Tipels GTK GUI.

    Verwaltet den Application-Lifecycle und erstellt das Hauptfenster.
    """

    def __init__(self):
        """Initialisiert die Tipels-Anwendung."""
        super().__init__(
            application_id='org.tipels.Tipels',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Logger und Config
        self.logger = TipelsLogger("tipels.gui")
        self.config = TipelsConfig()

        # Hauptfenster (wird in do_activate erstellt)
        self.main_window = None

        self.logger.info(f"Tipels GUI {__version__} gestartet")

    def do_startup(self):
        """
        Called once when the application starts.
        Setup global actions, menus, etc.
        """
        Gtk.Application.do_startup(self)

        # Dark Mode aktivieren
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        # Custom CSS laden
        self._load_css()

        # Actions
        self._create_actions()

        # Keyboard Shortcuts
        self._setup_accelerators()

        self.logger.debug("Application startup complete (Dark Mode + Akzentfarbe aktiv)")

    def do_activate(self):
        """
        Called when the application is activated (started or re-focused).
        Creates and shows the main window.
        """
        # Wenn Fenster schon existiert, in den Vordergrund bringen
        if self.main_window:
            self.main_window.present()
            return

        # Hauptfenster erstellen
        from tipels.gui.gtk.views.main_window import MainWindow
        self.main_window = MainWindow(application=self, logger=self.logger)
        self.main_window.present()

        self.logger.debug("Main window created and presented")

    def do_shutdown(self):
        """Called when the application shuts down."""
        self.logger.info("Tipels GUI wird beendet")
        Gtk.Application.do_shutdown(self)

    def _create_actions(self):
        """Erstellt Application-Actions."""
        # Quit Action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

        # About Action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        # Preferences Action
        prefs_action = Gio.SimpleAction.new("preferences", None)
        prefs_action.connect("activate", self._on_preferences)
        self.add_action(prefs_action)

    def _load_css(self):
        """Lädt die Custom CSS-Datei für Akzentfarbe."""
        try:
            from pathlib import Path

            css_path = Path(__file__).parent / "resources" / "css" / "tipels.css"

            if css_path.exists():
                css_provider = Gtk.CssProvider()
                css_provider.load_from_path(str(css_path))

                screen = Gdk.Screen.get_default()
                style_context = Gtk.StyleContext()
                style_context.add_provider_for_screen(
                    screen,
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

                self.logger.info(f"Akzentfarbe CSS geladen: {css_path}")
            else:
                self.logger.warning(f"CSS-Datei nicht gefunden: {css_path}")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der CSS-Datei: {e}")

    def _setup_accelerators(self):
        """Richtet Keyboard-Shortcuts ein."""
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])
        self.set_accels_for_action("app.about", ["F1"])

    def _on_quit(self, action, param):
        """Quit-Action Handler."""
        self.quit()

    def _on_about(self, action, param):
        """About-Action Handler."""
        if self.main_window:
            self.main_window.show_about_dialog()

    def _on_preferences(self, action, param):
        """Preferences-Action Handler."""
        if self.main_window:
            self.main_window.show_settings_view()

    def run_gui(self):
        """
        Startet die GTK-Anwendung.

        Returns:
            Exit-Code
        """
        return self.run(None)
