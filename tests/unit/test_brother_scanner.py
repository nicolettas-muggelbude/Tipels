"""
Tests für Brother Scanner-Manager
"""

import pytest
from unittest.mock import MagicMock, patch
import subprocess

from tipels.drivers.brother.scanner import (
    BrotherScannerManager,
    ScannerConnectionType,
    ScannerConfigurationError,
)
from tipels.core.logger import TipelsLogger


class TestBrotherScannerManager:
    """Tests für BrotherScannerManager"""

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        return MagicMock(spec=TipelsLogger)

    @pytest.fixture
    def scanner_manager(self, mock_logger):
        """BrotherScannerManager Instanz"""
        return BrotherScannerManager(logger=mock_logger)

    @patch("subprocess.run")
    def test_is_brscan4_installed_true(self, mock_run, scanner_manager):
        """Test: brscan4 ist installiert"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = scanner_manager.is_brscan4_installed()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_is_brscan4_installed_false(self, mock_run, scanner_manager):
        """Test: brscan4 nicht installiert"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = scanner_manager.is_brscan4_installed()

        assert result is False

    @patch("subprocess.run")
    def test_add_scanner_usb_success(self, mock_run, scanner_manager):
        """Test: USB-Scanner erfolgreich hinzufügen"""
        # Mock: brscan4 verfügbar + Registrierung erfolgreich
        mock_results = [
            MagicMock(returncode=0),  # which brsaneconfig4
            MagicMock(returncode=0, stdout="", stderr=""),  # brsaneconfig4 -a
        ]
        mock_run.side_effect = mock_results

        result = scanner_manager.add_scanner(
            name="Brother_MFC-L2700DN",
            model="MFC-L2700DN",
            connection_type=ScannerConnectionType.USB,
            device_node="/dev/usb/lp0",
        )

        assert result is True
        assert mock_run.call_count == 2

        # Prüfe brsaneconfig4-Aufruf
        add_call = mock_run.call_args_list[1]
        cmd = add_call[0][0]
        assert "brsaneconfig4" in cmd
        assert "-a" in cmd
        assert "name=Brother_MFC-L2700DN" in cmd
        assert "model=MFC-L2700DN" in cmd
        assert "nodename=/dev/usb/lp0" in cmd

    @patch("subprocess.run")
    def test_add_scanner_network_success(self, mock_run, scanner_manager):
        """Test: Netzwerk-Scanner erfolgreich hinzufügen"""
        mock_results = [
            MagicMock(returncode=0),  # which
            MagicMock(returncode=0, stdout="", stderr=""),  # brsaneconfig4
        ]
        mock_run.side_effect = mock_results

        result = scanner_manager.add_scanner(
            name="Brother_MFC-L2700DN",
            model="MFC-L2700DN",
            connection_type=ScannerConnectionType.NETWORK,
            ip_address="192.168.1.100",
        )

        assert result is True

        # Prüfe IP im Aufruf
        add_call = mock_run.call_args_list[1]
        cmd = add_call[0][0]
        assert "ip=192.168.1.100" in cmd

    @patch("subprocess.run")
    def test_add_scanner_usb_missing_device_node(self, mock_run, scanner_manager):
        """Test: USB-Scanner ohne device_node"""
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(ScannerConfigurationError, match="device_node"):
            scanner_manager.add_scanner(
                name="Brother_MFC-L2700DN",
                model="MFC-L2700DN",
                connection_type=ScannerConnectionType.USB,
                # device_node fehlt!
            )

    @patch("subprocess.run")
    def test_add_scanner_network_missing_ip(self, mock_run, scanner_manager):
        """Test: Netzwerk-Scanner ohne IP"""
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(ScannerConfigurationError, match="ip_address"):
            scanner_manager.add_scanner(
                name="Brother_MFC-L2700DN",
                model="MFC-L2700DN",
                connection_type=ScannerConnectionType.NETWORK,
                # ip_address fehlt!
            )

    @patch("subprocess.run")
    def test_add_scanner_brscan4_not_installed(self, mock_run, scanner_manager):
        """Test: Scanner hinzufügen ohne brscan4"""
        # brscan4 nicht installiert
        mock_run.return_value = MagicMock(returncode=1)

        with pytest.raises(ScannerConfigurationError, match="nicht installiert"):
            scanner_manager.add_scanner(
                name="Brother_MFC-L2700DN",
                model="MFC-L2700DN",
                connection_type=ScannerConnectionType.USB,
                device_node="/dev/usb/lp0",
            )

    @patch("subprocess.run")
    def test_add_scanner_registration_failed(self, mock_run, scanner_manager):
        """Test: Scanner-Registrierung fehlgeschlagen"""
        mock_results = [
            MagicMock(returncode=0),  # brscan4 verfügbar
            MagicMock(returncode=1, stdout="", stderr="Registration failed"),  # Fehler
        ]
        mock_run.side_effect = mock_results

        with pytest.raises(ScannerConfigurationError, match="fehlgeschlagen"):
            scanner_manager.add_scanner(
                name="Brother_MFC-L2700DN",
                model="MFC-L2700DN",
                connection_type=ScannerConnectionType.USB,
                device_node="/dev/usb/lp0",
            )

    @patch("subprocess.run")
    def test_remove_scanner_success(self, mock_run, scanner_manager):
        """Test: Scanner erfolgreich entfernen"""
        mock_results = [
            MagicMock(returncode=0),  # brscan4 verfügbar
            MagicMock(returncode=0, stdout="", stderr=""),  # Entfernung erfolgreich
        ]
        mock_run.side_effect = mock_results

        result = scanner_manager.remove_scanner("Brother_MFC-L2700DN")

        assert result is True

        # Prüfe brsaneconfig4 -r Aufruf
        remove_call = mock_run.call_args_list[1]
        cmd = remove_call[0][0]
        assert "brsaneconfig4" in cmd
        assert "-r" in cmd
        assert "Brother_MFC-L2700DN" in cmd

    @patch("subprocess.run")
    def test_list_scanners_success(self, mock_run, scanner_manager):
        """Test: Scanner auflisten"""
        mock_output = """  0 Brother_MFC-L2700DN         "MFC-L2700DN"         I:192.168.1.100
  1 Brother_DCP-L2540DN         "DCP-L2540DN"         0x04f9:0x0358
"""
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")

        scanners = scanner_manager.list_scanners()

        assert len(scanners) == 2
        assert scanners[0]["name"] == "Brother_MFC-L2700DN"
        assert scanners[0]["model"] == "MFC-L2700DN"
        assert "192.168.1.100" in scanners[0]["connection"]
        assert scanners[1]["name"] == "Brother_DCP-L2540DN"

    @patch("subprocess.run")
    def test_list_scanners_empty(self, mock_run, scanner_manager):
        """Test: Keine Scanner gefunden"""
        mock_run.return_value = MagicMock(returncode=0, stdout="No scanners found.", stderr="")

        scanners = scanner_manager.list_scanners()

        assert len(scanners) == 0

    @patch("subprocess.run")
    def test_list_scanners_not_installed(self, mock_run, scanner_manager):
        """Test: Scanner auflisten ohne brscan4"""
        mock_run.return_value = MagicMock(returncode=1)

        scanners = scanner_manager.list_scanners()

        assert len(scanners) == 0

    @patch("subprocess.run")
    def test_test_scan_success(self, mock_run, scanner_manager):
        """Test: Erfolgreicher Test-Scan"""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = scanner_manager.test_scan(
            scanner_name="Brother_MFC-L2700DN", output_file="/tmp/test.pnm"
        )

        assert result is True

        # Prüfe scanimage-Aufruf
        cmd = mock_run.call_args[0][0]
        assert "scanimage" in cmd
        assert "--device-name" in cmd
        assert "brother4:Brother_MFC-L2700DN" in cmd
        assert "--output-file" in cmd
        assert "/tmp/test.pnm" in cmd

    @patch("subprocess.run")
    def test_test_scan_auto_device(self, mock_run, scanner_manager):
        """Test: Test-Scan ohne spezifischen Scanner"""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = scanner_manager.test_scan()

        assert result is True

        # Prüfe dass kein --device-name verwendet wird
        cmd = mock_run.call_args[0][0]
        assert "scanimage" in cmd
        assert "--device-name" not in cmd

    @patch("subprocess.run")
    def test_test_scan_failed(self, mock_run, scanner_manager):
        """Test: Fehlgeschlagener Test-Scan"""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="No scanner found")

        with pytest.raises(ScannerConfigurationError, match="fehlgeschlagen"):
            scanner_manager.test_scan()

    @patch("subprocess.run")
    def test_test_scan_timeout(self, mock_run, scanner_manager):
        """Test: Test-Scan Timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["scanimage"], timeout=60)

        with pytest.raises(ScannerConfigurationError, match="Timeout"):
            scanner_manager.test_scan()

    @patch("subprocess.run")
    def test_get_scanner_status(self, mock_run, scanner_manager):
        """Test: Scanner-Status abrufen"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if "brsaneconfig4" in cmd:
                return MagicMock(returncode=0)  # brscan4 installiert
            elif "scanimage" in cmd:
                return MagicMock(returncode=0)  # SANE verfügbar
            elif "getent" in cmd and "scanner" in cmd:
                return MagicMock(returncode=0)  # scanner-Gruppe existiert
            elif "getent" in cmd and "saned" in cmd:
                return MagicMock(returncode=0)  # saned-Gruppe existiert
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        status = scanner_manager.get_scanner_status()

        assert status["brscan4_installed"] is True
        assert status["sane_available"] is True
        assert status["scanner_group_exists"] is True
        assert status["saned_group_exists"] is True

    @patch("subprocess.run")
    @patch("getpass.getuser")
    def test_add_user_to_groups_success(self, mock_getuser, mock_run, scanner_manager):
        """Test: Benutzer zu Gruppen hinzufügen"""
        mock_getuser.return_value = "testuser"

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if "getent" in cmd:
                return MagicMock(returncode=0)  # Alle Gruppen existieren
            elif "usermod" in cmd:
                return MagicMock(returncode=0, stdout="", stderr="")  # Erfolgreich
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        success, groups = scanner_manager.add_user_to_groups(use_sudo=False)

        assert success is True
        assert "scanner" in groups
        assert "saned" in groups
        assert "lp" in groups
        assert len(groups) == 3

    @patch("subprocess.run")
    @patch("getpass.getuser")
    def test_add_user_to_groups_with_sudo(self, mock_getuser, mock_run, scanner_manager):
        """Test: Benutzer zu Gruppen hinzufügen mit sudo"""
        mock_getuser.return_value = "testuser"

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if "getent" in cmd:
                return MagicMock(returncode=0)
            elif "usermod" in cmd:
                # Prüfe dass sudo verwendet wird
                assert cmd[0] == "sudo"
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        success, groups = scanner_manager.add_user_to_groups(use_sudo=True)

        assert success is True

    @patch("subprocess.run")
    @patch("getpass.getuser")
    def test_add_user_to_groups_group_not_exists(self, mock_getuser, mock_run, scanner_manager):
        """Test: Benutzer zu nicht-existierenden Gruppen hinzufügen"""
        mock_getuser.return_value = "testuser"

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if "getent" in cmd and "scanner" in cmd:
                return MagicMock(returncode=0)  # scanner existiert
            elif "getent" in cmd:
                return MagicMock(returncode=1)  # andere nicht
            elif "usermod" in cmd:
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        success, groups = scanner_manager.add_user_to_groups(use_sudo=False)

        # Nur scanner-Gruppe sollte hinzugefügt worden sein
        assert success is True
        assert groups == ["scanner"]

    @patch("subprocess.run")
    def test_add_scanner_timeout(self, mock_run, scanner_manager):
        """Test: Scanner-Registrierung Timeout"""
        mock_results = [
            MagicMock(returncode=0),  # brscan4 verfügbar
            subprocess.TimeoutExpired(cmd=["brsaneconfig4"], timeout=30),
        ]
        mock_run.side_effect = mock_results

        with pytest.raises(ScannerConfigurationError, match="Timeout"):
            scanner_manager.add_scanner(
                name="Brother_MFC-L2700DN",
                model="MFC-L2700DN",
                connection_type=ScannerConnectionType.USB,
                device_node="/dev/usb/lp0",
            )
