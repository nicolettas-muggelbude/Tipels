"""
Tipels - Main Entry Point

Startet entweder GUI oder CLI basierend auf Argumenten
"""

import sys


def main():
    """Haupteinstiegspunkt für Tipels"""
    # TODO: Implementierung
    # - Prüfen ob GUI oder CLI gewünscht
    # - Bei keinen Argumenten: GUI starten
    # - Bei Argumenten: CLI starten

    if len(sys.argv) > 1:
        # CLI-Modus
        from tipels.cli.commands import cli

        cli()
    else:
        # GUI-Modus
        try:
            from tipels.gui.gtk.main_window import main as gui_main

            gui_main()
        except ImportError as e:
            print(f"Fehler beim Laden der GUI: {e}")
            print("Bitte installiere die GTK-Abhängigkeiten:")
            print("  sudo apt install python3-gi gir1.2-gtk-3.0")
            sys.exit(1)


if __name__ == "__main__":
    main()
