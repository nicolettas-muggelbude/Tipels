"""
Tipels - Konfigurationsverwaltung

Verwaltung von System- und User-Konfigurationen
"""

import json
from pathlib import Path
from typing import Any, Dict


class TipelsConfig:
    """Verwaltung von Konfigurationsdateien"""

    DEFAULT_CONFIG = {
        "version": "1.0",
        "language": "de",
        "auto_detect": True,
        "prefer_opensource_drivers": False,
        "notification_enabled": True,
        "debug_mode": False,
        "backup_path": str(Path.home() / "tipels-backups"),
    }

    def __init__(self):
        """Initialisiert die Konfiguration"""
        self.system_config_dir = Path("/etc/tipels")
        self.user_config_dir = Path.home() / ".config" / "tipels"
        self.user_config_file = self.user_config_dir / "tipels.conf"

        # Verzeichnisse erstellen
        self.user_config_dir.mkdir(parents=True, exist_ok=True)

        # Konfiguration laden
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Lädt Konfiguration (User > System > Default)

        Returns:
            dict: Geladene Konfiguration
        """
        config = self.DEFAULT_CONFIG.copy()

        # System-Config laden (falls vorhanden)
        system_config_file = self.system_config_dir / "tipels.conf"
        if system_config_file.exists():
            try:
                with open(system_config_file, "r", encoding="utf-8") as f:
                    system_config = json.load(f)
                    config.update(system_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warnung: Fehler beim Laden der System-Config: {e}")

        # User-Config laden (falls vorhanden)
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warnung: Fehler beim Laden der User-Config: {e}")

        return config

    def save_config(self):
        """Speichert die User-Konfiguration"""
        try:
            with open(self.user_config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Konfigurationswert

        Args:
            key: Konfigurationsschlüssel
            default: Standardwert falls Schlüssel nicht existiert

        Returns:
            Konfigurationswert
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """
        Setzt einen Konfigurationswert

        Args:
            key: Konfigurationsschlüssel
            value: Wert
        """
        self.config[key] = value
        self.save_config()

    # TODO: Migrations-Logik für Updates implementieren
    def migrate_config(self, old_version: str, new_version: str):
        """
        Migriert Konfiguration zwischen Versionen

        Args:
            old_version: Alte Version
            new_version: Neue Version
        """
        # TODO: Implementierung
        pass
