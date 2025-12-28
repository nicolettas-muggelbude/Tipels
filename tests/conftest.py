"""
Pytest-Konfiguration und gemeinsame Fixtures für Tipels-Tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Erstellt ein temporäres Verzeichnis für Tests"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def temp_config_dir(temp_dir, monkeypatch):
    """Erstellt temporäres Config-Verzeichnis und setzt HOME"""
    config_dir = temp_dir / ".config" / "tipels"
    config_dir.mkdir(parents=True)

    # Mock HOME-Verzeichnis
    monkeypatch.setenv("HOME", str(temp_dir))

    yield config_dir


@pytest.fixture
def temp_log_dir(temp_dir, monkeypatch):
    """Erstellt temporäres Log-Verzeichnis"""
    log_dir = temp_dir / ".local" / "share" / "tipels" / "logs"
    log_dir.mkdir(parents=True)

    # Mock HOME-Verzeichnis
    monkeypatch.setenv("HOME", str(temp_dir))

    yield log_dir


@pytest.fixture
def mock_system_calls(monkeypatch):
    """Mock für System-Calls (lsusb, lpinfo, etc.)"""

    # Mock lsusb
    def mock_lsusb(*args, **kwargs):
        return """Bus 001 Device 003: ID 04f9:0273 Brother Industries, Ltd MFC-L2700DN"""

    # Mock lpinfo
    def mock_lpinfo(*args, **kwargs):
        return """network ipp
network ipps
network http
network https
network socket"""

    # Mock scanimage
    def mock_scanimage(*args, **kwargs):
        return """device 'brother4:net1;dev0' is a Brother MFC-L2700DN network scanner"""

    # TODO: Weitere Mock-Funktionen hinzufügen

    return {
        "lsusb": mock_lsusb,
        "lpinfo": mock_lpinfo,
        "scanimage": mock_scanimage,
    }
