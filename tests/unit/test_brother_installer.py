"""
Tests für Brother Driver-Installer
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import subprocess
from pathlib import Path
import tempfile

from tipels.drivers.brother.installer import (
    DriverInstaller,
    DriverInstallationError,
)
from tipels.core.logger import TipelsLogger


class TestDriverInstaller:
    """Tests für DriverInstaller"""

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        return MagicMock(spec=TipelsLogger)

    @pytest.fixture
    def installer(self, mock_logger):
        """DriverInstaller Instanz"""
        # Deaktiviere Foomatic für Brother-spezifische Tests
        return DriverInstaller(logger=mock_logger, use_foomatic=False)

    def test_installer_initialization(self, mock_logger):
        """Test: Installer initialisieren"""
        installer = DriverInstaller(logger=mock_logger)
        assert installer.logger == mock_logger

    @patch("subprocess.run")
    def test_is_driver_installed_true(self, mock_run, installer):
        """Test: Treiber ist installiert"""
        # Mock dpkg -l Ausgabe mit installiertem Paket
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ii  printer-driver-brlaser  6.0-1  all  Brother laser printer driver"
        mock_run.return_value = mock_result

        result = installer.is_driver_installed("printer-driver-brlaser")

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_is_driver_installed_false(self, mock_run, installer):
        """Test: Treiber ist nicht installiert"""
        # Mock dpkg -l Ausgabe ohne Paket
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = installer.is_driver_installed("printer-driver-brlaser")

        assert result is False

    @patch("subprocess.run")
    def test_get_installed_version(self, mock_run, installer):
        """Test: Installierte Version abrufen"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ii  printer-driver-brlaser  6.0-1  all  Brother laser printer driver"
        mock_run.return_value = mock_result

        version = installer.get_installed_version("printer-driver-brlaser")

        assert version == "6.0-1"

    @patch("subprocess.run")
    def test_get_installed_version_not_installed(self, mock_run, installer):
        """Test: Version von nicht installiertem Paket"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        version = installer.get_installed_version("printer-driver-brlaser")

        assert version is None

    @patch("subprocess.run")
    def test_install_from_repository_already_installed(self, mock_run, installer):
        """Test: Installation wenn bereits installiert"""
        # Mock: Paket bereits installiert
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ii  printer-driver-brlaser  6.0-1  all  Brother laser printer driver"
        mock_run.return_value = mock_result

        result = installer.install_from_repository("printer-driver-brlaser", use_sudo=False)

        assert result is True
        # Sollte nur dpkg -l aufrufen, nicht apt-get install
        assert mock_run.call_count == 1

    @patch("subprocess.run")
    def test_install_from_repository_success(self, mock_run, installer):
        """Test: Erfolgreiche Installation"""
        # Erster Call: dpkg -l (nicht installiert)
        # Zweiter Call: apt-get install (erfolgreich)
        mock_results = [
            MagicMock(returncode=1, stdout=""),  # dpkg -l: nicht installiert
            MagicMock(returncode=0, stdout="", stderr=""),  # apt-get install: erfolgreich
        ]
        mock_run.side_effect = mock_results

        result = installer.install_from_repository("printer-driver-brlaser", use_sudo=False)

        assert result is True
        assert mock_run.call_count == 2

        # Prüfe apt-get install wurde aufgerufen
        install_call = mock_run.call_args_list[1]
        assert "apt-get" in install_call[0][0]
        assert "install" in install_call[0][0]
        assert "printer-driver-brlaser" in install_call[0][0]

    @patch("subprocess.run")
    def test_install_from_repository_with_sudo(self, mock_run, installer):
        """Test: Installation mit sudo"""
        mock_results = [
            MagicMock(returncode=1, stdout=""),  # nicht installiert
            MagicMock(returncode=0, stdout="", stderr=""),  # erfolgreich
        ]
        mock_run.side_effect = mock_results

        result = installer.install_from_repository("printer-driver-brlaser", use_sudo=True)

        assert result is True

        # Prüfe dass sudo verwendet wurde
        install_call = mock_run.call_args_list[1]
        assert install_call[0][0][0] == "sudo"

    @patch("subprocess.run")
    def test_install_from_repository_failure(self, mock_run, installer):
        """Test: Fehlgeschlagene Installation"""
        mock_results = [
            MagicMock(returncode=1, stdout=""),  # nicht installiert
            MagicMock(returncode=1, stdout="", stderr="E: Package not found"),  # Installation fehlgeschlagen
        ]
        mock_run.side_effect = mock_results

        with pytest.raises(DriverInstallationError, match="Installation fehlgeschlagen"):
            installer.install_from_repository("printer-driver-brlaser", use_sudo=False)

    @patch("subprocess.run")
    def test_update_package_cache_success(self, mock_run, installer):
        """Test: Erfolgreiche Package-Cache-Aktualisierung"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = installer.update_package_cache(use_sudo=False)

        assert result is True
        mock_run.assert_called_once()
        assert "apt-get" in mock_run.call_args[0][0]
        assert "update" in mock_run.call_args[0][0]

    @patch("subprocess.run")
    def test_install_driver_for_model_success(self, mock_run, installer):
        """Test: Erfolgreiche Treiber-Installation für Modell"""
        # Mock: alle Checks und Installationen erfolgreich
        mock_results = [
            MagicMock(returncode=1, stdout=""),  # brlaser nicht installiert
            MagicMock(returncode=0, stdout="", stderr=""),  # brlaser Installation erfolgreich
            MagicMock(returncode=1, stdout=""),  # brscan4 nicht installiert
            MagicMock(returncode=0, stdout="", stderr=""),  # brscan4 Installation erfolgreich
        ]
        mock_run.side_effect = mock_results

        success, installed = installer.install_driver_for_model(
            "MFC-L2700DN", install_scanner=True, use_sudo=False
        )

        assert success is True
        assert "printer-driver-brlaser" in installed
        assert "brscan4" in installed
        assert len(installed) == 2

    @patch("subprocess.run")
    def test_install_driver_for_model_printer_only(self, mock_run, installer):
        """Test: Nur Drucker-Treiber installieren"""
        mock_results = [
            MagicMock(returncode=1, stdout=""),  # nicht installiert
            MagicMock(returncode=0, stdout="", stderr=""),  # Installation erfolgreich
        ]
        mock_run.side_effect = mock_results

        success, installed = installer.install_driver_for_model(
            "MFC-L2700DN", install_scanner=False, use_sudo=False
        )

        assert success is True
        assert "printer-driver-brlaser" in installed
        assert "brscan4" not in installed
        assert len(installed) == 1

    def test_install_driver_for_unknown_model(self, installer):
        """Test: Installation für unbekanntes Modell"""
        with pytest.raises(DriverInstallationError, match="Kein Treiber"):
            installer.install_driver_for_model("UNKNOWN-MODEL", use_sudo=False)

    @patch("subprocess.run")
    def test_uninstall_driver_success(self, mock_run, installer):
        """Test: Erfolgreiche Deinstallation"""
        mock_results = [
            MagicMock(returncode=0, stdout="ii  printer-driver-brlaser"),  # installiert
            MagicMock(returncode=0, stdout="", stderr=""),  # Deinstallation erfolgreich
        ]
        mock_run.side_effect = mock_results

        result = installer.uninstall_driver("printer-driver-brlaser", use_sudo=False)

        assert result is True
        assert mock_run.call_count == 2

        # Prüfe apt-get remove wurde aufgerufen
        remove_call = mock_run.call_args_list[1]
        assert "apt-get" in remove_call[0][0]
        assert "remove" in remove_call[0][0]
        assert "printer-driver-brlaser" in remove_call[0][0]

    @patch("subprocess.run")
    def test_uninstall_driver_not_installed(self, mock_run, installer):
        """Test: Deinstallation von nicht installiertem Treiber"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = installer.uninstall_driver("printer-driver-brlaser", use_sudo=False)

        assert result is True
        # Sollte nur dpkg -l aufrufen, nicht apt-get remove
        assert mock_run.call_count == 1

    @patch("subprocess.run")
    def test_list_installed_brother_drivers(self, mock_run, installer):
        """Test: Liste installierter Brother-Treiber"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
