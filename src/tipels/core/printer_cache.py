"""
Tipels - Drucker-Cache

Speichert erkannte Drucker und ihre Treiber für schnellen Zugriff
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from tipels.core.logger import TipelsLogger


class PrinterCache:
    """Cache für erkannte Drucker und Treiber"""

    def __init__(
        self,
        cache_file: Optional[Path] = None,
        logger: Optional[TipelsLogger] = None,
    ):
        """
        Initialisiert den Drucker-Cache

        Args:
            cache_file: Pfad zur Cache-Datei (optional)
            logger: Logger-Instanz (optional)
        """
        self.logger = logger or TipelsLogger("tipels.cache")

        if cache_file is None:
            cache_dir = Path.home() / ".local" / "share" / "tipels"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / "printer_cache.json"

        self.cache_file = cache_file
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        """Lädt den Cache von Datei"""
        if not self.cache_file.exists():
            self.logger.info("Cache-Datei existiert nicht, erstelle neue")
            self._cache = {}
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
            self.logger.info(f"Cache geladen: {len(self._cache)} Einträge")
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Fehler beim Laden des Cache: {e}")
            self._cache = {}

    def _save_cache(self):
        """Speichert den Cache in Datei"""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Cache gespeichert: {len(self._cache)} Einträge")
        except OSError as e:
            self.logger.error(f"Fehler beim Speichern des Cache: {e}")

    def _make_key(self, manufacturer: str, model: str) -> str:
        """
        Erstellt einen eindeutigen Schlüssel für einen Drucker

        Args:
            manufacturer: Hersteller
            model: Modell

        Returns:
            str: Cache-Schlüssel
        """
        return f"{manufacturer}:{model}".lower()

    def get(self, manufacturer: str, model: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Cache-Eintrag für einen Drucker zurück

        Args:
            manufacturer: Hersteller
            model: Modell

        Returns:
            Optional[Dict]: Cache-Eintrag oder None
        """
        key = self._make_key(manufacturer, model)
        entry = self._cache.get(key)

        if entry:
            self.logger.debug(f"Cache-Hit für {manufacturer} {model}")
        else:
            self.logger.debug(f"Cache-Miss für {manufacturer} {model}")

        return entry

    def set(
        self,
        manufacturer: str,
        model: str,
        openprinting_driver: Optional[str] = None,
        official_driver: Optional[str] = None,
        last_used: Optional[str] = None,
        ppd_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Speichert einen Drucker im Cache

        Args:
            manufacturer: Hersteller
            model: Modell
            openprinting_driver: OpenPrinting-Treiber (z.B. "brlaser")
            official_driver: Official-Treiber (z.B. "brother-lpr")
            last_used: Zuletzt verwendeter Treiber
            ppd_name: PPD-Dateiname
            **kwargs: Weitere Metadaten
        """
        key = self._make_key(manufacturer, model)

        entry = {
            "manufacturer": manufacturer,
            "model": model,
            "openprinting_driver": openprinting_driver,
            "official_driver": official_driver,
            "last_used": last_used or openprinting_driver,
            "ppd_name": ppd_name,
            "last_updated": datetime.now().isoformat(),
            **kwargs,
        }

        self._cache[key] = entry
        self._save_cache()

        self.logger.info(f"Cache aktualisiert für {manufacturer} {model}")

    def update(self, manufacturer: str, model: str, **updates):
        """
        Aktualisiert einen Cache-Eintrag

        Args:
            manufacturer: Hersteller
            model: Modell
            **updates: Zu aktualisierende Felder
        """
        key = self._make_key(manufacturer, model)
        entry = self._cache.get(key, {})

        entry.update(updates)
        entry["last_updated"] = datetime.now().isoformat()

        self._cache[key] = entry
        self._save_cache()

        self.logger.debug(f"Cache-Eintrag aktualisiert: {manufacturer} {model}")

    def delete(self, manufacturer: str, model: str) -> bool:
        """
        Löscht einen Cache-Eintrag

        Args:
            manufacturer: Hersteller
            model: Modell

        Returns:
            bool: True wenn gelöscht, False wenn nicht vorhanden
        """
        key = self._make_key(manufacturer, model)

        if key in self._cache:
            del self._cache[key]
            self._save_cache()
            self.logger.info(f"Cache-Eintrag gelöscht: {manufacturer} {model}")
            return True

        return False

    def clear(self):
        """Löscht den gesamten Cache"""
        self._cache = {}
        self._save_cache()
        self.logger.info("Cache komplett gelöscht")

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Gibt alle Cache-Einträge zurück

        Returns:
            Dict: Alle Cache-Einträge
        """
        return self._cache.copy()

    def count(self) -> int:
        """
        Gibt die Anzahl der Cache-Einträge zurück

        Returns:
            int: Anzahl Einträge
        """
        return len(self._cache)
