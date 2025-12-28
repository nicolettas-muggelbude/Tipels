"""
Unit-Tests für das Tipels Logging-System
"""

import logging
from pathlib import Path

import pytest

from tipels.core.logger import TipelsLogger


class TestTipelsLogger:
    """Tests für TipelsLogger"""

    def test_logger_creation(self, temp_log_dir):
        """Test: Logger kann erstellt werden"""
        logger = TipelsLogger(name="test-logger")

        assert logger is not None
        assert logger.logger.name == "test-logger"

    def test_logger_default_level(self, temp_log_dir):
        """Test: Standard-Log-Level ist INFO"""
        logger = TipelsLogger()

        assert logger.logger.level == logging.INFO

    def test_logger_custom_level(self, temp_log_dir):
        """Test: Custom Log-Level wird gesetzt"""
        logger = TipelsLogger(log_level=logging.DEBUG)

        assert logger.logger.level == logging.DEBUG

    def test_log_directory_creation(self, temp_log_dir):
        """Test: Log-Verzeichnis wird erstellt"""
        logger = TipelsLogger()

        # Prüfe ob Log-Verzeichnis existiert
        assert temp_log_dir.exists()
        assert temp_log_dir.is_dir()

    def test_log_file_creation(self, temp_log_dir):
        """Test: Log-Datei wird erstellt"""
        logger = TipelsLogger()

        # Schreibe eine Log-Nachricht
        logger.info("Test-Nachricht")

        # Prüfe ob Log-Datei existiert
        log_file = temp_log_dir / "tipels.log"
        assert log_file.exists()

    def test_info_logging(self, temp_log_dir):
        """Test: Info-Logs werden geschrieben"""
        logger = TipelsLogger()
        test_message = "Dies ist eine Info-Nachricht"

        logger.info(test_message)

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        assert test_message in content
        assert "INFO" in content

    def test_error_logging(self, temp_log_dir):
        """Test: Error-Logs werden geschrieben"""
        logger = TipelsLogger()
        test_message = "Dies ist eine Error-Nachricht"

        logger.error(test_message)

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        assert test_message in content
        assert "ERROR" in content

    def test_debug_logging_disabled_by_default(self, temp_log_dir):
        """Test: Debug-Logs sind standardmäßig deaktiviert"""
        logger = TipelsLogger(log_level=logging.INFO)
        test_message = "Debug-Nachricht"

        logger.debug(test_message)

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        # Debug sollte NICHT im Log sein
        assert test_message not in content

    def test_debug_logging_when_enabled(self, temp_log_dir):
        """Test: Debug-Logs wenn aktiviert"""
        logger = TipelsLogger(log_level=logging.DEBUG)
        test_message = "Debug-Nachricht"

        logger.debug(test_message)

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        assert test_message in content
        assert "DEBUG" in content

    def test_warning_logging(self, temp_log_dir):
        """Test: Warning-Logs werden geschrieben"""
        logger = TipelsLogger()
        test_message = "Warnung"

        logger.warning(test_message)

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        assert test_message in content
        assert "WARNING" in content

    def test_critical_logging(self, temp_log_dir):
        """Test: Critical-Logs werden geschrieben"""
        logger = TipelsLogger()
        test_message = "Kritischer Fehler"

        logger.critical(test_message)

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        assert test_message in content
        assert "CRITICAL" in content

    def test_multiple_log_entries(self, temp_log_dir):
        """Test: Mehrere Log-Einträge werden geschrieben"""
        logger = TipelsLogger()

        logger.info("Nachricht 1")
        logger.warning("Nachricht 2")
        logger.error("Nachricht 3")

        log_file = temp_log_dir / "tipels.log"
        content = log_file.read_text()

        assert "Nachricht 1" in content
        assert "Nachricht 2" in content
        assert "Nachricht 3" in content

    # TODO: Test für Log-Rotation hinzufügen
    # TODO: Test für Crash-Report-Generator hinzufügen