ii  printer-driver-brlaser  6.0-1  all  Brother laser printer driver
ii  brscan4  0.4.11-1  amd64  Brother Scanner Driver
ii  cups  2.4.2-1  amd64  Common UNIX Printing System
ii  brother-lpr-mfcl2700dn  3.5.1-1  amd64  Brother LPR Driver
        """
        mock_run.return_value = mock_result

        installed = installer.list_installed_brother_drivers()

        assert len(installed) == 3
        assert "printer-driver-brlaser" in installed
        assert "brscan4" in installed
        assert "brother-lpr-mfcl2700dn" in installed
        assert "cups" not in installed  # CUPS sollte nicht in der Liste sein

    @patch("subprocess.run")
    def test_install_timeout(self, mock_run, installer):
        """Test: Installation Timeout"""
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),  # nicht installiert
            subprocess.TimeoutExpired(cmd=["apt-get"], timeout=300),  # Timeout
        ]

        with pytest.raises(DriverInstallationError, match="zu lange gedauert"):
            installer.install_from_repository("printer-driver-brlaser", use_sudo=False)

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_deb_package_success(self, mock_file, mock_get, installer):
        """Test: Erfolgreicher .deb-Download"""
        # Mock HTTP Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"data1", b"data2"]
        mock_get.return_value = mock_response

        url = "https://example.com/brother-lpr.deb"
        result = installer.download_deb_package(url)

        assert result.name == "brother-lpr.deb"
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_download_deb_package_failure(self, mock_get, installer):
        """Test: Fehlgeschlagener Download"""
        import requests
        mock_get.side_effect = requests.RequestException("Connection error")

        url = "https://example.com/brother-lpr.deb"

        with pytest.raises(DriverInstallationError, match="Download fehlgeschlagen"):
            installer.download_deb_package(url)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.unlink")
    def test_install_deb_package_success(
        self, mock_unlink, mock_exists, mock_run, installer
    ):
        """Test: Erfolgreiche .deb-Installation"""
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        deb_file = Path("/tmp/test.deb")
        result = installer.install_deb_package(deb_file, use_sudo=False, cleanup=True)

        assert result is True
        mock_run.assert_called_once()
        # Prüfe dpkg -i wurde aufgerufen
        assert "dpkg" in mock_run.call_args[0][0]
        assert "-i" in mock_run.call_args[0][0]

        # Cleanup sollte aufgerufen worden sein
        mock_unlink.assert_called_once()

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_install_deb_package_not_found(self, mock_exists, mock_run, installer):
        """Test: .deb-Datei nicht gefunden"""
        mock_exists.return_value = False

        deb_file = Path("/tmp/test.deb")

        with pytest.raises(DriverInstallationError, match="nicht gefunden"):
            installer.install_deb_package(deb_file, use_sudo=False)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_install_deb_package_dependency_fix(
        self, mock_exists, mock_run, installer
    ):
        """Test: Abhängigkeiten automatisch reparieren"""
        mock_exists.return_value = True

        # Erster Call: dpkg -i (Abhängigkeitsfehler)
        # Zweiter Call: apt-get -f install (erfolgreich)
        mock_results = [
            MagicMock(
                returncode=1,
                stdout="",
                stderr="dpkg: dependency problems prevent configuration",
            ),
            MagicMock(returncode=0, stdout="", stderr=""),  # apt-get -f install
        ]
        mock_run.side_effect = mock_results

        deb_file = Path("/tmp/test.deb")
        result = installer.install_deb_package(deb_file, use_sudo=False, cleanup=False)

        assert result is True
        assert mock_run.call_count == 2

        # Zweiter Call sollte apt-get -f install sein
        fix_call = mock_run.call_args_list[1]
        assert "apt-get" in fix_call[0][0]
        assert "-f" in fix_call[0][0]
        assert "install" in fix_call[0][0]

    @patch("tipels.drivers.brother.installer.DriverInstaller.download_deb_package")
    @patch("tipels.drivers.brother.installer.DriverInstaller.install_deb_package")
    def test_install_from_url_success(
        self, mock_install, mock_download, installer
    ):
        """Test: Installation von URL"""
        mock_download.return_value = Path("/tmp/test.deb")
        mock_install.return_value = True

        url = "https://example.com/brother-lpr.deb"
        result = installer.install_from_url(url, use_sudo=False)

        assert result is True
        mock_download.assert_called_once_with(url)
        mock_install.assert_called_once()

    @patch("subprocess.run")
    def test_install_driver_force_official(self, mock_run, installer):
        """Test: Installation mit force_official (Brother statt OpenPrinting)"""
        # Mock: Alle Checks zeigen "nicht installiert", Installationen erfolgreich
        def mock_subprocess(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if "dpkg" in cmd and "-l" in cmd:
                # dpkg -l check: nicht installiert
                result = MagicMock()
                result.returncode = 1
                result.stdout = ""
                result.stderr = ""
                return result
            else:
                # apt-get install: erfolgreich
                result = MagicMock()
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
                return result

        mock_run.side_effect = mock_subprocess

        # force_official=True → sollte brother-lpr nutzen statt brlaser
        success, installed = installer.install_driver_for_model(
            "MFC-L2700DN", install_scanner=True, force_official=True, use_sudo=False
        )

        assert success is True
        # Sollte brother-lpr verwendet haben (alternatives[0])
        # NICHT brlaser (preferred)
        assert "brother-lpr" in installed
        assert "brscan4" in installed
        assert len(installed) == 2
