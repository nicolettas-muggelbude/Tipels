"""
Tests für SANE-Helper
"""

import pytest
from unittest.mock import MagicMock, patch
import subprocess
from pathlib import Path

from tipels.utils.sane_helper import (
    SaneHelper,
    SaneError,
    ScannerState,
    ScannerInfo,
    ScanFormat,
)
from tipels.core.logger import TipelsLogger


class TestSaneHelper:
    """Tests für SaneHelper"""

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        return MagicMock(spec=TipelsLogger)

    @pytest.fixture
    def sane_helper(self, mock_logger):
        """SaneHelper Instanz"""
        return SaneHelper(logger=mock_logger)

    @patch("subprocess.run")
    def test_is_sane_available_true(self, mock_run, sane_helper):
        """Test: SANE ist verfügbar"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = sane_helper.is_sane_available()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_is_sane_available_false(self, mock_run, sane_helper):
        """Test: SANE nicht verfügbar"""
        mock_run.side_effect = FileNotFoundError()

        result = sane_helper.is_sane_available()

        assert result is False

    @patch("subprocess.run")
    def test_list_scanners_success(self, mock_run, sane_helper):
        """Test: Scanner auflisten"""
        mock_scanimage_output = """device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner
device `hpaio:/usb/HP_LaserJet_M1522nf' is a Hewlett-Packard HP LaserJet M1522nf all-in-one
"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0, stdout="/usr/bin/scanimage")
            elif cmd[0] == "scanimage" and "-L" in cmd:
                return MagicMock(returncode=0, stdout=mock_scanimage_output, stderr="")
            return MagicMock(returncode=1, stdout="", stderr="")

        mock_run.side_effect = mock_subprocess

        scanners = sane_helper.list_scanners()

        assert len(scanners) == 2
        assert scanners[0].device_name == "brother4:Brother_MFC-L2700DN"
        assert scanners[0].vendor == "Brother"
        assert scanners[0].model == "MFC-L2700DN"
        assert scanners[0].backend == "brother4"
        assert scanners[0].scanner_type == "flatbed scanner"
        assert scanners[0].state == ScannerState.AVAILABLE

        assert scanners[1].device_name == "hpaio:/usb/HP_LaserJet_M1522nf"
        assert scanners[1].vendor == "Hewlett-Packard"

    @patch("subprocess.run")
    def test_list_scanners_no_scanners_found(self, mock_run, sane_helper):
        """Test: Keine Scanner gefunden"""
        mock_scanimage_output = "No scanners were identified."

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout=mock_scanimage_output, stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        scanners = sane_helper.list_scanners()

        assert len(scanners) == 0

    @patch("subprocess.run")
    def test_list_scanners_sane_not_available(self, mock_run, sane_helper):
        """Test: Scanner auflisten ohne SANE"""
        mock_run.return_value = MagicMock(returncode=1)

        with pytest.raises(SaneError, match="nicht installiert"):
            sane_helper.list_scanners()

    @patch("subprocess.run")
    def test_get_scanner_info_success(self, mock_run, sane_helper):
        """Test: Scanner-Info abrufen"""
        mock_scanimage_output = (
            "device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner"
        )

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout=mock_scanimage_output, stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        scanner_info = sane_helper.get_scanner_info("brother4:Brother_MFC-L2700DN")

        assert scanner_info is not None
        assert scanner_info.device_name == "brother4:Brother_MFC-L2700DN"
        assert scanner_info.vendor == "Brother"

    @patch("subprocess.run")
    def test_get_scanner_info_not_found(self, mock_run, sane_helper):
        """Test: Scanner-Info nicht gefunden"""
        mock_scanimage_output = (
            "device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner"
        )

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout=mock_scanimage_output, stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        scanner_info = sane_helper.get_scanner_info("nonexistent:Scanner")

        assert scanner_info is None

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("subprocess.run")
    def test_test_scan_success(self, mock_run, mock_stat, mock_exists, sane_helper):
        """Test: Erfolgreicher Test-Scan"""
        mock_exists.return_value = True
        mock_stat.return_value = MagicMock(st_size=1024000)

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout="Scanned 1 page", stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        result = sane_helper.test_scan(device_name="brother4:Brother_MFC-L2700DN")

        assert result is True

        # Prüfe scanimage-Aufruf
        scan_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "scanimage"]
        assert len(scan_calls) == 1
        cmd = scan_calls[0][0][0]
        assert "--device-name" in cmd
        assert "brother4:Brother_MFC-L2700DN" in cmd
        assert "--format" in cmd
        assert "pnm" in cmd
        assert "--resolution" in cmd
        assert "--output-file" in cmd

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("subprocess.run")
    def test_test_scan_auto_device(self, mock_run, mock_stat, mock_exists, sane_helper):
        """Test: Test-Scan mit Auto-Device"""
        mock_exists.return_value = True
        mock_stat.return_value = MagicMock(st_size=1024000)

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        result = sane_helper.test_scan()  # Kein device_name

        assert result is True

        # Prüfe dass kein --device-name übergeben wurde
        scan_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "scanimage"]
        cmd = scan_calls[0][0][0]
        assert "--device-name" not in cmd

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("subprocess.run")
    def test_test_scan_custom_format(self, mock_run, mock_stat, mock_exists, sane_helper):
        """Test: Test-Scan mit TIFF-Format"""
        mock_exists.return_value = True
        mock_stat.return_value = MagicMock(st_size=2048000)

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        result = sane_helper.test_scan(
            scan_format=ScanFormat.TIFF, output_file="/tmp/custom_scan.tiff"
        )

        assert result is True

        scan_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "scanimage"]
        cmd = scan_calls[0][0][0]
        assert "tiff" in cmd
        assert "/tmp/custom_scan.tiff" in cmd

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    def test_test_scan_file_not_created(self, mock_run, mock_exists, sane_helper):
        """Test: Scan-Datei wurde nicht erstellt"""
        mock_exists.return_value = False

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        with pytest.raises(SaneError, match="nicht erstellt"):
            sane_helper.test_scan()

    @patch("subprocess.run")
    def test_test_scan_failed(self, mock_run, sane_helper):
        """Test: Test-Scan fehlgeschlagen"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=1, stdout="", stderr="Scanner not ready")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        with pytest.raises(SaneError, match="fehlgeschlagen"):
            sane_helper.test_scan()

    @patch("subprocess.run")
    def test_test_scan_timeout(self, mock_run, sane_helper):
        """Test: Test-Scan Timeout"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                raise subprocess.TimeoutExpired(cmd=["scanimage"], timeout=120)
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        with pytest.raises(SaneError, match="Timeout"):
            sane_helper.test_scan()

    @patch("subprocess.run")
    def test_get_scanner_capabilities_success(self, mock_run, sane_helper):
        """Test: Scanner-Fähigkeiten abrufen"""
        mock_help_output = """
Options specific to device `brother4:Brother_MFC-L2700DN':
  --resolution 100..600dpi [100]
      Sets the resolution of the scanned image.
  --mode Color|Gray|Lineart [Gray]
      Selects the scan mode (e.g., lineart, gray, color).
  --source Flatbed|ADF [Flatbed]
      Selects the scan source (such as a document-feeder).
