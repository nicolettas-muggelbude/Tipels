"""
Tests für Drucker-Cache
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tipels.core.logger import TipelsLogger
from tipels.core.printer_cache import PrinterCache


class TestPrinterCache:
    """Tests für PrinterCache"""

    @pytest.fixture
    def temp_cache_file(self):
        """Temporäre Cache-Datei"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            cache_file = Path(f.name)
        yield cache_file
        if cache_file.exists():
            cache_file.unlink()

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        return MagicMock(spec=TipelsLogger)

    @pytest.fixture
    def cache(self, temp_cache_file, mock_logger):
        """PrinterCache Instanz"""
        return PrinterCache(cache_file=temp_cache_file, logger=mock_logger)

    def test_cache_initialization(self, cache):
        """Test: Cache initialisieren"""
        assert cache.count() == 0

    def test_set_and_get(self, cache):
        """Test: Cache-Eintrag setzen und abrufen"""
        cache.set(
            manufacturer="Brother",
            model="MFC-L2700DN",
            openprinting_driver="brlaser",
            official_driver="brother-lpr",
            ppd_name="brother-mfc-l2700dn-brlaser.ppd",
        )

        entry = cache.get("Brother", "MFC-L2700DN")

        assert entry is not None
        assert entry["manufacturer"] == "Brother"
        assert entry["model"] == "MFC-L2700DN"
        assert entry["openprinting_driver"] == "brlaser"
        assert entry["official_driver"] == "brother-lpr"
        assert entry["last_used"] == "brlaser"
        assert entry["ppd_name"] == "brother-mfc-l2700dn-brlaser.ppd"
        assert "last_updated" in entry

    def test_get_not_found(self, cache):
        """Test: Nicht vorhandener Eintrag"""
        entry = cache.get("Unknown", "Printer")

        assert entry is None

    def test_case_insensitive_key(self, cache):
        """Test: Groß-/Kleinschreibung egal"""
        cache.set(
            manufacturer="Brother",
            model="MFC-L2700DN",
            openprinting_driver="brlaser",
        )

        # Abrufen mit unterschiedlicher Schreibweise
        entry1 = cache.get("brother", "mfc-l2700dn")
        entry2 = cache.get("BROTHER", "MFC-L2700DN")

        assert entry1 is not None
        assert entry2 is not None
        assert entry1 == entry2

    def test_update(self, cache):
        """Test: Cache-Eintrag aktualisieren"""
        cache.set(
            manufacturer="Brother",
            model="MFC-L2700DN",
            openprinting_driver="brlaser",
        )

        cache.update(
            manufacturer="Brother",
            model="MFC-L2700DN",
            last_used="brother-lpr",
            user_preference="official",
        )

        entry = cache.get("Brother", "MFC-L2700DN")

        assert entry["openprinting_driver"] == "brlaser"  # Unverändert
        assert entry["last_used"] == "brother-lpr"  # Aktualisiert
        assert entry["user_preference"] == "official"  # Neu

    def test_delete(self, cache):
        """Test: Cache-Eintrag löschen"""
        cache.set(
            manufacturer="Brother",
            model="MFC-L2700DN",
            openprinting_driver="brlaser",
        )

        assert cache.count() == 1

        result = cache.delete("Brother", "MFC-L2700DN")

        assert result is True
        assert cache.count() == 0
        assert cache.get("Brother", "MFC-L2700DN") is None

    def test_delete_not_found(self, cache):
        """Test: Löschen nicht vorhandener Eintrag"""
        result = cache.delete("Unknown", "Printer")

        assert result is False

    def test_clear(self, cache):
        """Test: Gesamten Cache löschen"""
        cache.set("Brother", "MFC-L2700DN", openprinting_driver="brlaser")
        cache.set("HP", "LaserJet M404dn", openprinting_driver="hplip")

        assert cache.count() == 2

        cache.clear()

        assert cache.count() == 0

    def test_get_all(self, cache):
        """Test: Alle Einträge abrufen"""
        cache.set("Brother", "MFC-L2700DN", openprinting_driver="brlaser")
        cache.set("HP", "LaserJet M404dn", openprinting_driver="hplip")

        all_entries = cache.get_all()

        assert len(all_entries) == 2
        assert "brother:mfc-l2700dn" in all_entries
        assert "hp:laserjet m404dn" in all_entries

    def test_persistence(self, temp_cache_file, mock_logger):
        """Test: Cache wird persistent gespeichert"""
        # Cache erstellen und Daten speichern
        cache1 = PrinterCache(cache_file=temp_cache_file, logger=mock_logger)
        cache1.set("Brother", "MFC-L2700DN", openprinting_driver="brlaser")

        # Neuer Cache von gleicher Datei
        cache2 = PrinterCache(cache_file=temp_cache_file, logger=mock_logger)

        entry = cache2.get("Brother", "MFC-L2700DN")

        assert entry is not None
        assert entry["openprinting_driver"] == "brlaser"

    def test_json_format(self, cache, temp_cache_file):
        """Test: Cache-Datei ist valides JSON"""
        cache.set("Brother", "MFC-L2700DN", openprinting_driver="brlaser")

        with open(temp_cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "brother:mfc-l2700dn" in data
        assert data["brother:mfc-l2700dn"]["openprinting_driver"] == "brlaser"

    def test_corrupted_cache_file(self, temp_cache_file, mock_logger):
        """Test: Korrupte Cache-Datei wird ignoriert"""
        # Schreibe ungültiges JSON
        with open(temp_cache_file, "w") as f:
            f.write("{ invalid json }")

        # Cache sollte trotzdem initialisiert werden
        cache = PrinterCache(cache_file=temp_cache_file, logger=mock_logger)

        assert cache.count() == 0

    def test_count(self, cache):
        """Test: Anzahl Einträge"""
        assert cache.count() == 0

        cache.set("Brother", "MFC-L2700DN", openprinting_driver="brlaser")
        assert cache.count() == 1

        cache.set("HP", "LaserJet M404dn", openprinting_driver="hplip")
        assert cache.count() == 2

        cache.delete("Brother", "MFC-L2700DN")
        assert cache.count() == 1

    def test_last_used_default(self, cache):
        """Test: last_used defaultet zu openprinting_driver"""
        cache.set(
            manufacturer="Brother",
            model="MFC-L2700DN",
            openprinting_driver="brlaser",
        )

        entry = cache.get("Brother", "MFC-L2700DN")

        assert entry["last_used"] == "brlaser"

    def test_custom_metadata(self, cache):
        """Test: Eigene Metadaten speichern"""
        cache.set(
            manufacturer="Brother",
            model="MFC-L2700DN",
            openprinting_driver="brlaser",
            custom_field="custom_value",
            another_field=123,
        )

        entry = cache.get("Brother", "MFC-L2700DN")

        assert entry["custom_field"] == "custom_value"
        assert entry["another_field"] == 123
