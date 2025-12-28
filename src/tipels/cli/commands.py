"""
Tipels - CLI Commands

Kommandozeilen-Interface für Tipels
"""

import click
import sys
from typing import Optional
from pathlib import Path

from tipels import __version__
from tipels.core.logger import TipelsLogger
from tipels.core.detector import HardwareDetector
from tipels.core.device import DeviceType
from tipels.utils.cups_helper import CupsHelper, CupsError
from tipels.utils.sane_helper import SaneHelper, SaneError
from tipels.drivers.brother.installer import DriverInstaller
from tipels.drivers.brother.scanner import BrotherScannerManager


# Logger
logger = TipelsLogger("tipels.cli")


# Farben für bessere User Experience
def success(msg):
    """Erfolgsmeldung in Grün"""
    click.secho(f"✓ {msg}", fg="green")


def error(msg):
    """Fehlermeldung in Rot"""
    click.secho(f"✗ {msg}", fg="red", err=True)


def warning(msg):
    """Warnung in Gelb"""
    click.secho(f"⚠ {msg}", fg="yellow")


def info(msg):
    """Info-Meldung"""
    click.echo(f"ℹ {msg}")


@click.group()
@click.version_option(version=__version__)
def cli():
    """Tipels - Drucker & Scanner Setup-Tool für Linux"""
    pass


@cli.command()
@click.option("--usb", is_flag=True, help="Nur USB-Geräte scannen")
@click.option("--network", is_flag=True, help="Nur Netzwerk-Geräte scannen")
@click.option("--timeout", default=10, help="Timeout für Netzwerk-Scan (Sekunden)")
def scan(usb, network, timeout):
    """Scanne nach Druckern und Scannern"""
    click.echo("🔍 Scanne nach Geräten...")

    try:
        detector = HardwareDetector(logger=logger)

        # Bestimme Scan-Typen
        scan_usb = usb or (not usb and not network)
        scan_network = network or (not usb and not network)

        devices = []

        if scan_usb:
            info("Scanne USB-Geräte...")
            usb_devices = detector.detect_usb_devices()
            devices.extend(usb_devices)
            success(f"{len(usb_devices)} USB-Gerät(e) gefunden")

        if scan_network:
            info(f"Scanne Netzwerk (Timeout: {timeout}s)...")
            network_devices = detector.detect_network_devices(timeout=timeout)
            devices.extend(network_devices)
            success(f"{len(network_devices)} Netzwerk-Gerät(e) gefunden")

        if not devices:
            warning("Keine Geräte gefunden")
            return

        # Zeige gefundene Geräte
        click.echo("\n📋 Gefundene Geräte:")
        click.echo("=" * 70)

        for device in devices:
            device_type_str = "🖨️  Drucker" if device.device_type == DeviceType.PRINTER else "🖼️  Scanner"
            if device.device_type == DeviceType.MFP:
                device_type_str = "🖨️ 🖼️  Multifunktionsgerät"

            click.echo(f"\n{device_type_str}")
            click.echo(f"  Hersteller: {device.manufacturer}")
            click.echo(f"  Modell:     {device.model}")
            click.echo(f"  Verbindung: {device.connection_type.value.upper()}")

            if device.connection_type.value == "network" and device.ip_address:
                click.echo(f"  IP-Adresse: {device.ip_address}")
            if device.uri:
                click.echo(f"  URI:        {device.uri}")

        click.echo("\n" + "=" * 70)
        info(f"Gesamt: {len(devices)} Gerät(e) gefunden")

    except Exception as e:
        error(f"Fehler beim Scannen: {e}")
        logger.error(f"Scan-Fehler: {e}")
        sys.exit(1)