"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage" and "--help" in cmd:
                return MagicMock(returncode=0, stdout=mock_help_output, stderr="")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        capabilities = sane_helper.get_scanner_capabilities("brother4:Brother_MFC-L2700DN")

        assert "resolutions" in capabilities
        assert "100" in capabilities["resolutions"]
        assert "modes" in capabilities
        assert "Color" in capabilities["modes"]
        assert "Gray" in capabilities["modes"]
        assert "Lineart" in capabilities["modes"]
        assert "sources" in capabilities
        assert "Flatbed" in capabilities["sources"]
        assert "ADF" in capabilities["sources"]

    @patch("subprocess.run")
    def test_get_scanner_capabilities_failed(self, mock_run, sane_helper):
        """Test: Scanner-Fähigkeiten abrufen fehlgeschlagen"""

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage":
                return MagicMock(returncode=1, stdout="", stderr="Device not found")
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        with pytest.raises(SaneError, match="fehlgeschlagen"):
            sane_helper.get_scanner_capabilities("nonexistent:Scanner")

    @patch("subprocess.run")
    def test_get_scanner_status_success(self, mock_run, sane_helper):
        """Test: Scanner-Status abrufen"""
        mock_scanimage_output = (
            "device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner"
        )

        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "which":
                return MagicMock(returncode=0)
            elif cmd[0] == "scanimage" and "-L" in cmd:
                return MagicMock(returncode=0, stdout=mock_scanimage_output, stderr="")
            elif cmd[0] == "getent":
                return MagicMock(returncode=0)
            return MagicMock(returncode=1)

        mock_run.side_effect = mock_subprocess

        status = sane_helper.get_scanner_status()

        assert status["sane_available"] is True
        assert status["scanners_found"] is True
        assert status["scanner_group_exists"] is True
        assert status["saned_group_exists"] is True

    @patch("subprocess.run")
    def test_get_scanner_status_no_sane(self, mock_run, sane_helper):
        """Test: Scanner-Status ohne SANE"""
        mock_run.side_effect = FileNotFoundError()

        status = sane_helper.get_scanner_status()

        assert status["sane_available"] is False
        assert status["scanners_found"] is False

    @patch("subprocess.run")
    def test_parse_scanner_line_brother(self, mock_run, sane_helper):
        """Test: Parse Brother-Scanner-Zeile"""
        line = "device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner"

        scanner_info = sane_helper._parse_scanner_line(line)

        assert scanner_info is not None
        assert scanner_info.device_name == "brother4:Brother_MFC-L2700DN"
        assert scanner_info.vendor == "Brother"
        assert scanner_info.model == "MFC-L2700DN"
        assert scanner_info.backend == "brother4"
        assert scanner_info.scanner_type == "flatbed scanner"
        assert scanner_info.state == ScannerState.AVAILABLE

    @patch("subprocess.run")
    def test_parse_scanner_line_hp(self, mock_run, sane_helper):
        """Test: Parse HP-Scanner-Zeile"""
        line = "device `hpaio:/usb/HP_LaserJet_M1522nf' is a Hewlett-Packard HP LaserJet M1522nf all-in-one"

        scanner_info = sane_helper._parse_scanner_line(line)

        assert scanner_info is not None
        assert scanner_info.device_name == "hpaio:/usb/HP_LaserJet_M1522nf"
        assert scanner_info.vendor == "Hewlett-Packard"
        assert scanner_info.backend == "hpaio"

    @patch("subprocess.run")
    def test_parse_scanner_line_invalid(self, mock_run, sane_helper):
        """Test: Parse ungültige Zeile"""
        line = "This is not a valid scanner line"

        scanner_info = sane_helper._parse_scanner_line(line)

        assert scanner_info is None

    @patch("subprocess.run")
    def test_check_group_exists_true(self, mock_run, sane_helper):
        """Test: Gruppe existiert"""
        mock_run.return_value = MagicMock(returncode=0)

        result = sane_helper._check_group_exists("scanner")

        assert result is True

    @patch("subprocess.run")
    def test_check_group_exists_false(self, mock_run, sane_helper):
        """Test: Gruppe existiert nicht"""
        mock_run.return_value = MagicMock(returncode=2)

        result = sane_helper._check_group_exists("nonexistent")

        assert result is False

    @patch("subprocess.run")
    def test_sane_not_available_error(self, mock_run, sane_helper):
        """Test: SANE nicht verfügbar"""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(SaneError, match="nicht installiert"):
            sane_helper.list_scanners()

        with pytest.raises(SaneError, match="nicht installiert"):
            sane_helper.test_scan()

        with pytest.raises(SaneError, match="nicht installiert"):
            sane_helper.get_scanner_capabilities("test:scanner")
