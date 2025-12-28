"""
Tipels GTK GUI - Main Window

Hauptfenster mit Navigation und Content-Area
"""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from tipels import __version__
from tipels.gui.gtk.dialogs.info_dialog import InfoDialog
from tipels.gui.gtk.views.welcome_view import WelcomeView


class MainWindow(Gtk.ApplicationWindow):
    """
    Hauptfenster der Tipels-Anwendung.

    Verwendet Gtk.Stack + Gtk.StackSidebar für Navigation zwischen Views.
    """

    def __init__(self, application, logger):
        """
        Initialisiert MainWindow.

        Args:
            application: TipelsApplication-Instanz
            logger: TipelsLogger-Instanz
        """
        super().__init__(application=application)
        self.logger = logger
        self.app = application

        # Window-Eigenschaften
        self.set_title("Tipels")
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Views
        self.views = {}

        # UI aufbauen
        self._build_ui()

        self.logger.debug("MainWindow erstellt")

    def _build_ui(self):
        """Baut die UI-Komponenten auf."""
        # HeaderBar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title("Tipels")
        headerbar.set_subtitle("Drucker & Scanner Setup")
        self.set_titlebar(headerbar)

        # Menu Button
        menu_button = Gtk.MenuButton()
        menu_button.set_image(
            Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        )
        headerbar.pack_end(menu_button)

        # Menu
        menu = Gio.Menu()
        menu.append("Einstellungen", "app.preferences")
        menu.append("Über Tipels", "app.about")
        menu.append("Beenden", "app.quit")
        menu_button.set_menu_model(menu)

        # Hauptcontainer (Horizontal Box)
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Stack für Content
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)

        # StackSidebar für Navigation
        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(self.stack)
        sidebar.set_size_request(200, -1)

        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        # Views erstellen
        self._create_views()

        # Layout zusammenbauen
        main_box.pack_start(sidebar, False, False, 0)
        main_box.pack_start(separator, False, False, 0)
        main_box.pack_start(self.stack, True, True, 0)

        self.add(main_box)
        self.show_all()

    def _create_views(self):
        """Erstellt alle Views und fügt sie zum Stack hinzu."""
        # Welcome View
        welcome = WelcomeView(self.logger)
        self.stack.add_titled(welcome, "welcome", "Übersicht")
        self.views["welcome"] = welcome

        # Placeholder für weitere Views
        # TODO: Scan View hinzufügen
        scan_placeholder = Gtk.Label(label="Scan-Ansicht\n(wird implementiert)")
        self.stack.add_titled(scan_placeholder, "scan", "Hardware scannen")
        self.views["scan"] = scan_placeholder

        # TODO: Install View hinzufügen
        install_placeholder = Gtk.Label(label="Installations-Assistent\n(wird implementiert)")
        self.stack.add_titled(install_placeholder, "install", "Gerät installieren")
        self.views["install"] = install_placeholder

        # TODO: Device List View hinzufügen
        devices_placeholder = Gtk.Label(label="Geräteverwaltung\n(wird implementiert)")
        self.stack.add_titled(devices_placeholder, "devices", "Installierte Geräte")
        self.views["devices"] = devices_placeholder

        # TODO: Settings View hinzufügen
        settings_placeholder = Gtk.Label(label="Einstellungen\n(wird implementiert)")
        self.stack.add_titled(settings_placeholder, "settings", "Einstellungen")
        self.views["settings"] = settings_placeholder

    def switch_to_view(self, view_name: str):
        """
        Wechselt zu einer bestimmten View.

        Args:
            view_name: Name der View (welcome, scan, install, devices, settings)
        """
        if view_name in self.views:
            self.stack.set_visible_child_name(view_name)
            self.logger.debug(f"Zu View '{view_name}' gewechselt")

            # Status aktualisieren wenn Welcome-View
            if view_name == "welcome" and hasattr(self.views[view_name], "update_status"):
                self.views[view_name].update_status()
        else:
            self.logger.warning(f"View '{view_name}' nicht gefunden")

    def show_about_dialog(self):
        """Zeigt den Über-Dialog an."""
        dialog = InfoDialog(parent=self)
        dialog.run()
        dialog.destroy()

    def show_settings_view(self):
        """Wechselt zur Einstellungs-View."""
        self.switch_to_view("settings")
