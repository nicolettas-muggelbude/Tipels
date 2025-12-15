"""
Tipels - Brother Scanner-Konfiguration

Verwaltet Brother-Scanner via SANE (brscan4)
"""

import subprocess
import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from tipels.core.logger import TipelsLogger


class ScannerConnectionType(Enum):
    """Scanner-Verbindungstyp"""

    USB = "usb"
    NETWORK = "network"


@dataclass
class ScannerConfig:
    """Scanner-Konfiguration"""

    name: str  # Name im System (z.B. "Brother_MFC-L2700DN")
    model: str  # Modell (z.B. "MFC-L2700DN")
    connection_type: ScannerConnectionType
    device_node: Optional[str] = None  # USB: /dev/usb/lp0
    ip_address: Optional[str] = None  # Netzwerk: 192.168.1.100


class ScannerConfigurationError(Exception):
    """Fehler bei Scanner-Konfiguration"""

    pass


class BrotherScannerManager:
    """Verwaltet Brother-Scanner via SANE (brscan4)"""

    def __init__(self, logger: Optional[TipelsLogger] = None):
        """
        Initialisiert den Scanner-Manager

        Args:
            logger: Logger-Instanz (optional)
        """
        self.logger = logger or TipelsLogger("tipels.scanner")

    def is_brscan4_installed(self) -> bool:
        """
        Prüft ob brscan4 installiert ist

        Returns:
            bool: True wenn brscan4 verfügbar
        """
        try:
            result = subprocess.run(
                ["which", "brsaneconfig4"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def add_scanner(
        self,
        name: str,
        model: str,
        connection_type: ScannerConnectionType,
        device_node: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> bool:
        """
        Registriert einen Scanner in SANE

        Args:
            name: Scanner-Name im System
            model: Brother-Modell (z.B. "MFC-L2700DN")
            connection_type: USB oder Netzwerk
            device_node: USB-Device-Node (nur bei USB)
            ip_address: IP-Adresse (nur bei Netzwerk)

        Returns:
            bool: True bei Erfolg

        Raises:
            ScannerConfigurationError: Bei Konfigurationsfehler
        """
        if not self.is_brscan4_installed():
            error_msg = "brscan4 ist nicht installiert. Bitte zuerst installieren."
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)

        self.logger.info(f"Registriere Scanner: {name} ({model}, {connection_type.value})")

        # Baue brsaneconfig4-Befehl
        cmd = ["brsaneconfig4", "-a", f"name={name}", f"model={model}"]

        if connection_type == ScannerConnectionType.USB:
            if not device_node:
                error_msg = "USB-Verbindung benötigt device_node"
                self.logger.error(error_msg)
                raise ScannerConfigurationError(error_msg)
            cmd.append(f"nodename={device_node}")
        elif connection_type == ScannerConnectionType.NETWORK:
            if not ip_address:
                error_msg = "Netzwerk-Verbindung benötigt ip_address"
                self.logger.error(error_msg)
                raise ScannerConfigurationError(error_msg)
            cmd.append(f"ip={ip_address}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Scanner '{name}' erfolgreich registriert")
                return True
            else:
                error_msg = f"Scanner-Registrierung fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise ScannerConfigurationError(error_msg)

        except subprocess.TimeoutExpired:
            error_msg = "Scanner-Registrierung Timeout"
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)
        except FileNotFoundError:
            error_msg = "brsaneconfig4 nicht gefunden"
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)

    def remove_scanner(self, name: str) -> bool:
        """
        Entfernt einen Scanner aus SANE

        Args:
            name: Scanner-Name im System

        Returns:
            bool: True bei Erfolg

        Raises:
            ScannerConfigurationError: Bei Fehler
        """
        if not self.is_brscan4_installed():
            error_msg = "brscan4 ist nicht installiert"
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)

        self.logger.info(f"Entferne Scanner: {name}")

        cmd = ["brsaneconfig4", "-r", name]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Scanner '{name}' erfolgreich entfernt")
                return True
            else:
                error_msg = f"Scanner-Entfernung fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise ScannerConfigurationError(error_msg)

        except subprocess.TimeoutExpired:
            error_msg = "Scanner-Entfernung Timeout"
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)

    def list_scanners(self) -> List[Dict[str, str]]:
        """
        Listet alle registrierten Scanner auf

        Returns:
            List[Dict]: Liste der Scanner mit Name, Modell, etc.
        """
        if not self.is_brscan4_installed():
            self.logger.warning("brscan4 ist nicht installiert")
            return []

        self.logger.debug("Liste registrierte Scanner auf...")

        cmd = ["brsaneconfig4", "-q"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                self.logger.warning(f"brsaneconfig4 -q fehlgeschlagen: {result.stderr}")
                return []

            # Parse Ausgabe
            # Format: "  0 Brother_MFC-L2700DN         "MFC-L2700DN"         I:192.168.1.100"
            scanners = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or line.startswith("No"):
                    continue

                # Regex für die Ausgabe
                # Beispiel: "  0 Brother_MFC-L2700DN         "MFC-L2700DN"         I:192.168.1.100"
                match = re.match(
                    r'\s*(\d+)\s+(\S+)\s+"([^"]+)"\s+(.+)',
                    line,
                )
                if match:
                    index, name, model, connection = match.groups()
                    scanner_info = {
                        "index": index,
                        "name": name,
                        "model": model,
                        "connection": connection.strip(),
                    }
                    scanners.append(scanner_info)

            self.logger.info(f"{len(scanners)} Scanner gefunden")
            return scanners

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Fehler bei Scanner-Auflistung: {e}")
            return []

    def test_scan(
        self, scanner_name: Optional[str] = None, output_file: str = "/tmp/test_scan.pnm"
    ) -> bool:
        """
        Führt einen Test-Scan durch

        Args:
            scanner_name: Scanner-Name (optional, nutzt ersten verfügbaren)
            output_file: Ausgabedatei für Scan

        Returns:
            bool: True bei Erfolg

        Raises:
            ScannerConfigurationError: Bei Scan-Fehler
        """
        self.logger.info(f"Führe Test-Scan durch (Scanner: {scanner_name or 'auto'})...")

        # Baue scanimage-Befehl
        cmd = ["scanimage"]
        if scanner_name:
            cmd.extend(["--device-name", f"brother4:{scanner_name}"])

        cmd.extend(["--format", "pnm", "--output-file", output_file])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # Scan kann dauern
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Test-Scan erfolgreich: {output_file}")
                return True
            else:
                error_msg = f"Test-Scan fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise ScannerConfigurationError(error_msg)

        except subprocess.TimeoutExpired:
            error_msg = "Test-Scan Timeout (>60s)"
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)
        except FileNotFoundError:
            error_msg = "scanimage nicht gefunden. SANE installiert?"
            self.logger.error(error_msg)
            raise ScannerConfigurationError(error_msg)

    def get_scanner_status(self) -> Dict[str, bool]:
        """
        Prüft Scanner-Status und Systemvoraussetzungen

        Returns:
            Dict: Status-Informationen
        """
        status = {
            "brscan4_installed": self.is_brscan4_installed(),
            "sane_available": self._is_sane_available(),
            "scanner_group_exists": self._check_group_exists("scanner"),
            "saned_group_exists": self._check_group_exists("saned"),
        }

        self.logger.debug(f"Scanner-Status: {status}")
        return status

    def _is_sane_available(self) -> bool:
        """Prüft ob SANE (scanimage) verfügbar ist"""
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

    def add_user_to_groups(
        self, username: Optional[str] = None, use_sudo: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Fügt Benutzer zu Scanner-Gruppen hinzu

        Args:
            username: Benutzername (None = aktueller User)
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            Tuple[bool, List[str]]: (Erfolg, Liste hinzugefügter Gruppen)

        Raises:
            ScannerConfigurationError: Bei Fehler
        """
        # Aktueller User wenn nicht angegeben
        if not username:
            import getpass

            username = getpass.getuser()

        self.logger.info(f"Füge Benutzer '{username}' zu Scanner-Gruppen hinzu...")

        # Gruppen die hinzugefügt werden sollen
        groups_to_add = ["scanner", "saned", "lp"]
        added_groups = []

        for group in groups_to_add:
            # Prüfe ob Gruppe existiert
            if not self._check_group_exists(group):
                self.logger.warning(f"Gruppe '{group}' existiert nicht, überspringe")
                continue

            # Füge User zu Gruppe hinzu
            cmd = ["usermod", "-aG", group, username]
            if use_sudo:
                cmd = ["sudo"] + cmd

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )

                if result.returncode == 0:
                    self.logger.info(f"Benutzer '{username}' zu Gruppe '{group}' hinzugefügt")
                    added_groups.append(group)
                else:
                    self.logger.warning(f"Fehler beim Hinzufügen zu '{group}': {result.stderr}")

            except subprocess.TimeoutExpired:
                self.logger.error(f"Timeout beim Hinzufügen zu Gruppe '{group}'")

        if added_groups:
            self.logger.info(
                f"Benutzer '{username}' zu {len(added_groups)} Gruppen hinzugefügt. "
                "WICHTIG: Neuanmeldung erforderlich für Gruppenänderungen!"
            )

        return len(added_groups) > 0, added_groups
