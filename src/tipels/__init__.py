"""
Tipels - Einfache Einrichtung von Druckern und Scannern unter Linux

Copyright (C) 2025 Tipels Contributors
Licensed under GPL-3.0-or-later
"""

__version__ = "0.1.0"
__author__ = "Tipels Contributors"
__license__ = "GPL-3.0-or-later"

from tipels.core.config import TipelsConfig
from tipels.core.logger import TipelsLogger

__all__ = ["TipelsConfig", "TipelsLogger", "__version__"]
