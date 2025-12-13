"""
Tipels - Foomatic-DB Integration

Nutzt die Foomatic-Datenbank für automatische Treiber-Erkennung
"""

import subprocess
import re
from typing import Optional, List, Dict
from dataclasses import dataclass

from tipels.core.logger import TipelsLogger


@dataclass
class FoomaticDriver:
    """Foomatic-Treiber-Info"""

    ppd_name: str  # z.B. "brother-mfc-l2700dn-brlaser.ppd"
    driver: str  # z.B. "brlaser"
    manufacturer: str  # z.B. "Brother"
    model: str  # z.B. "MFC-L2700DN"
    description: str  # z.B. "Brother MFC-L2700DN Foomatic/brlaser"


class FoomaticDetector:
    """Foomatic-DB Integration für Treiber-Erkennung"""

    def __init__(self, logger: Optional[TipelsLogger] = None):
        """
        Initialisiert den Foomatic-Detector

        Args:
            logger: Logger-Instanz (optional)
        """
        self.logger = logger or TipelsLogger("tipels.foomatic")
        self._ppd_cache: Optional[List[str]] = None

    def is_foomatic_available(self) -> bool:
        """
        Prüft ob Foomatic-DB auf dem System verfügbar ist

        Returns:
            bool: True wenn verfügbar
        """
        try:
            result = subprocess.run(
                ["lpinfo", "-m"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            self.logger.warning("lpinfo nicht gefunden. CUPS nicht installiert?")
            return False
        except subprocess.TimeoutExpired:
            self.logger.warning("lpinfo Timeout")
            return False

    def get_all_ppd_files(self, force_refresh: bool = False) -> List[str]:
        """
        Gibt alle verfügbaren PPD-Dateien zurück

        Args:
            force_refresh: Cache ignorieren und neu laden

        Returns:
            List[str]: Liste der PPD-Dateien
        """
        if self._ppd_cache is not None and not force_refresh:
            return self._ppd_cache

        self.logger.info("Lade PPD-Liste von lpinfo...")

        try:
            result = subprocess.run(
                ["lpinfo", "-m"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                # Parse Ausgabe: "drv:///sample.drv/generic.ppd Generic PCL Laser Printer"
                ppd_list = []
                for line in result.stdout.split("\n"):
                    if line.strip():
                        ppd_list.append(line.strip())

                self._ppd_cache = ppd_list
                self.logger.info(f"{len(ppd_list)} PPD-Dateien gefunden")
                return ppd_list

            self.logger.warning(f"lpinfo fehlgeschlagen: {result.stderr}")
            return []

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Fehler bei lpinfo: {e}")
            return []

    def find_drivers_for_printer(
        self, manufacturer: str, model: str
    ) -> List[FoomaticDriver]:
        """
        Findet alle verfügbaren Treiber für ein Drucker-Modell

        Args:
            manufacturer: Hersteller (z.B. "Brother")
            model: Modell (z.B. "MFC-L2700DN")

        Returns:
            List[FoomaticDriver]: Liste gefundener Treiber
        """
        self.logger.info(f"Suche Treiber für {manufacturer} {model}...")

        ppd_list = self.get_all_ppd_files()
        if not ppd_list:
            return []

        # Bereinige Modellname für Suche
        model_lower = model.lower()
        manufacturer_clean = manufacturer.lower()

        found_drivers = []

        for ppd_line in ppd_list:
            # PPD-Line Format: "ppd_file description"
            parts = ppd_line.split(maxsplit=1)
            if len(parts) < 2:
                continue

            ppd_file = parts[0]
            description = parts[1]

            # Prüfe ob Hersteller und Modell im PPD-Namen oder Description
            ppd_lower = ppd_file.lower()
            desc_lower = description.lower()

            # Bereinige PPD und Description für Vergleich (entferne Sonderzeichen)
            ppd_clean = ppd_lower.replace("-", "").replace("_", "").replace(" ", "")
            desc_clean = desc_lower.replace("-", "").replace("_", "").replace(" ", "")

            if manufacturer_clean in ppd_lower or manufacturer_clean in desc_lower:
                # Hersteller gefunden, prüfe Modell
                match_found = False

                # Zerlege Modellname in Teile (z.B. "LaserJet Pro M404dn" → ["laserjet", "pro", "m404dn"])
                model_parts = model_lower.replace("-", " ").replace("_", " ").split()
                if not model_parts:
                    model_parts = [model_lower]

                # Ganzer Modellname matched (bereinigt) - höchste Priorität
                model_clean = model_lower.replace("-", "").replace("_", "").replace(" ", "")
                if model_clean in ppd_clean or model_clean in desc_clean:
                    match_found = True
                else:
                    # Sonst: Mindestens 50% der signifikanten Teile müssen matchen
                    # Filtere kurze/generische Teile raus (< 4 Zeichen)
                    significant_parts = [p for p in model_parts if len(p) >= 4]

                    if significant_parts:
                        matched_parts = 0
                        for part in significant_parts:
                            if part in ppd_clean or part in desc_clean:
                                matched_parts += 1

                        # Mindestens 50% der signifikanten Teile müssen matchen
                        if matched_parts >= len(significant_parts) * 0.5:
                            match_found = True
                    else:
                        # Fallback: Wenn alle Teile kurz sind, reicht ein Match
                        for part in model_parts:
                            if len(part) >= 3 and (part in ppd_clean or part in desc_clean):
                                match_found = True
                                break

                if match_found:
                    # Extrahiere Treiber-Name
                    driver = self._extract_driver_name(ppd_file, description)

                    foomatic_driver = FoomaticDriver(
                        ppd_name=ppd_file,
                        driver=driver,
                        manufacturer=manufacturer,
                        model=model,
                        description=description,
                    )

                    found_drivers.append(foomatic_driver)

        self.logger.info(f"{len(found_drivers)} Treiber für {manufacturer} {model} gefunden")
        return found_drivers

    def _extract_driver_name(self, ppd_file: str, description: str) -> str:
        """
        Extrahiert den Treiber-Namen aus PPD-File oder Description

        Args:
            ppd_file: PPD-Dateiname
            description: Beschreibung

        Returns:
            str: Treiber-Name
        """
        # Pattern 1: "Foomatic/brlaser" in Description (höchste Priorität)
        match = re.search(r"foomatic/(\w+)", description, re.IGNORECASE)
        if match:
            return match.group(1)

        # Pattern 2: brother-mfc-l2700dn-brlaser.ppd → brlaser
        match = re.search(r"-(\w+)\.ppd", ppd_file)
        if match:
            return match.group(1)

        # Pattern 3: Aus PPD-File extrahieren (letzter Teil vor .ppd)
        if ppd_file.endswith(".ppd"):
            parts = ppd_file.replace(".ppd", "").split("-")
            if parts:
                return parts[-1]

        return "unknown"

    def get_recommended_driver(
        self, manufacturer: str, model: str
    ) -> Optional[FoomaticDriver]:
        """
        Gibt den empfohlenen Treiber für ein Drucker-Modell zurück

        Args:
            manufacturer: Hersteller
            model: Modell

        Returns:
            Optional[FoomaticDriver]: Empfohlener Treiber oder None
        """
        drivers = self.find_drivers_for_printer(manufacturer, model)
        if not drivers:
            return None

        # Bevorzuge Open-Source-Treiber
        # Priorität: brlaser > hplip > gutenprint > generic
        priority = {
            "brlaser": 10,
            "hplip": 9,
            "gutenprint": 8,
            "postscript": 7,
            "pxlmono": 6,
        }

        # Sortiere nach Priorität
        drivers_sorted = sorted(
            drivers,
            key=lambda d: priority.get(d.driver.lower(), 0),
            reverse=True,
        )

        recommended = drivers_sorted[0]
        self.logger.info(
            f"Empfohlener Treiber für {manufacturer} {model}: {recommended.driver}"
        )
        return recommended

    def get_ppd_file_path(self, ppd_name: str) -> Optional[str]:
        """
        Gibt den vollständigen Pfad zu einer PPD-Datei zurück

        Args:
            ppd_name: PPD-Dateiname (z.B. "brother-mfc-l2700dn-brlaser.ppd")

        Returns:
            Optional[str]: Vollständiger Pfad oder None
        """
        # PPD-Dateien sind typischerweise in /usr/share/ppd/
        # oder werden von lpinfo dynamisch generiert
        # Für CUPS-Installation brauchen wir nur den PPD-Namen
        return ppd_name