@cli.command()
@click.option("--model", required=True, help="Drucker/Scanner-Modell (z.B. MFC-L2700DN)")
@click.option("--connection", type=click.Choice(["usb", "network"]), required=True, help="Verbindungstyp")
@click.option("--ip", help="IP-Adresse (erforderlich bei Netzwerk)")
@click.option("--name", help="Gerätename im System (optional)")
@click.option("--type", "device_type", type=click.Choice(["printer", "scanner", "both"]), default="both", help="Gerätetyp")
def install(model, connection, ip, name, device_type):
    """Installiere Drucker/Scanner"""

    # Validierung
    if connection == "network" and not ip:
        error("--ip ist erforderlich für Netzwerk-Verbindungen")
        sys.exit(1)

    # Standard-Name falls nicht angegeben
    if not name:
        name = f"Brother_{model.replace('-', '_')}"

    click.echo(f"📦 Installiere {model} via {connection.upper()}...")

    try:
        # Installiere Drucker
        if device_type in ["printer", "both"]:
            info("Installiere Drucker-Treiber...")
            installer = DriverInstaller(logger=logger)

            # Drucker-Installation
            result = installer.install_driver(
                model=model,
                connection_type="network" if connection == "network" else "usb",
                ip_address=ip
            )

            if result:
                success("Drucker-Treiber erfolgreich installiert")

                # Registriere in CUPS
                cups = CupsHelper(logger=logger)
                if connection == "usb":
                    uri = f"usb://Brother/{model}"
                else:
                    uri = f"ipp://{ip}/ipp/print"

                ppd_file = cups.get_ppd_file(f"Brother {model}")
                cups.add_printer(
                    name=name,
                    uri=uri,
                    ppd_file=ppd_file,
                    description=f"Brother {model}",
                    use_sudo=True
                )
                success(f"Drucker '{name}' in CUPS registriert")
            else:
                warning("Drucker-Treiber-Installation fehlgeschlagen")

        # Installiere Scanner
        if device_type in ["scanner", "both"]:
            info("Konfiguriere Scanner...")
            scanner_mgr = BrotherScannerManager(logger=logger)

            if not scanner_mgr.is_brscan4_installed():
                warning("brscan4 ist nicht installiert. Installiere zuerst den Scanner-Treiber.")
            else:
                from tipels.drivers.brother.scanner import ScannerConnectionType
                conn_type = ScannerConnectionType.NETWORK if connection == "network" else ScannerConnectionType.USB

                scanner_mgr.add_scanner(
                    name=name,
                    model=model,
                    connection_type=conn_type,
                    device_node="/dev/usb/lp0" if connection == "usb" else None,
                    ip_address=ip if connection == "network" else None
                )
                success(f"Scanner '{name}' erfolgreich konfiguriert")

                # Füge User zu Gruppen hinzu
                info("Füge Benutzer zu Scanner-Gruppen hinzu...")
                added, groups = scanner_mgr.add_user_to_groups()
                if added:
                    success(f"Benutzer zu Gruppen hinzugefügt: {', '.join(groups)}")
                    warning("WICHTIG: Neuanmeldung erforderlich für Gruppenänderungen!")

        click.echo()
        success(f"✅ Installation von {model} abgeschlossen!")

    except (CupsError, Exception) as e:
        error(f"Fehler bei der Installation: {e}")
        logger.error(f"Installations-Fehler: {e}")
        sys.exit(1)


