"""
Tipels - Einfache Einrichtung von Druckern und Scannern unter Linux

Copyright (C) 2025 Tipels Contributors
Licensed under GPL-3.0-or-later
"""

# Version
__version__ = "0.1.0"

# Projekt-Metadaten
__author__ = "Tipels Contributors"
__copyright__ = "© 2025 Tipels Contributors"
__license__ = "GPL-3.0-or-later"
__website__ = "https://github.com/nicolettas-muggelbude/Tipels"
__website_label__ = "GitHub Repository"

# Branding
__accent_color__ = "#3F51B5"  # Indigo-Blau (aus Logo)

# Beschreibung
__description__ = "Drucker & Scanner einfach einrichten unter Linux"
__long_description__ = (
    "Tipels vereinfacht die Installation und Verwaltung von "
    "Druckern und Scannern unter Linux durch automatische "
    "Hardware-Erkennung und Treiber-Installation."
)

# Team
__authors__ = ["Tipels Contributors"]
__documenters__ = ["Tipels Team"]

from tipels.core.config import TipelsConfig
from tipels.core.logger import TipelsLogger

__all__ = [
    "TipelsConfig",
    "TipelsLogger",
    "__version__",
    "__author__",
    "__copyright__",
    "__license__",
    "__website__",
    "__website_label__",
    "__description__",
    "__long_description__",
    "__authors__",
    "__documenters__",
]
