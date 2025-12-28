"""
Tests für CUPS-Helper
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from tipels.core.logger import TipelsLogger
from tipels.utils.cups_helper import (
    CupsError,
    CupsHelper,
    PrinterInfo,
    PrinterState,
)


class TestCupsHelper:
    """Tests für CupsHelper"""

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        return MagicMock(spec=TipelsLogger)

    @pytest.fixture
    def cups_helper(self, mock_logger):
        """CupsHelper Instanz"""
        return CupsHelper(logger=mock_logger)

    @patch("subprocess.run")
    def test_is_cups_available_true(self, mock_run, cups_helper):
        """Test: CUPS ist verfügbar"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "scheduler is running"
        mock_run.return_value = mock_result

        result = cups_helper.is_cups_available()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_is_cups_available_false(self, mock_run, cups_helper):
        """Test: CUPS nicht verfügbar"""
        mock_run.side_effect = FileNotFoundError()

        result = cups_helper.is_cups_available()

        assert result is False

    @patch("subprocess.run")
    def test_list_printers_success(self, mock_run, cups_helper):
        """Test: Drucker auflisten"""
        mock_lpstat_output = """printer Brother_MFC-L2700DN is idle.  enabled since Thu Dec 14 10:30:00 2025
printer HP_LaserJet is printing.  enabled since Thu Dec 14 10:00:00 2025
"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "lpstat" and "-r" in cmd:
                return MagicMock(returncode=0, stdout="scheduler is running")
            elif cmd[0] == "lpstat" and "-p" in cmd:
                return MagicMock(returncode=0, stdout=mock_lpstat_output, stderr="")
            elif cmd[0] == "lpstat" and "-v" in cmd:
                return MagicMock(
                    returncode=0,
                    stdout="device for Brother_MFC-L2700DN: usb://Brother/MFC-L2700DN",
                )
            elif cmd[0] == "lpoptions":
                return MagicMock(returncode=0, stdout="")
            elif cmd[0] == "lpstat" and "-o" in cmd:
                return MagicMock(returncode=0, stdout="")
            return MagicMock(returncode=1, stdout="", stderr="")

        mock_run.side_effect = mock_subprocess

        printers = cups_helper.list_printers()

        assert len(printers) == 2
        assert printers[0].name == "Brother_MFC-L2700DN"
        assert printers[0].state == PrinterState.IDLE
        assert printers[1].name == "HP_LaserJet"
        assert printers[1].state == PrinterState.PRINTING

    @patch("subprocess.run")
    def test_list_printers_cups_not_available(self, mock_run, cups_helper):
        """Test: Drucker auflisten ohne CUPS"""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        with pytest.raises(CupsError, match="nicht verfügbar"):
            cups_helper.list_printers()

    @patch("subprocess.run")
    def test_add_printer_usb_success(self, mock_run, cups_helper):
        """Test: USB-Drucker erfolgreich hinzufügen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),  # is_cups_available
            MagicMock(returncode=0, stdout="", stderr=""),  # lpadmin
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.add_printer(
            name="Brother_MFC-L2700DN",
            uri="usb://Brother/MFC-L2700DN",
            ppd_file="brother-mfc-l2700dn.ppd",
            location="Office",
            description="Brother MFC-L2700DN",
            use_sudo=False,
        )

        assert result is True
        assert mock_run.call_count == 2

        # Prüfe lpadmin-Aufruf
        lpadmin_call = mock_run.call_args_list[1]
        cmd = lpadmin_call[0][0]
        assert "lpadmin" in cmd
        assert "-p" in cmd
        assert "Brother_MFC-L2700DN" in cmd
        assert "-E" in cmd
        assert "-v" in cmd
        assert "usb://Brother/MFC-L2700DN" in cmd
        assert "-m" in cmd
        assert "brother-mfc-l2700dn.ppd" in cmd
        assert "-L" in cmd
        assert "Office" in cmd
        assert "-D" in cmd
        assert "Brother MFC-L2700DN" in cmd

    @patch("subprocess.run")
    def test_add_printer_network_ipp(self, mock_run, cups_helper):
        """Test: Netzwerk-Drucker (IPP) hinzufügen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.add_printer(
            name="Network_Printer",
            uri="ipp://192.168.1.100/ipp/print",
            use_sudo=False,
        )

        assert result is True

        # Prüfe URI
        lpadmin_call = mock_run.call_args_list[1]
        cmd = lpadmin_call[0][0]
        assert "ipp://192.168.1.100/ipp/print" in cmd

    @patch("subprocess.run")
    def test_add_printer_with_sudo(self, mock_run, cups_helper):
        """Test: Drucker mit sudo hinzufügen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.add_printer(name="Test_Printer", uri="usb://Test", use_sudo=True)

        assert result is True

        # Prüfe sudo
        lpadmin_call = mock_run.call_args_list[1]
        cmd = lpadmin_call[0][0]
        assert cmd[0] == "sudo"

    @patch("subprocess.run")
    def test_add_printer_failed(self, mock_run, cups_helper):
        """Test: Drucker hinzufügen fehlgeschlagen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=1, stdout="", stderr="lpadmin: error"),
        ]
        mock_run.side_effect = mock_results

        with pytest.raises(CupsError, match="fehlgeschlagen"):
            cups_helper.add_printer(name="Test", uri="usb://Test", use_sudo=False)

    @patch("subprocess.run")
    def test_remove_printer_success(self, mock_run, cups_helper):
        """Test: Drucker erfolgreich entfernen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.remove_printer("Brother_MFC-L2700DN", use_sudo=False)

        assert result is True

        # Prüfe lpadmin -x
        remove_call = mock_run.call_args_list[1]
        cmd = remove_call[0][0]
        assert "lpadmin" in cmd
        assert "-x" in cmd
        assert "Brother_MFC-L2700DN" in cmd

    @patch("subprocess.run")
    def test_remove_printer_with_sudo(self, mock_run, cups_helper):
        """Test: Drucker mit sudo entfernen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.remove_printer("Test_Printer", use_sudo=True)

        assert result is True

        remove_call = mock_run.call_args_list[1]
        cmd = remove_call[0][0]
        assert cmd[0] == "sudo"

    @patch("subprocess.run")
    def test_remove_printer_failed(self, mock_run, cups_helper):
        """Test: Drucker entfernen fehlgeschlagen"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=1, stdout="", stderr="Printer not found"),
        ]
        mock_run.side_effect = mock_results

        with pytest.raises(CupsError, match="fehlgeschlagen"):
            cups_helper.remove_printer("NonExistent", use_sudo=False)

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    def test_test_print_success(self, mock_run, mock_exists, cups_helper):
        """Test: Erfolgreicher Testdruck"""
        mock_exists.return_value = True
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(
                returncode=0,
                stdout="request id is Brother_MFC-L2700DN-1 (1 file(s))",
                stderr="",
            ),
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.test_print("Brother_MFC-L2700DN")

        assert result is True

        # Prüfe lp-Aufruf
        lp_call = mock_run.call_args_list[1]
        cmd = lp_call[0][0]
        assert "lp" in cmd
        assert "-d" in cmd
        assert "Brother_MFC-L2700DN" in cmd

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    def test_test_print_custom_file(self, mock_run, mock_exists, cups_helper):
        """Test: Testdruck mit eigener Datei"""
        mock_exists.return_value = True
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout="request id is Test-1", stderr=""),
        ]
        mock_run.side_effect = mock_results

        result = cups_helper.test_print("Test_Printer", test_file="/tmp/test.pdf")

        assert result is True

        lp_call = mock_run.call_args_list[1]
        cmd = lp_call[0][0]
        assert "/tmp/test.pdf" in cmd

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    def test_test_print_file_not_found(self, mock_run, mock_exists, cups_helper):
        """Test: Test-Datei nicht gefunden"""
        mock_exists.return_value = False
        mock_run.return_value = MagicMock(returncode=0, stdout="scheduler is running")

        with pytest.raises(CupsError, match="nicht gefunden"):
            cups_helper.test_print("Test_Printer")

    @patch("subprocess.run")
    def test_test_print_failed(self, mock_run, cups_helper):
        """Test: Testdruck fehlgeschlagen"""
        with patch("pathlib.Path.exists", return_value=True):
            mock_results = [
                MagicMock(returncode=0, stdout="scheduler is running"),
                MagicMock(returncode=1, stdout="", stderr="Printer not ready"),
            ]
            mock_run.side_effect = mock_results

            with pytest.raises(CupsError, match="fehlgeschlagen"):
                cups_helper.test_print("Test_Printer")

    @patch("subprocess.run")
    def test_get_printer_status_success(self, mock_run, cups_helper):
        """Test: Drucker-Status abrufen"""
        mock_status_output = """printer Brother_MFC-L2700DN is idle.  enabled since Thu Dec 14
        Description: Brother MFC-L2700DN
        Location: Office
        Interface: /etc/cups/ppd/Brother_MFC-L2700DN.ppd
"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout=mock_status_output, stderr=""),
        ]
        mock_run.side_effect = mock_results

        status = cups_helper.get_printer_status("Brother_MFC-L2700DN")

        assert status["name"] == "Brother_MFC-L2700DN"
        assert status["state"] == "idle"
        assert "Brother MFC-L2700DN" in status["description"]
        assert "Office" in status["location"]

    @patch("subprocess.run")
    def test_get_ppd_file_success(self, mock_run, cups_helper):
        """Test: PPD-Datei finden"""
        mock_lpinfo_output = """drv:///sample.drv/generic.ppd Generic PCL Laser Printer
brother-mfc-l2700dn-brlaser.ppd Brother MFC-L2700DN Foomatic/brlaser
hp-laserjet-m404dn.ppd HP LaserJet Pro M404dn
"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout=mock_lpinfo_output, stderr=""),
        ]
        mock_run.side_effect = mock_results

        ppd_file = cups_helper.get_ppd_file("Brother MFC-L2700DN")

        assert ppd_file == "brother-mfc-l2700dn-brlaser.ppd"

    @patch("subprocess.run")
    def test_get_ppd_file_not_found(self, mock_run, cups_helper):
        """Test: PPD-Datei nicht gefunden"""
        mock_results = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        mock_run.side_effect = mock_results

        ppd_file = cups_helper.get_ppd_file("Unknown Printer")

        assert ppd_file is None

    @patch("subprocess.run")
    def test_cups_timeout(self, mock_run, cups_helper):
        """Test: CUPS-Befehl Timeout"""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="scheduler is running"),
            subprocess.TimeoutExpired(cmd=["lpstat"], timeout=10),
        ]

        with pytest.raises(CupsError, match="Timeout"):
            cups_helper.list_printers()