@cli.command()
@click.argument("device_name")
@click.option("--printer", is_flag=True, help="Nur Drucker entfernen")
@click.option("--scanner", is_flag=True, help="Nur Scanner entfernen")
@click.confirmation_option(prompt="Gerät wirklich entfernen?")
def remove(device_name, printer, scanner):
    """Entferne Drucker/Scanner"""

    click.echo(f"🗑️  Entferne {device_name}...")

    remove_printer = printer or (not printer and not scanner)
    remove_scanner = scanner or (not printer and not scanner)

    try:
        # Entferne Drucker
        if remove_printer:
            info("Entferne Drucker aus CUPS...")
            cups = CupsHelper(logger=logger)

            try:
                cups.remove_printer(device_name, use_sudo=True)
                success("Drucker erfolgreich entfernt")
            except CupsError as e:
                warning(f"Drucker konnte nicht entfernt werden: {e}")

        # Entferne Scanner
        if remove_scanner:
            info("Entferne Scanner aus SANE...")
            scanner_mgr = BrotherScannerManager(logger=logger)

            try:
                scanner_mgr.remove_scanner(device_name)
                success("Scanner erfolgreich entfernt")
            except Exception as e:
                warning(f"Scanner konnte nicht entfernt werden: {e}")

        click.echo()
        success(f"✅ {device_name} erfolgreich entfernt")

    except Exception as e:
        error(f"Fehler beim Entfernen: {e}")
        logger.error(f"Entfernungs-Fehler: {e}")
        sys.exit(1)


@cli.command()
@click.option("--printers", is_flag=True, help="Nur Drucker anzeigen")
@click.option("--scanners", is_flag=True, help="Nur Scanner anzeigen")
def list(printers, scanners):
    """Liste installierte Geräte"""

    show_printers = printers or (not printers and not scanners)
    show_scanners = scanners or (not printers and not scanners)

    try:
        # Liste Drucker
        if show_printers:
            click.echo("🖨️  Installierte Drucker:")
            click.echo("=" * 70)

            cups = CupsHelper(logger=logger)
            if not cups.is_cups_available():
                warning("CUPS ist nicht verfügbar")
            else:
                printer_list = cups.list_printers()

                if not printer_list:
                    info("Keine Drucker installiert")
                else:
                    for printer in printer_list:
                        click.echo(f"\n📄 {printer.name}")
                        click.echo(f"   Status:      {printer.state.value}")
                        click.echo(f"   URI:         {printer.uri}")
                        if printer.location:
                            click.echo(f"   Standort:    {printer.location}")
                        if printer.make_model:
                            click.echo(f"   Modell:      {printer.make_model}")
                        if printer.jobs > 0:
                            click.echo(f"   Jobs:        {printer.jobs}")

            click.echo()

        # Liste Scanner
        if show_scanners:
            click.echo("🖼️  Installierte Scanner:")
            click.echo("=" * 70)

            sane = SaneHelper(logger=logger)
            if not sane.is_sane_available():
                warning("SANE ist nicht verfügbar")
            else:
                scanner_list = sane.list_scanners()

                if not scanner_list:
                    info("Keine Scanner gefunden")
                else:
                    for scanner in scanner_list:
                        click.echo(f"\n🔍 {scanner.device_name}")
                        if scanner.vendor:
                            click.echo(f"   Hersteller:  {scanner.vendor}")
                        if scanner.model:
                            click.echo(f"   Modell:      {scanner.model}")
                        if scanner.backend:
                            click.echo(f"   Backend:     {scanner.backend}")
                        if scanner.scanner_type:
                            click.echo(f"   Typ:         {scanner.scanner_type}")

            click.echo()

    except Exception as e:
        error(f"Fehler beim Auflisten: {e}")
        logger.error(f"Listen-Fehler: {e}")
        sys.exit(1)


@cli.command()
@click.argument("output_path", type=click.Path())
def backup(output_path):
    """Erstelle Backup der Konfiguration"""
    click.echo(f"💾 Erstelle Backup nach {output_path}...")
    # TODO: Backup-Modul implementieren
    warning("Backup-Funktion ist noch nicht implementiert")
    info("Wird in einer zukünftigen Version verfügbar sein")


@cli.command()
@click.argument("backup_path", type=click.Path(exists=True))
def restore(backup_path):
    """Stelle Backup wieder her"""
    click.echo(f"♻️  Stelle Backup von {backup_path} wieder her...")
    # TODO: Restore-Modul implementieren
    warning("Restore-Funktion ist noch nicht implementiert")
    info("Wird in einer zukünftigen Version verfügbar sein")


