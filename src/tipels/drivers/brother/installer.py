"""
Tipels - Brother Treiber-Installation

Installiert und verwaltet Brother-Drucker- und Scanner-Treiber
"""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests

from tipels.core.foomatic import FoomaticDetector, FoomaticDriver
from tipels.core.logger import TipelsLogger
from tipels.core.printer_cache import PrinterCache
from tipels.drivers.brother.driver_db import (
    DriverInfo,
    DriverSource,
    get_driver_info,
    get_recommended_driver,
    get_scanner_driver,
)


class DriverInstallationError(Exception):
    """Fehler bei der Treiber-Installation"""

    pass


class DriverInstaller:
    """Installiert und verwaltet Brother-Treiber"""

    def __init__(
        self,
        logger: Optional[TipelsLogger] = None,
        use_foomatic: bool = True,
        cache_file: Optional[Path] = None,
    ):
        """
        Initialisiert den Driver-Installer

        Args:
            logger: Logger-Instanz (optional)
            use_foomatic: Nutze Foomatic-DB für Treiber-Erkennung (Standard: True)
            cache_file: Pfad zur Cache-Datei (optional)
        """
        self.logger = logger or TipelsLogger("tipels.driver.installer")
        self.use_foomatic = use_foomatic

        # Foomatic-Integration
        if use_foomatic:
            self.foomatic = FoomaticDetector(logger=self.logger)
            self.cache = PrinterCache(cache_file=cache_file, logger=self.logger)
        else:
            self.foomatic = None
            self.cache = None

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

    def install_from_repository(self, package_name: str, use_sudo: bool = True) -> bool:
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

    def download_deb_package(self, url: str, target_dir: Optional[Path] = None) -> Path:
        """
        Lädt ein .deb-Paket von einer URL herunter

        Args:
            url: URL zum .deb-Paket
            target_dir: Ziel-Verzeichnis (optional, Standard: temp)

        Returns:
            Path: Pfad zur heruntergeladenen Datei

        Raises:
            DriverInstallationError: Bei Download-Fehler
        """
        self.logger.info(f"Lade .deb-Paket herunter: {url}")

        # Extrahiere Dateinamen aus URL
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name

        if not filename.endswith(".deb"):
            filename += ".deb"

        # Ziel-Verzeichnis
        if target_dir is None:
            target_dir = Path(tempfile.gettempdir())
        else:
            target_dir = Path(target_dir)

        target_file = target_dir / filename

        try:
            # Download mit requests
            response = requests.get(url, timeout=120, stream=True)
            response.raise_for_status()

            # Schreibe Datei
            with open(target_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f".deb-Paket heruntergeladen: {target_file}")
            return target_file

        except requests.RequestException as e:
            error_msg = f"Download fehlgeschlagen: {e}"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)
        except OSError as e:
            error_msg = f"Fehler beim Schreiben der Datei: {e}"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

    def install_deb_package(
        self, deb_file: Path, use_sudo: bool = True, cleanup: bool = True
    ) -> bool:
        """
        Installiert ein .deb-Paket via dpkg

        Args:
            deb_file: Pfad zum .deb-Paket
            use_sudo: Verwende sudo (Standard: True)
            cleanup: Lösche .deb nach Installation (Standard: True)

        Returns:
            bool: True bei Erfolg

        Raises:
            DriverInstallationError: Bei Installationsfehler
        """
        if not deb_file.exists():
            error_msg = f".deb-Datei nicht gefunden: {deb_file}"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

        self.logger.info(f"Installiere .deb-Paket: {deb_file}")

        # dpkg -i ausführen
        cmd = ["dpkg", "-i", str(deb_file)]
        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f".deb-Paket erfolgreich installiert: {deb_file}")

                # Cleanup
                if cleanup:
                    try:
                        deb_file.unlink()
                        self.logger.info(f".deb-Datei gelöscht: {deb_file}")
                    except OSError as e:
                        self.logger.warning(f"Cleanup fehlgeschlagen: {e}")

                return True
            else:
                # dpkg kann Abhängigkeitsfehler haben
                # Versuche apt-get -f install
                if "dependency problems" in result.stderr.lower():
                    self.logger.warning(
                        "Abhängigkeitsprobleme erkannt. Versuche apt-get -f install..."
                    )
                    fix_result = self._fix_dependencies(use_sudo)
                    if fix_result:
                        self.logger.info("Abhängigkeiten erfolgreich repariert")
                        return True

                error_msg = f"dpkg Installation fehlgeschlagen: {result.stderr}"
                self.logger.error(error_msg)
                raise DriverInstallationError(error_msg)

        except subprocess.TimeoutExpired:
            error_msg = f"Installation von '{deb_file}' hat zu lange gedauert"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)
        except FileNotFoundError:
            error_msg = "dpkg nicht gefunden. Ist dies ein Debian/Ubuntu-System?"
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

    def _fix_dependencies(self, use_sudo: bool = True) -> bool:
        """
        Repariert Abhängigkeiten via apt-get -f install

        Args:
            use_sudo: Verwende sudo

        Returns:
            bool: True bei Erfolg
        """
        cmd = ["apt-get", "-f", "install", "-y"]
        if use_sudo:
            cmd = ["sudo"] + cmd

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def install_from_url(self, url: str, use_sudo: bool = True, cleanup: bool = True) -> bool:
        """
        Lädt .deb-Paket herunter und installiert es

        Args:
            url: URL zum .deb-Paket
            use_sudo: Verwende sudo (Standard: True)
            cleanup: Lösche .deb nach Installation (Standard: True)

        Returns:
            bool: True bei Erfolg

        Raises:
            DriverInstallationError: Bei Fehler
        """
        # Download
        deb_file = self.download_deb_package(url)

        # Installation
        return self.install_deb_package(deb_file, use_sudo=use_sudo, cleanup=cleanup)

    def find_driver_with_foomatic(self, manufacturer: str, model: str) -> Optional[FoomaticDriver]:
        """
        Findet Treiber über Foomatic-DB

        Args:
            manufacturer: Hersteller (z.B. "Brother", "HP", "Canon")
            model: Modell (z.B. "MFC-L2700DN", "LaserJet Pro M404dn")

        Returns:
            Optional[FoomaticDriver]: Empfohlener Treiber oder None
        """
        if not self.use_foomatic or not self.foomatic:
            self.logger.warning("Foomatic-Integration ist deaktiviert")
            return None

        # Prüfe Cache
        if self.cache:
            cached = self.cache.get(manufacturer, model)
            if cached and cached.get("ppd_name"):
                self.logger.info(
                    f"Treiber für {manufacturer} {model} aus Cache: "
                    f"{cached.get('openprinting_driver')}"
                )
                # Erstelle FoomaticDriver aus Cache
                return FoomaticDriver(
                    ppd_name=cached["ppd_name"],
                    driver=cached.get("openprinting_driver", "unknown"),
                    manufacturer=manufacturer,
                    model=model,
                    description=cached.get("description", ""),
                )

        # Nicht im Cache: Frage Foomatic
        self.logger.info(f"Suche Treiber für {manufacturer} {model} via Foomatic...")
        recommended = self.foomatic.get_recommended_driver(manufacturer, model)

        if recommended:
            # Speichere im Cache
            if self.cache:
                self.cache.set(
                    manufacturer=manufacturer,
                    model=model,
                    openprinting_driver=recommended.driver,
                    ppd_name=recommended.ppd_name,
                    description=recommended.description,
                )

            self.logger.info(
                f"Foomatic-Treiber gefunden: {recommended.driver} " f"({recommended.ppd_name})"
            )
            return recommended

        self.logger.info(f"Kein Foomatic-Treiber für {manufacturer} {model} gefunden")
        return None

    def install_driver_for_model(
        self,
        model: str,
        manufacturer: str = "Brother",
        install_scanner: bool = True,
        prefer_opensource: bool = True,
        use_sudo: bool = True,
        force_official: bool = False,
    ) -> Tuple[bool, List[str]]:
        """
        Installiert den empfohlenen Treiber für ein Modell

        Args:
            model: Modellname (z.B. "MFC-L2700DN", "LaserJet Pro M404dn")
            manufacturer: Hersteller (Standard: "Brother")
            install_scanner: Installiere auch Scanner-Treiber (Standard: True)
            prefer_opensource: Bevorzuge Open-Source-Treiber (Standard: True)
            use_sudo: Verwende sudo (Standard: True)
            force_official: Erzwinge Brother Official Driver statt OpenPrinting (Standard: False)
                           Nützlich wenn:
                           - OpenPrinting-Treiber fehlt/funktioniert nicht
                           - Spezielle Features benötigt (Fax, erweiterte Funktionen)
                           - User explizit Brother-Treiber wünscht

        Returns:
            Tuple[bool, List[str]]: (Erfolg, Liste installierter Pakete)

        Raises:
            DriverInstallationError: Bei Installationsfehler
        """
        self.logger.info(
            f"Installiere Treiber für {manufacturer} {model} " f"(force_official={force_official})"
        )

        installed_packages = []
        driver_name = None
        driver_info = None

        # Strategie 1: Foomatic-DB (wenn aktiviert und nicht force_official)
        if self.use_foomatic and not force_official:
            foomatic_driver = self.find_driver_with_foomatic(manufacturer, model)
            if foomatic_driver:
                self.logger.info(
                    f"Nutze Foomatic-Treiber: {foomatic_driver.driver} "
                    f"(Package: printer-driver-{foomatic_driver.driver})"
                )
                # Versuche Repository-Installation
                package_name = f"printer-driver-{foomatic_driver.driver}"
                try:
                    success = self.install_from_repository(package_name, use_sudo=use_sudo)
                    if success:
                        installed_packages.append(package_name)
                        # Update Cache mit last_used
                        if self.cache:
                            self.cache.update(
                                manufacturer=manufacturer,
                                model=model,
                                last_used=foomatic_driver.driver,
                            )
                except Exception as e:
                    self.logger.warning(
                        f"Foomatic-Treiber-Installation fehlgeschlagen: {e}. "
                        "Versuche Fallback zu Brother Official..."
                    )

        # Strategie 2: Brother Official (Fallback oder force_official)
        # Nur für Brother-Drucker verfügbar
        if not installed_packages and manufacturer.lower() == "brother":
            self.logger.info("Nutze Brother-spezifische Treiber-Datenbank...")

            # Drucker-Treiber
            if force_official:
                # User möchte explizit Brother Official Driver
                # Ignoriere prefer_opensource und nutze alternatives[0]
                from tipels.drivers.brother.driver_db import MODEL_DRIVER_MAPPING

                mapping = MODEL_DRIVER_MAPPING.get(model)
                if not mapping or not mapping.get("alternatives"):
                    error_msg = f"Kein Brother Official Driver für Modell '{model}' hinterlegt"
                    self.logger.error(error_msg)
                    raise DriverInstallationError(error_msg)

                driver_name = mapping["alternatives"][0]
                self.logger.info(f"Verwende Brother Official Driver: {driver_name}")
            else:
                # Standard: Empfohlener Treiber (OpenPrinting bevorzugt)
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
                success = self.install_from_repository(driver_info.package_name, use_sudo=use_sudo)
                if success:
                    installed_packages.append(driver_info.package_name)
            elif driver_info.source == DriverSource.BROTHER_WEBSITE:
                # Download und Installation von Brother-Website
                if not driver_info.download_url:
                    error_msg = f"Keine Download-URL für '{driver_name}' hinterlegt"
                    self.logger.error(error_msg)
                    raise DriverInstallationError(error_msg)

                self.logger.info(
                    f"Lade offiziellen Brother-Treiber herunter: {driver_info.download_url}"
                )
                success = self.install_from_url(
                    driver_info.download_url, use_sudo=use_sudo, cleanup=True
                )
                if success:
                    installed_packages.append(driver_info.name)
            else:
                error_msg = f"Unbekannte Treiber-Quelle: {driver_info.source}"
                self.logger.error(error_msg)
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

        # Fehler wenn keine Installation erfolgreich war
        if not installed_packages:
            if manufacturer.lower() != "brother":
                error_msg = (
                    f"Kein Treiber für {manufacturer} {model} gefunden. "
                    "Foomatic-DB hat keinen passenden Treiber."
                )
            else:
                error_msg = (
                    f"Keine Treiber für Brother {model} gefunden. "
                    "Weder Foomatic noch Brother Official Driver verfügbar."
                )
            self.logger.error(error_msg)
            raise DriverInstallationError(error_msg)

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
