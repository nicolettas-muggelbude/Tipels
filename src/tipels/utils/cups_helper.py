"""
Tipels - CUPS Helper

Wrapper für CUPS (Common UNIX Printing System) Operationen
"""

import subprocess
import re
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from tipels.core.logger import TipelsLogger


class PrinterState(Enum):
    """Drucker-Status"""

    IDLE = "idle"
    PRINTING = "printing"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class ConnectionType(Enum):
    """Drucker-Verbindungstyp"""

    USB = "usb"
    NETWORK_IPP = "ipp"
    NETWORK_SOCKET = "socket"
    NETWORK_LPD = "lpd"


@dataclass
class PrinterInfo:
    """Drucker-Informationen"""

    name: str
    uri: str
    state: PrinterState
    state_message: Optional[str] = None
    location: Optional[str] = None
    make_model: Optional[str] = None
    jobs: int = 0


class CupsError(Exception):
    """Fehler bei CUPS-Operationen"""

    pass


class CupsHelper:
    """Helper für CUPS-Operationen"""

    def __init__(self, logger: Optional[TipelsLogger] = None):
        """
        Initialisiert den CUPS-Helper

        Args:
            logger: Logger-Instanz (optional)
        """
        self.logger = logger or TipelsLogger("tipels.cups")

    def is_cups_available(self) -> bool:
        """
        Prüft ob CUPS verfügbar ist

        Returns:
            bool: True wenn CUPS läuft
        """
        try:
            result = subprocess.run(
                ["lpstat", "-r"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            # lpstat -r gibt "scheduler is running" zurück wenn CUPS läuft
            return result.returncode == 0 and "running" in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def list_printers(self) -> List[PrinterInfo]:
        """
        Listet alle installierten CUPS-Drucker auf

        Returns:
            List[PrinterInfo]: Liste der Drucker

        Raises:
            CupsError: Bei CUPS-Fehler
        """
        if not self.is_cups_available():
            raise CupsError("CUPS ist nicht verfügbar oder läuft nicht")

        self.logger.info("Liste CUPS-Drucker auf...")

        try:
            # lpstat -p gibt Status aller Drucker
            result = subprocess.run(
                ["lpstat", "-p"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0 and result.stderr:
                raise CupsError(f"lpstat fehlgeschlagen: {result.stderr}")

            printers = []
            for line in result.stdout.split("\n"):
                if not line.strip() or not line.startswith("printer"):
                    continue

                # Parse: "printer Brother_MFC-L2700DN is idle.  enabled since ..."
                match = re.match(r"printer\s+(\S+)\s+is\s+(\w+)", line)
                if match:
                    name = match.group(1)
                    state_str = match.group(2)

                    # Mappe Status
                    state = PrinterState.IDLE
                    if "printing" in state_str.lower():
                        state = PrinterState.PRINTING
                    elif "stopped" in state_str.lower():
                        state = PrinterState.STOPPED

                    # Hole zusätzliche Infos
                    uri = self._get_printer_uri(name)
                    location = self._get_printer_attribute(name, "printer-location")
                    make_model = self._get_printer_attribute(name, "printer-make-and-model")
                    jobs = self._get_printer_jobs(name)

                    printer_info = PrinterInfo(
                        name=name,
                        uri=uri or "",
                        state=state,
                        state_message=state_str,
                        location=location,
                        make_model=make_model,
                        jobs=jobs,
                    )
                    printers.append(printer_info)

            self.logger.info(f"{len(printers)} Drucker gefunden")
            return printers

        except subprocess.TimeoutExpired:
            raise CupsError("Timeout bei lpstat")
        except Exception as e:
            raise CupsError(f"Fehler beim Auflisten der Drucker: {e}")

    def add_printer(
        self,
        name: str,
        uri: str,
        ppd_file: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        use_sudo: bool = True,
    ) -> bool:
        """
        Fügt einen Drucker zu CUPS hinzu

        Args:
            name: Drucker-Name im System
            uri: Device-URI (usb://..., ipp://..., socket://...)
            ppd_file: PPD-Datei (optional, z.B. für Foomatic)
            location: Standort (optional)
            description: Beschreibung (optional)
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            bool: True bei Erfolg

        Raises:
            CupsError: Bei CUPS-Fehler
        """
        if not self.is_cups_available():
            raise CupsError("CUPS ist nicht verfügbar")

        self.logger.info(f"Füge Drucker '{name}' zu CUPS hinzu (URI: {uri})...")

        # Baue lpadmin-Befehl
        cmd = ["lpadmin", "-p", name, "-E", "-v", uri]

        if ppd_file:
            cmd.extend(["-m", ppd_file])

        if location:
            cmd.extend(["-L", location])

        if description:
            cmd.extend(["-D", description])

        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Drucker '{name}' erfolgreich zu CUPS hinzugefügt")
                return True
            else:
                error_msg = f"lpadmin fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise CupsError(error_msg)

        except subprocess.TimeoutExpired:
            raise CupsError("Timeout bei lpadmin")
        except FileNotFoundError:
            raise CupsError("lpadmin nicht gefunden. CUPS installiert?")

    def remove_printer(self, name: str, use_sudo: bool = True) -> bool:
        """
        Entfernt einen Drucker aus CUPS

        Args:
            name: Drucker-Name
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            bool: True bei Erfolg

        Raises:
            CupsError: Bei CUPS-Fehler
        """
        if not self.is_cups_available():
            raise CupsError("CUPS ist nicht verfügbar")

        self.logger.info(f"Entferne Drucker '{name}' aus CUPS...")

        cmd = ["lpadmin", "-x", name]
        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Drucker '{name}' erfolgreich entfernt")
                return True
            else:
                error_msg = f"lpadmin -x fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise CupsError(error_msg)

        except subprocess.TimeoutExpired:
            raise CupsError("Timeout bei lpadmin -x")

    def test_print(self, printer_name: str, test_file: Optional[str] = None) -> bool:
        """
        Führt einen Testdruck durch

        Args:
            printer_name: Drucker-Name
            test_file: Test-Datei (optional, default: CUPS-Testseite)

        Returns:
            bool: True bei Erfolg

        Raises:
            CupsError: Bei Druck-Fehler
        """
        if not self.is_cups_available():
            raise CupsError("CUPS ist nicht verfügbar")

        # Standard CUPS-Testseite
        if not test_file:
            test_file = "/usr/share/cups/data/testprint"
            if not Path(test_file).exists():
                # Fallback: PostScript-Testseite
                test_file = "/usr/share/cups/data/testprint.ps"

        if not Path(test_file).exists():
            raise CupsError(f"Test-Datei nicht gefunden: {test_file}")

        self.logger.info(f"Starte Testdruck auf '{printer_name}'...")

        cmd = ["lp", "-d", printer_name, test_file]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Testdruck erfolgreich gestartet: {result.stdout}")
                return True
            else:
                error_msg = f"Testdruck fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise CupsError(error_msg)

        except subprocess.TimeoutExpired:
            raise CupsError("Timeout bei Testdruck")

    def get_printer_status(self, printer_name: str) -> Dict[str, str]:
        """
        Gibt detaillierten Status eines Druckers zurück

        Args:
            printer_name: Drucker-Name

        Returns:
            Dict: Status-Informationen

        Raises:
            CupsError: Bei CUPS-Fehler
        """
        if not self.is_cups_available():
            raise CupsError("CUPS ist nicht verfügbar")

        self.logger.debug(f"Hole Status für Drucker '{printer_name}'...")

        try:
            result = subprocess.run(
                ["lpstat", "-p", printer_name, "-l"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                raise CupsError(f"lpstat fehlgeschlagen: {result.stderr}")

            # Parse Ausgabe
            status = {"name": printer_name, "raw_output": result.stdout}

            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line:
                    continue

                # Parse verschiedene Attribute
                if line.startswith("printer"):
                    match = re.search(r"is\s+(\w+)", line)
                    if match:
                        status["state"] = match.group(1)
                elif "Description:" in line:
                    status["description"] = line.split("Description:", 1)[1].strip()
                elif "Location:" in line:
                    status["location"] = line.split("Location:", 1)[1].strip()
                elif "Interface:" in line:
                    status["ppd"] = line.split("Interface:", 1)[1].strip()

            return status

        except subprocess.TimeoutExpired:
            raise CupsError("Timeout bei lpstat")

    def get_ppd_file(self, model_search: str) -> Optional[str]:
        """
        Sucht passende PPD-Datei für ein Modell

        Args:
            model_search: Modell-Suchbegriff (z.B. "Brother MFC-L2700DN")

        Returns:
            Optional[str]: PPD-Dateiname oder None

        Raises:
            CupsError: Bei CUPS-Fehler
        """
        if not self.is_cups_available():
            raise CupsError("CUPS ist nicht verfügbar")

        self.logger.info(f"Suche PPD-Datei für '{model_search}'...")

        try:
            result = subprocess.run(
                ["lpinfo", "-m"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode != 0:
                raise CupsError(f"lpinfo -m fehlgeschlagen: {result.stderr}")

            # Durchsuche PPD-Liste
            model_lower = model_search.lower()
            for line in result.stdout.split("\n"):
                if model_lower in line.lower():
                    # Format: "ppd_file description"
                    parts = line.split(maxsplit=1)
                    if parts:
                        ppd_file = parts[0]
                        self.logger.info(f"PPD gefunden: {ppd_file}")
                        return ppd_file

            self.logger.warning(f"Keine PPD für '{model_search}' gefunden")
            return None

        except subprocess.TimeoutExpired:
            raise CupsError("Timeout bei lpinfo -m")

    def _get_printer_uri(self, printer_name: str) -> Optional[str]:
        """Gibt Device-URI eines Druckers zurück"""
        try:
            result = subprocess.run(
                ["lpstat", "-v", printer_name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                # Parse: "device for Brother_MFC-L2700DN: usb://..."
                match = re.search(r"device for \S+:\s+(\S+)", result.stdout)
                if match:
                    return match.group(1)

            return None
        except (subprocess.TimeoutExpired, Exception):
            return None

    def _get_printer_attribute(self, printer_name: str, attribute: str) -> Optional[str]:
        """Gibt ein spezifisches Drucker-Attribut zurück"""
        try:
            result = subprocess.run(
                ["lpoptions", "-p", printer_name, "-l"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                # Suche Attribut in Ausgabe
                for line in result.stdout.split("\n"):
                    if attribute in line.lower():
                        return line.strip()

            return None
        except (subprocess.TimeoutExpired, Exception):
            return None

    def _get_printer_jobs(self, printer_name: str) -> int:
        """Gibt Anzahl der Jobs für einen Drucker zurück"""
        try:
            result = subprocess.run(
                ["lpstat", "-o", printer_name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                # Zähle Zeilen (jede Zeile = ein Job)
                jobs = len(
                    [
                        line
                        for line in result.stdout.split("\n")
                        if line.strip() and printer_name in line
                    ]
                )
                return jobs

            return 0
        except (subprocess.TimeoutExpired, Exception):
            return 0