@cli.command()
def status():
    """Zeige System-Status"""
    click.echo("📊 System-Status:")
    click.echo("=" * 70)

    try:
        # CUPS-Status
        click.echo("\n🖨️  CUPS (Drucker):")
        cups = CupsHelper(logger=logger)
        if cups.is_cups_available():
            success("CUPS läuft")
            printers = cups.list_printers()
            info(f"{len(printers)} Drucker installiert")
        else:
            error("CUPS ist nicht verfügbar")

        # SANE-Status
        click.echo("\n🖼️  SANE (Scanner):")
        sane = SaneHelper(logger=logger)
        status_info = sane.get_scanner_status()

        if status_info["sane_available"]:
            success("SANE installiert")
        else:
            error("SANE ist nicht installiert")

        if status_info["scanners_found"]:
            scanners = sane.list_scanners()
            info(f"{len(scanners)} Scanner gefunden")
        else:
            info("Keine Scanner gefunden")

        if status_info["scanner_group_exists"]:
            success("Gruppe 'scanner' existiert")
        else:
            warning("Gruppe 'scanner' fehlt")

        if status_info["saned_group_exists"]:
            success("Gruppe 'saned' existiert")
        else:
            warning("Gruppe 'saned' fehlt")

        # Brother-Treiber
        click.echo("\n📦 Brother-Treiber:")
        scanner_mgr = BrotherScannerManager(logger=logger)
        if scanner_mgr.is_brscan4_installed():
            success("brscan4 installiert")
        else:
            info("brscan4 nicht installiert")

        click.echo()

    except Exception as e:
        error(f"Fehler beim Status-Check: {e}")
        logger.error(f"Status-Fehler: {e}")
        sys.exit(1)


@cli.command("test-print")
@click.argument("printer_name")
@click.option("--file", "test_file", type=click.Path(exists=True), help="Test-Datei (optional)")
def test_print(printer_name, test_file):
    """Führe Testdruck durch"""
    click.echo(f"🖨️  Starte Testdruck auf '{printer_name}'...")

    try:
        cups = CupsHelper(logger=logger)
        cups.test_print(printer_name, test_file=test_file)
        success("Testdruck erfolgreich gestartet")
        info("Prüfe deinen Drucker für die Ausgabe")

    except CupsError as e:
        error(f"Testdruck fehlgeschlagen: {e}")
        logger.error(f"Testdruck-Fehler: {e}")
        sys.exit(1)


@cli.command("test-scan")
@click.option("--device", help="Scanner-Device (optional, nutzt ersten verfügbaren)")
@click.option("--output", default="/tmp/tipels_scan.pnm", help="Ausgabedatei")
@click.option("--format", "scan_format", type=click.Choice(["pnm", "tiff", "png", "jpeg"]), default="pnm", help="Scan-Format")
@click.option("--resolution", default=150, help="Scan-Auflösung (DPI)")
def test_scan(device, output, scan_format, resolution):
    """Führe Test-Scan durch"""

    device_str = device if device else "Auto-Device"
    click.echo(f"🖼️  Starte Test-Scan ({device_str}, {scan_format.upper()}, {resolution} DPI)...")

    try:
        from tipels.utils.sane_helper import ScanFormat

        sane = SaneHelper(logger=logger)

        # Format konvertieren
        format_map = {
            "pnm": ScanFormat.PNM,
            "tiff": ScanFormat.TIFF,
            "png": ScanFormat.PNG,
            "jpeg": ScanFormat.JPEG,
        }

        sane.test_scan(
            device_name=device,
            output_file=output,
            scan_format=format_map[scan_format],
            resolution=resolution
        )

        success(f"Test-Scan erfolgreich: {output}")

        # Zeige Dateigröße
        file_size = Path(output).stat().st_size
        info(f"Dateigröße: {file_size / 1024:.2f} KB")

    except SaneError as e:
        error(f"Test-Scan fehlgeschlagen: {e}")
        logger.error(f"Test-Scan-Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
