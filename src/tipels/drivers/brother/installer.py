"""
Tipels - Brother Treiber-Installation

Installiert und verwaltet Brother-Drucker- und Scanner-Treiber
"""

import subprocess
import re
from typing import Optional, List, Tuple
from pathlib import Path

from tipels.core.logger import TipelsLogger
from tipels.drivers.brother.driver_db import (
    get_driver_info,
    get_recommended_driver,
    get_scanner_driver,
    DriverInfo,
    DriverSource,
)


class DriverInstallationError(Exception):
    """Fehler bei der Treiber-Installation"""
    pass


class DriverInstaller:
    """Installiert und verwaltet Brother-Treiber"""

    def __init__(self, logger: Optional[TipelsLogger] = None):
        """
        Initialisiert den Driver-Installer

        Args:
            logger: Logger-Instanz (optional)
        """
        self.logger = logger or TipelsLogger("tipels.driver.installer")

    def is_driver_installed(self, package_name: str) -> bool:
        """
        Prüft ob ein Treiber-Paket installiert ist

        Args:
            package_name: Name des Pakets (z.B. "printer-driver-brlaser")

        Returns:
            bool: True wenn installiert
        """
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            # dpkg -l gibt "ii" zurück wenn Paket installiert ist
            if result.returncode == 0 and "ii" in result.stdout:
                self.logger.info(f"Treiber '{package_name}' ist bereits installiert")
                return True

            self.logger.info(f"Treiber '{package_name}' ist nicht installiert")
            return False

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Fehler bei dpkg-Prüfung: {e}")
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """
        Gibt die installierte Version eines Pakets zurück

        Args:
            package_name: Name des Pakets

        Returns:
            Optional[str]: Version oder None
        """
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                # Parse dpkg -l Ausgabe
                # Format: ii  package-name  version  architecture  description
                for line in result.stdout.split("\n"):
                    if line.startswith("ii") and package_name in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]  # Version

            return None

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Fehler bei Version-Abfrage: {e}")
            return None

    def install_from_repository(
        self, package_name: str, use_sudo: bool = True
    ) -> bool:
        """
        Installiert ein Paket aus den Repositories

        Args:
            package_name: Name des Pakets
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            bool: True bei Erfolg

        Raises:
            DriverInstallationError: Bei Installationsfehler
        """
        self.logger.info(f"Installiere Treiber '{package_name}' aus Repository...")

        # Prüfe ob bereits installiert
        if self.is_driver_installed(package_name):
            self.logger.info(f"Treiber '{package_name}' ist bereits installiert")
            return True

        # apt-get install ausführen
        cmd = ["apt-get", "install", "-y", package_name]
        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 Minuten Timeout
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Treiber '{package_name}' erfolgreich installiert")
                return True
            else:
                error_msg = f"Installation fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise DriverInstallationError(error_msg)

        except subprocess.TimeoutExpired:
            error_msg = f"Installation von '{package_name}' hat zu lange gedauert"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)
        except FileNotFoundError:
            error_msg = "apt-get nicht gefunden. Ist dies ein Debian/Ubuntu-System?"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

    def update_package_cache(self, use_sudo: bool = True) -> bool:
        """
        Aktualisiert den apt Package-Cache

        Args:
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            bool: True bei Erfolg
        """
        self.logger.info("Aktualisiere Package-Cache...")

        cmd = ["apt-get", "update"]
        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info("Package-Cache erfolgreich aktualisiert")
                return True
            else:
                self.logger.warning(f"Package-Cache-Update fehlgeschlagen: {result.stderr}")
                return False

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Fehler bei apt-get update: {e}")
            return False

    def install_driver_for_model(
        self,
        model: str,
        install_scanner: bool = True,
        prefer_opensource: bool = True,
        use_sudo: bool = True,
    ) -> Tuple[bool, List[str]]:
        """
        Installiert den empfohlenen Treiber für ein Modell

        Args:
            model: Brother-Modellname (z.B. "MFC-L2700DN")
            install_scanner: Installiere auch Scanner-Treiber (Standard: True)
            prefer_opensource: Bevorzuge Open-Source-Treiber (Standard: True)
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            Tuple[bool, List[str]]: (Erfolg, Liste installierter Pakete)

        Raises:
            DriverInstallationError: Bei Installationsfehler
        """
        self.logger.info(f"Installiere Treiber für Modell: {model}")

        installed_packages = []

        # Drucker-Treiber
        driver_name = get_recommended_driver(model, prefer_opensource)
        if not driver_name:
            error_msg = f"Kein Treiber für Modell '{model}' gefunden"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

        driver_info = get_driver_info(driver_name)
        if not driver_info:
            error_msg = f"Treiber-Info für '{driver_name}' nicht gefunden"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

        # Installiere Drucker-Treiber
        if driver_info.source == DriverSource.REPOSITORY:
            success = self.install_from_repository(
                driver_info.package_name, use_sudo=use_sudo
            )
            if success:
                installed_packages.append(driver_info.package_name)
        else:
            # TODO: Brother-Website-Download implementieren
            error_msg = (
                f"Download von Brother-Website noch nicht implementiert. "
                f"Bitte installiere '{driver_name}' manuell von: {driver_info.download_url}"
            )
            self.logger.warning(error_msg)
            raise DriverInstallationError(error_msg)

        # Scanner-Treiber (falls Multifunktionsgerät)
        if install_scanner:
            scanner_driver_name = get_scanner_driver(model)
            if scanner_driver_name:
                scanner_info = get_driver_info(scanner_driver_name)
                if scanner_info and scanner_info.source == DriverSource.REPOSITORY:
                    success = self.install_from_repository(
                        scanner_info.package_name, use_sudo=use_sudo
                    )
                    if success:
                        installed_packages.append(scanner_info.package_name)

        self.logger.info(
            f"Installation abgeschlossen. Installierte Pakete: {', '.join(installed_packages)}"
        )
        return True, installed_packages

    def uninstall_driver(self, package_name: str, use_sudo: bool = True) -> bool:
        """
        Deinstalliert ein Treiber-Paket

        Args:
            package_name: Name des Pakets
            use_sudo: Verwende sudo (Standard: True)

        Returns:
            bool: True bei Erfolg

        Raises:
            DriverInstallationError: Bei Deinstallationsfehler
        """
        self.logger.info(f"Deinstalliere Treiber '{package_name}'...")

        # Prüfe ob installiert
        if not self.is_driver_installed(package_name):
            self.logger.info(f"Treiber '{package_name}' ist nicht installiert")
            return True

        # apt-get remove ausführen
        cmd = ["apt-get", "remove", "-y", package_name]
        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Treiber '{package_name}' erfolgreich deinstalliert")
                return True
            else:
                error_msg = f"Deinstallation fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise DriverInstallationError(error_msg)

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            error_msg = f"Fehler bei Deinstallation: {e}"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

    def list_installed_brother_drivers(self) -> List[str]:
        """
        Liste alle installierten Brother-Treiber auf

        Returns:
            List[str]: Liste der installierten Pakete
        """
        try:
            result = subprocess.run(
                ["dpkg", "-l"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            installed = []
            if result.returncode == 0:
                # Suche nach brother, brlaser, brscan
                for line in result.stdout.split("\n"):
                    if line.startswith("ii"):
                        parts = line.split()
                        if len(parts) >= 2:
                            package = parts[1]
                            if any(
                                keyword in package.lower()
                                for keyword in ["brother", "brlaser", "brscan"]
                            ):
                                installed.append(package)

            return installed

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Fehler bei dpkg -l: {e}")
            return []
