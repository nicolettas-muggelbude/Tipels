"""
Tipels - SANE Helper

Wrapper für SANE (Scanner Access Now Easy) Operationen
"""

import subprocess
import re
from typing import Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from tipels.core.logger import TipelsLogger


class ScannerState(Enum):
    """Scanner-Status"""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ScanFormat(Enum):
    """Scan-Ausgabeformat"""

    PNM = "pnm"
    TIFF = "tiff"
    PNG = "png"
    JPEG = "jpeg"


@dataclass
class ScannerInfo:
    """Scanner-Informationen"""

    device_name: str  # z.B. "brother4:Brother_MFC-L2700DN"
    vendor: Optional[str] = None  # z.B. "Brother"
    model: Optional[str] = None  # z.B. "MFC-L2700DN"
    scanner_type: Optional[str] = None  # z.B. "flatbed scanner"
    backend: Optional[str] = None  # z.B. "brother4"
    state: ScannerState = ScannerState.UNKNOWN


class SaneError(Exception):
    """Fehler bei SANE-Operationen"""

    pass


class SaneHelper:
    """Helper für SANE-Operationen"""

    def __init__(self, logger: Optional[TipelsLogger] = None):
        """
        Initialisiert den SANE-Helper

        Args:
            logger: Logger-Instanz (optional)
        """
        self.logger = logger or TipelsLogger("tipels.sane")

    def is_sane_available(self) -> bool:
        """
        Prüft ob SANE verfügbar ist

        Returns:
            bool: True wenn SANE installiert ist
        """
        try:
            result = subprocess.run(
                ["which", "scanimage"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def list_scanners(self) -> List[ScannerInfo]:
        """
        Listet alle verfügbaren SANE-Scanner auf

        Returns:
            List[ScannerInfo]: Liste der Scanner

        Raises:
            SaneError: Bei SANE-Fehler
        """
        if not self.is_sane_available():
            raise SaneError("SANE ist nicht installiert")

        self.logger.info("Liste SANE-Scanner auf...")

        try:
            # scanimage -L listet alle verfügbaren Scanner auf
            result = subprocess.run(
                ["scanimage", "-L"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode != 0 and result.stderr:
                # SANE gibt manchmal Warnungen aus, auch bei Erfolg
                if "No scanners were identified" in result.stdout:
                    self.logger.info("Keine Scanner gefunden")
                    return []
                # Nur bei echten Fehlern
                if result.returncode != 0:
                    raise SaneError(f"scanimage -L fehlgeschlagen: {result.stderr}")

            scanners = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or "No scanners" in line:
                    continue

                # Parse Zeile
                # Format: "device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner"
                scanner_info = self._parse_scanner_line(line)
                if scanner_info:
                    scanners.append(scanner_info)

            self.logger.info(f"{len(scanners)} Scanner gefunden")
            return scanners

        except subprocess.TimeoutExpired:
            raise SaneError("Timeout bei scanimage -L")
        except Exception as e:
            raise SaneError(f"Fehler beim Auflisten der Scanner: {e}")

    def get_scanner_info(self, device_name: str) -> Optional[ScannerInfo]:
        """
        Gibt Informationen über einen spezifischen Scanner zurück

        Args:
            device_name: Scanner-Device-Name (z.B. "brother4:Brother_MFC-L2700DN")

        Returns:
            Optional[ScannerInfo]: Scanner-Informationen oder None
        """
        scanners = self.list_scanners()
        for scanner in scanners:
            if scanner.device_name == device_name:
                return scanner
        return None

    def test_scan(
        self,
        device_name: Optional[str] = None,
        output_file: Optional[str] = None,
        scan_format: ScanFormat = ScanFormat.PNM,
        resolution: int = 150,
    ) -> bool:
        """
        Führt einen Test-Scan durch

        Args:
            device_name: Scanner-Device-Name (optional, nutzt ersten verfügbaren)
            output_file: Ausgabedatei (optional, Standard: /tmp/tipels_test_scan.<format>)
            scan_format: Ausgabeformat (Standard: PNM)
            resolution: Scan-Auflösung in DPI (Standard: 150)

        Returns:
            bool: True bei Erfolg

        Raises:
            SaneError: Bei Scan-Fehler
        """
        if not self.is_sane_available():
            raise SaneError("SANE ist nicht installiert")

        # Standard-Ausgabedatei
        if not output_file:
            output_file = f"/tmp/tipels_test_scan.{scan_format.value}"

        self.logger.info(
            f"Starte Test-Scan (Device: {device_name or 'auto'}, "
            f"Format: {scan_format.value}, DPI: {resolution})..."
        )

        # Baue scanimage-Befehl
        cmd = ["scanimage"]

        if device_name:
            cmd.extend(["--device-name", device_name])

        cmd.extend(
            [
                "--format",
                scan_format.value,
                "--resolution",
                str(resolution),
                "--output-file",
                output_file,
            ]
        )

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # Scan kann dauern (2 Minuten)
                check=False,
            )

            if result.returncode == 0:
                # Prüfe ob Datei erstellt wurde
                if Path(output_file).exists():
                    file_size = Path(output_file).stat().st_size
                    self.logger.info(
                        f"Test-Scan erfolgreich: {output_file} ({file_size} Bytes)"
                    )
                    return True
                else:
                    error_msg = f"Scan-Befehl erfolgreich, aber Datei nicht erstellt: {output_file}"
                    self.logger.error(error_msg)
                    raise SaneError(error_msg)
            else:
                error_msg = f"Test-Scan fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise SaneError(error_msg)

        except subprocess.TimeoutExpired:
            raise SaneError("Test-Scan Timeout (>120s)")
        except FileNotFoundError:
            raise SaneError("scanimage nicht gefunden. SANE installiert?")

    def get_scanner_capabilities(self, device_name: str) -> Dict[str, List[str]]:
        """
        Gibt die Fähigkeiten eines Scanners zurück

        Args:
            device_name: Scanner-Device-Name

        Returns:
            Dict: Scanner-Fähigkeiten (Auflösungen, Formate, Modi, etc.)

        Raises:
            SaneError: Bei SANE-Fehler
        """
        if not self.is_sane_available():
            raise SaneError("SANE ist nicht installiert")

        self.logger.debug(f"Hole Fähigkeiten für Scanner '{device_name}'...")

        try:
            # scanimage --help -d <device> gibt alle Optionen
            result = subprocess.run(
                ["scanimage", "--help", "-d", device_name],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode != 0:
                raise SaneError(f"scanimage --help fehlgeschlagen: {result.stderr}")

            capabilities = {
                "resolutions": [],
                "modes": [],
                "sources": [],
                "formats": ["pnm", "tiff", "png", "jpeg"],  # Standard-Formate
            }

            # Parse Ausgabe
            for line in result.stdout.split("\n"):
                line = line.strip()

                # Suche nach Auflösungen
                if "--resolution" in line and "dpi" in line.lower():
                    # Extrahiere Auflösungen
                    resolution_match = re.findall(r"(\d+)(?:\.\.\d+)?dpi", line)
                    if resolution_match:
                        capabilities["resolutions"].extend(resolution_match)

                # Suche nach Modi (Farbe, Graustufen, etc.)
                elif "--mode" in line:
                    # Extrahiere Modi aus Zeilen wie: --mode Color|Gray|Lineart [Gray]
                    # Suche nach Optionen vor den eckigen Klammern
                    mode_match = re.search(r"--mode\s+([^\[]+)", line)
                    if mode_match:
                        modes_str = mode_match.group(1).strip()
                        modes = modes_str.split("|")
                        capabilities["modes"].extend(modes)

                # Suche nach Quellen (Flatbed, ADF, etc.)
                elif "--source" in line:
                    # Extrahiere Quellen aus Zeilen wie: --source Flatbed|ADF [Flatbed]
                    # Suche nach Optionen vor den eckigen Klammern
                    source_match = re.search(r"--source\s+([^\[]+)", line)
                    if source_match:
                        sources_str = source_match.group(1).strip()
                        sources = sources_str.split("|")
                        capabilities["sources"].extend(sources)

            return capabilities

        except subprocess.TimeoutExpired:
            raise SaneError("Timeout bei scanimage --help")

    def get_scanner_status(self) -> Dict[str, bool]:
        """
        Prüft SANE-Status und Systemvoraussetzungen

        Returns:
            Dict: Status-Informationen
        """
        status = {
            "sane_available": self.is_sane_available(),
            "scanners_found": False,
            "scanner_group_exists": self._check_group_exists("scanner"),
            "saned_group_exists": self._check_group_exists("saned"),
        }

        # Prüfe ob Scanner verfügbar sind
        if status["sane_available"]:
            try:
                scanners = self.list_scanners()
                status["scanners_found"] = len(scanners) > 0
            except SaneError:
                pass

        self.logger.debug(f"SANE-Status: {status}")
        return status

    def _parse_scanner_line(self, line: str) -> Optional[ScannerInfo]:
        """
        Parst eine scanimage -L Ausgabezeile

        Args:
            line: Zeile aus scanimage -L

        Returns:
            Optional[ScannerInfo]: Scanner-Info oder None
        """
        # Format: "device `brother4:Brother_MFC-L2700DN' is a Brother MFC-L2700DN flatbed scanner"
        match = re.match(r"device\s+`([^']+)'\s+is\s+a\s+(.+)", line)
        if not match:
            return None

        device_name = match.group(1)
        description = match.group(2)

        # Extrahiere Backend (z.B. "brother4" aus "brother4:Brother_MFC-L2700DN")
        backend = None
        if ":" in device_name:
            backend = device_name.split(":")[0]

        # Parse Beschreibung (z.B. "Brother MFC-L2700DN flatbed scanner")
        # Versuche Hersteller und Modell zu extrahieren
        vendor = None
        model = None
        scanner_type = None

        # Suche nach bekannten Scanner-Typen
        type_keywords = ["flatbed", "sheet-fed", "handheld", "multi-function"]
        for keyword in type_keywords:
            if keyword in description.lower():
                scanner_type = keyword + " scanner"
                break

        # Versuche Hersteller zu extrahieren (erster Teil vor Modell)
        parts = description.split()
        if parts:
            vendor = parts[0]
            # Rest ist vermutlich Modell + Typ
            if len(parts) > 1:
                # Entferne Scanner-Typ-Keywords
                model_parts = []
                for part in parts[1:]:
                    if part.lower() not in type_keywords and part.lower() != "scanner":
                        model_parts.append(part)
                if model_parts:
                    model = " ".join(model_parts)

        return ScannerInfo(
            device_name=device_name,
            vendor=vendor,
            model=model,
            scanner_type=scanner_type,
            backend=backend,
            state=ScannerState.AVAILABLE,
        )

    def _check_group_exists(self, group_name: str) -> bool:
        """Prüft ob eine Gruppe existiert"""
        try:
            result = subprocess.run(
                ["getent", "group", group_name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
