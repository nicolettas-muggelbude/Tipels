"""
Tests für Foomatic-Integration
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from tipels.core.foomatic import FoomaticDetector, FoomaticDriver
from tipels.core.logger import TipelsLogger

# Mock lpinfo -m Ausgabe
MOCK_LPINFO_OUTPUT = """drv:///sample.drv/generic.ppd Generic PCL Laser Printer
brother-mfc-l2700dn-brlaser.ppd Brother MFC-L2700DN Foomatic/brlaser
brother-mfc-l2700dn-cups.ppd Brother MFC-L2700DN CUPS Driver
brother-mfc-l3770cdw-brlaser.ppd Brother MFC-L3770CDW Foomatic/brlaser
hp-laserjet_pro_m404dn-hplip.ppd HP LaserJet Pro M404dn Foomatic/hplip
canon-pixma-tr4500-gutenprint.ppd Canon PIXMA TR4500 Gutenprint
"""


class TestFoomaticDetector:
    """Tests für FoomaticDetector"""

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        return MagicMock(spec=TipelsLogger)

    @pytest.fixture
    def detector(self, mock_logger):
        """FoomaticDetector Instanz"""
        return FoomaticDetector(logger=mock_logger)

    @patch("subprocess.run")
    def test_is_foomatic_available_true(self, mock_run, detector):
        """Test: Foomatic ist verfügbar"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = detector.is_foomatic_available()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_is_foomatic_available_false(self, mock_run, detector):
        """Test: Foomatic nicht verfügbar"""
        mock_run.side_effect = FileNotFoundError()

        result = detector.is_foomatic_available()

        assert result is False

    @patch("subprocess.run")
    def test_get_all_ppd_files(self, mock_run, detector):
        """Test: Alle PPD-Dateien abrufen"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        ppd_list = detector.get_all_ppd_files()

        assert len(ppd_list) == 6
        assert "brother-mfc-l2700dn-brlaser.ppd Brother MFC-L2700DN Foomatic/brlaser" in ppd_list

    @patch("subprocess.run")
    def test_get_all_ppd_files_cached(self, mock_run, detector):
        """Test: PPD-Liste wird gecacht"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        # Erster Aufruf
        ppd_list1 = detector.get_all_ppd_files()

        # Zweiter Aufruf (sollte Cache nutzen)
        ppd_list2 = detector.get_all_ppd_files()

        # lpinfo sollte nur einmal aufgerufen worden sein
        assert mock_run.call_count == 1
        assert ppd_list1 == ppd_list2

    @patch("subprocess.run")
    def test_find_drivers_for_printer_brother(self, mock_run, detector):
        """Test: Treiber für Brother MFC-L2700DN finden"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        drivers = detector.find_drivers_for_printer("Brother", "MFC-L2700DN")

        assert len(drivers) == 2  # brlaser + cups
        assert drivers[0].manufacturer == "Brother"
        assert drivers[0].model == "MFC-L2700DN"
        assert drivers[0].driver in ["brlaser", "cups"]

    @patch("subprocess.run")
    def test_find_drivers_for_printer_hp(self, mock_run, detector):
        """Test: Treiber für HP LaserJet finden"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        drivers = detector.find_drivers_for_printer("HP", "LaserJet Pro M404dn")

        assert len(drivers) == 1
        assert drivers[0].driver == "hplip"

    @patch("subprocess.run")
    def test_find_drivers_for_printer_not_found(self, mock_run, detector):
        """Test: Keine Treiber gefunden"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        drivers = detector.find_drivers_for_printer("Unknown", "Printer")

        assert len(drivers) == 0

    @patch("subprocess.run")
    def test_get_recommended_driver_brother(self, mock_run, detector):
        """Test: Empfohlener Treiber für Brother"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        driver = detector.get_recommended_driver("Brother", "MFC-L2700DN")

        assert driver is not None
        assert driver.driver == "brlaser"  # brlaser hat höchste Priorität

    @patch("subprocess.run")
    def test_get_recommended_driver_priority(self, mock_run, detector):
        """Test: Treiber-Priorität (brlaser > hplip > gutenprint)"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = MOCK_LPINFO_OUTPUT
        mock_run.return_value = mock_result

        # HP sollte hplip bevorzugen
        driver_hp = detector.get_recommended_driver("HP", "LaserJet Pro M404dn")
        assert driver_hp.driver == "hplip"

        # Canon sollte gutenprint bekommen
        driver_canon = detector.get_recommended_driver("Canon", "PIXMA TR4500")
        assert driver_canon.driver == "gutenprint"

    def test_extract_driver_name(self, detector):
        """Test: Treiber-Name aus PPD extrahieren"""
        # Pattern 1: brother-mfc-l2700dn-brlaser.ppd
        driver1 = detector._extract_driver_name(
            "brother-mfc-l2700dn-brlaser.ppd",
            "Brother MFC-L2700DN Foomatic/brlaser",
        )
        assert driver1 == "brlaser"

        # Pattern 2: Foomatic/hplip in Description
        driver2 = detector._extract_driver_name("hp-laserjet.ppd", "HP LaserJet Foomatic/hplip")
        assert driver2 == "hplip"

    @patch("subprocess.run")
    def test_get_ppd_file_path(self, mock_run, detector):
        """Test: PPD-Dateipfad abrufen"""
        ppd_name = "brother-mfc-l2700dn-brlaser.ppd"
        result = detector.get_ppd_file_path(ppd_name)

        # Für CUPS brauchen wir nur den PPD-Namen
        assert result == ppd_name

    @patch("subprocess.run")
    def test_lpinfo_timeout(self, mock_run, detector):
        """Test: lpinfo Timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["lpinfo"], timeout=30)

        result = detector.is_foomatic_available()

        assert result is False
