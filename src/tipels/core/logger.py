"""
Tipels - Logging System

Zentrales Logging für Tipels mit einfachen und Debug-Logs
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


class TipelsLogger:
    """Zentrales Logging-System für Tipels"""

    def __init__(self, name="tipels", log_level=logging.INFO):
        """
        Initialisiert den Logger

        Args:
            name: Name des Loggers
            log_level: Logging-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Log-Verzeichnis erstellen
        log_dir = Path.home() / ".local" / "share" / "tipels" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log-Datei
        log_file = log_dir / "tipels.log"

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler mit Rotation
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        """Debug-Log"""
        self.logger.debug(message)

    def info(self, message):
        """Info-Log"""
        self.logger.info(message)

    def warning(self, message):
        """Warning-Log"""
        self.logger.warning(message)

    def error(self, message):
        """Error-Log"""
        self.logger.error(message)

    def critical(self, message):
        """Critical-Log"""
        self.logger.critical(message)

    def exception(self, message):
        """Exception-Log mit Traceback"""
        self.logger.exception(message)

    # TODO: Crash-Report-Generator implementieren
    def generate_crash_report(self, exception):
        """
        Erstellt einen Crash-Report für GitHub-Issues

        Args:
            exception: Die aufgetretene Exception

        Returns:
            str: Formatierter Crash-Report
        """
        # TODO: Implementierung
        pass


# Globaler Logger
logger = TipelsLogger()
