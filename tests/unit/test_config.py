"""
Unit-Tests für das Tipels Konfigurations-System
"""

import pytest
import json
from pathlib import Path
from tipels.core.config import TipelsConfig


class TestTipelsConfig:
    """Tests für TipelsConfig"""

    def test_config_creation(self, temp_config_dir):
        """Test: Config kann erstellt werden"""
        config = TipelsConfig()

        assert config is not None
        assert isinstance(config.config, dict)

    def test_default_config_values(self, temp_config_dir):
        """Test: Default-Werte sind gesetzt"""
        config = TipelsConfig()

        assert config.get("version") == "1.0"
        assert config.get("language") == "de"
        assert config.get("auto_detect") is True
        assert config.get("prefer_opensource_drivers") is False
        assert config.get("notification_enabled") is True
        assert config.get("debug_mode") is False

    def test_config_directory_creation(self, temp_config_dir):
        """Test: Config-Verzeichnis wird erstellt"""
        config = TipelsConfig()

        assert temp_config_dir.exists()
        assert temp_config_dir.is_dir()

    def test_get_existing_key(self, temp_config_dir):
        """Test: Existierenden Schlüssel abrufen"""
        config = TipelsConfig()

        value = config.get("language")

        assert value == "de"

    def test_get_nonexisting_key_with_default(self, temp_config_dir):
        """Test: Nicht-existierenden Schlüssel mit Default abrufen"""
        config = TipelsConfig()

        value = config.get("nonexistent_key", "default_value")

        assert value == "default_value"

    def test_get_nonexisting_key_without_default(self, temp_config_dir):
        """Test: Nicht-existierenden Schlüssel ohne Default abrufen"""
        config = TipelsConfig()

        value = config.get("nonexistent_key")

        assert value is None

    def test_set_config_value(self, temp_config_dir):
        """Test: Config-Wert setzen"""
        config = TipelsConfig()

        config.set("test_key", "test_value")

        assert config.get("test_key") == "test_value"

    def test_config_persistence(self, temp_config_dir):
        """Test: Config wird gespeichert und geladen"""
        # Erstelle Config und setze Wert
        config1 = TipelsConfig()
        config1.set("test_persistence", "persistenter_wert")

        # Lade Config neu
        config2 = TipelsConfig()

        assert config2.get("test_persistence") == "persistenter_wert"

    def test_config_file_creation(self, temp_config_dir):
        """Test: Config-Datei wird erstellt"""
        config = TipelsConfig()
        config.set("test", "value")

        config_file = temp_config_dir / "tipels.conf"

        assert config_file.exists()
        assert config_file.is_file()

    def test_config_file_json_format(self, temp_config_dir):
        """Test: Config-Datei ist valides JSON"""
        config = TipelsConfig()
        config.set("test", "value")

        config_file = temp_config_dir / "tipels.conf"

        # Versuche JSON zu laden
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "test" in data

    def test_update_existing_value(self, temp_config_dir):
        """Test: Existierenden Wert aktualisieren"""
        config = TipelsConfig()

        # Ursprünglicher Wert
        assert config.get("language") == "de"

        # Aktualisiere Wert
        config.set("language", "en")

        assert config.get("language") == "en"

    def test_config_backup_path_default(self, temp_config_dir):
        """Test: Standard Backup-Pfad ist gesetzt"""
        config = TipelsConfig()

        backup_path = config.get("backup_path")

        assert backup_path is not None
        assert "tipels-backups" in backup_path

    def test_multiple_config_instances_share_file(self, temp_config_dir):
        """Test: Mehrere Config-Instanzen teilen sich die Datei"""
        config1 = TipelsConfig()
        config1.set("shared_value", "test123")

        config2 = TipelsConfig()

        assert config2.get("shared_value") == "test123"

    def test_config_with_invalid_json_file(self, temp_config_dir):
        """Test: Umgang mit invalider JSON-Datei"""
        # Erstelle invalide JSON-Datei
        config_file = temp_config_dir / "tipels.conf"
        config_file.write_text("{ invalid json }")

        # Config sollte trotzdem funktionieren mit Defaults
        config = TipelsConfig()

        assert config.get("version") == "1.0"

    def test_config_handles_boolean_values(self, temp_config_dir):
        """Test: Boolean-Werte werden korrekt gehandhabt"""
        config = TipelsConfig()

        config.set("test_bool_true", True)
        config.set("test_bool_false", False)

        assert config.get("test_bool_true") is True
        assert config.get("test_bool_false") is False

    def test_config_handles_integer_values(self, temp_config_dir):
        """Test: Integer-Werte werden korrekt gehandhabt"""
        config = TipelsConfig()

        config.set("test_int", 42)

        assert config.get("test_int") == 42
        assert isinstance(config.get("test_int"), int)

    def test_config_handles_dict_values(self, temp_config_dir):
        """Test: Dictionary-Werte werden korrekt gehandhabt"""
        config = TipelsConfig()

        test_dict = {"key1": "value1", "key2": "value2"}
        config.set("test_dict", test_dict)

        retrieved = config.get("test_dict")
        assert retrieved == test_dict
        assert isinstance(retrieved, dict)

    # TODO: Test für System-Config vs User-Config
    # TODO: Test für Config-Migration
