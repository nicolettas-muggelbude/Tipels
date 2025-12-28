"""
Tipels GTK GUI - Main Entry Point

Startet die GTK3-GUI
"""

import sys
from tipels.gui.gtk.application import TipelsApplication


def main():
    """
    Haupteinstiegspunkt für die Tipels GTK GUI.

    Returns:
        Exit-Code
    """
    app = TipelsApplication()
    return app.run_gui()


if __name__ == "__main__":
    sys.exit(main())
