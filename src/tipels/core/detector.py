"""
Tipels - Hardware-Erkennung

Hardware-Detector für USB- und Netzwerk-Geräte
"""

import re
import subprocess
from typing import List, Optional, Callable
from pathlib import Path

from tipels.core.device import Device, DeviceType, ConnectionType, DeviceStatus
from tipels.core.logger import TipelsLogger


# GitHub Issue-Template URL für Hardware-Support-Anfragen
HARDWARE_SUPPORT_URL = (
    "https://github.com/nicolettas-muggelbude/Tipels/issues/new?template=hardware_support.yml"
)

# USB Vendor IDs bekannter Drucker-Hersteller
USB_VENDORS = {
    "04f9": "Brother",  # Unterstützt
    "03f0": "HP",  # Noch nicht unterstützt
    "04a9": "Canon",  # Noch nicht unterstützt
    "04b8": "Epson",  # Noch nicht unterstützt
    "0924": "Xerox",  # Noch nicht unterstützt
    "0525": "Lexmark",  # Noch nicht unterstützt
    "413c": "Dell",  # Noch nicht unterstützt
    "0482": "Kyocera",  # Noch nicht unterstützt
}


class HardwareDetector:
    """Hardware-Detector für Drucker und Scanner"""

    def __init__(
        self,
        logger: Optional[TipelsLogger] = None,
        lsusb_command: Optional[Callable] = None,
        avahi_command: Optional[Callable] = None,
    ):
        """
        Initialisiert den Hardware-Detector

        Args:
            logger: Logger-Instanz (optional)
            lsusb_command: Callable für lsusb (für Tests, optional)
            avahi_command: Callable für avahi-browse (für Tests, optional)
        """
        self.logger = logger or TipelsLogger("tipels.detector")
        self._lsusb_command = lsusb_command or self._run_lsusb
        self._avahi_command = avahi_command or self._run_avahi_browse

    def _run_lsusb(self) -> str:
        """
        Führt lsusb aus

        Returns:
            str: Ausgabe von lsusb
        """
        try:
            result = subprocess.run(
                ["lsusb", "-v"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"lsusb Fehler: {e}")
            return ""

    def _run_avahi_browse(self) -> str:
        """
        Führt avahi-browse aus

        Returns:
            str: Ausgabe von avahi-browse
        """
        try:
            # Scanne nach IPP-Druckern und allgemeinen Druckern
            result = subprocess.run(
                ["avahi-browse", "-t", "-r", "-p", "_ipp._tcp,_printer._tcp"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"avahi-browse Fehler: {e}")
            return ""

    def scan_all(self) -> List[Device]:
        """
        Scannt nach allen Geräten (USB + Netzwerk)

        Returns:
            List[Device]: Liste aller erkannten Geräte
        """
        devices = []
        devices.extend(self.scan_usb())
        devices.extend(self.scan_network())
        self.logger.info(f"{len(devices)} Geräte erkannt")
        return devices

    def scan_usb(self) -> List[Device]:
        """
        Scannt nach USB-Geräten

        Returns:
            List[Device]: Liste der USB-Geräte
        """
        self.logger.info("Scanne USB-Geräte...")
        devices = []

        lsusb_output = self._lsusb_command()
        if not lsusb_output:
            return devices

        # Parse lsusb -v Ausgabe
        # Format: Bus XXX Device XXX: ID VVVV:PPPP Manufacturer Model
        usb_pattern = re.compile(
            r"Bus\s+\d+\s+Device\s+\d+:\s+ID\s+([0-9a-f]{4}):([0-9a-f]{4})\s+(.*)"
        )

        for line in lsusb_output.split("\n"):
            match = usb_pattern.match(line)
            if match:
                vendor_id = match.group(1)
                product_id = match.group(2)
                description = match.group(3).strip()

                # Identifiziere Drucker/Scanner anhand VID/PID
                device = self._identify_usb_device(vendor_id, product_id, description)
                if device:
                    devices.append(device)

        self.logger.info(f"{len(devices)} USB-Geräte gefunden")
        return devices

    def scan_network(self) -> List[Device]:
        """
        Scannt nach Netzwerk-Geräten (via Avahi/mDNS)

        Returns:
            List[Device]: Liste der Netzwerk-Geräte
        """
        self.logger.info("Scanne Netzwerk-Geräte...")
        devices = []

        avahi_output = self._avahi_command()
        if not avahi_output:
            return devices

        # Parse avahi-browse -p Ausgabe
        # Format: =;interface;protocol;name;type;domain;hostname;address;port;txt...
        for line in avahi_output.split("\n"):
            if not line.startswith("="):
                continue

            parts = line.split(";")
            if len(parts) < 9:
                continue

            service_name = parts[3]
            service_type = parts[4]
            hostname = parts[6]
            ip_address = parts[7]
            port = parts[8]

            # Identifiziere Gerät anhand Service-Name
            device = self._identify_network_device(
                service_name, hostname, ip_address, port, service_type
            )
            if device:
                devices.append(device)

        self.logger.info(f"{len(devices)} Netzwerk-Geräte gefunden")
        return devices

    def _identify_network_device(
        self,
        service_name: str,
        hostname: str,
        ip_address: str,
        port: str,
        service_type: str,
    ) -> Optional[Device]:
        """
        Identifiziert ein Netzwerk-Gerät

        Args:
            service_name: Service-Name (z.B. "Brother MFC-L2700DN series")
            hostname: mDNS Hostname
            ip_address: IP-Adresse
            port: Port
            service_type: Service-Typ (_ipp._tcp, _printer._tcp)

        Returns:
            Optional[Device]: Device-Objekt oder None
        """
        # Extrahiere Hersteller und Modell aus Service-Name
        # Typische Formate:
        # - "Brother MFC-L2700DN series"
        # - "HP LaserJet Pro M404dn"
        # - "Canon PIXMA TR4500 series"

        manufacturer = None
        model = None
        supported = False  # Default: nicht unterstützt

        service_lower = service_name.lower()

        # Erkenne Brother (UNTERSTÜTZT)
        if "brother" in service_lower:
            manufacturer = "Brother"
            # Extrahiere Modell (z.B. "MFC-L2700DN")
            match = re.search(
                r"(MFC-[A-Z0-9]+|DCP-[A-Z0-9]+|HL-[A-Z0-9]+)", service_name, re.IGNORECASE
            )
            if match:
                model = match.group(1).upper()
                supported = True

        # HP (NOCH NICHT UNTERSTÜTZT)
        elif "hp" in service_lower or "hewlett" in service_lower:
            manufacturer = "HP"
            # Extrahiere Modell (z.B. "LaserJet Pro M404dn")
            match = re.search(
                r"(LaserJet|OfficeJet|DeskJet|Envy|PageWide)\s+[A-Za-z0-9\s-]+",
                service_name,
                re.IGNORECASE,
            )
            if match:
                model = match.group(0).strip()
                supported = False

        # Canon (NOCH NICHT UNTERSTÜTZT)
        elif "canon" in service_lower:
            manufacturer = "Canon"
            # Extrahiere Modell (z.B. "PIXMA TR4500")
            match = re.search(
                r"(PIXMA|imageCLASS|imageRUNNER|MAXIFY)\s+[A-Z0-9-]+", service_name, re.IGNORECASE
            )
            if match:
                model = match.group(0).strip()
                supported = False

        # Epson (NOCH NICHT UNTERSTÜTZT)
        elif "epson" in service_lower:
            manufacturer = "Epson"
            # Extrahiere Modell (z.B. "WorkForce WF-2830")
            match = re.search(
                r"(WorkForce|EcoTank|Expression|SureColor)\s+[A-Z0-9-]+",
                service_name,
                re.IGNORECASE,
            )
            if match:
                model = match.group(0).strip()
                supported = False

        # Xerox (NOCH NICHT UNTERSTÜTZT)
        elif "xerox" in service_lower:
            manufacturer = "Xerox"
            model = service_name.replace("Xerox", "").strip()
            supported = False

        # Lexmark (NOCH NICHT UNTERSTÜTZT)
        elif "lexmark" in service_lower:
            manufacturer = "Lexmark"
            model = service_name.replace("Lexmark", "").strip()
            supported = False

        if not manufacturer or not model:
            self.logger.warning(f"Unbekanntes Netzwerk-Gerät: {service_name}")
            return None

        # Bestimme Gerätetyp anhand Service-Type
        device_type = DeviceType.PRINTER
        if "_ipp._tcp" in service_type or "_printer._tcp" in service_type:
            # Annahme: Netzwerk-Drucker sind meist Multifunktionsgeräte
            device_type = DeviceType.MULTIFUNCTION

        # Erstelle Connection URI
        if "_ipp._tcp" in service_type:
            connection_uri = f"ipp://{ip_address}:{port}/ipp/print"
        else:
            connection_uri = f"socket://{ip_address}:{port}"

        device = Device(
            manufacturer=manufacturer,
            model=model,
            device_type=device_type,
            connection_type=ConnectionType.NETWORK,
            connection_uri=connection_uri,
            ip_address=ip_address,
            hostname=hostname,
            status=DeviceStatus.DETECTED,
            supported=supported,
            support_url=HARDWARE_SUPPORT_URL if not supported else None,
            driver_installed=False,
        )

        if supported:
            self.logger.info(f"Netzwerk-Gerät erkannt: {device}")
        else:
            self.logger.warning(
                f"Nicht unterstütztes Netzwerk-Gerät erkannt: {device} - "
                f"Feature-Request unter: {HARDWARE_SUPPORT_URL}"
            )

        return device

    def _identify_usb_device(
        self, vendor_id: str, product_id: str, description: str
    ) -> Optional[Device]:
        """
        Identifiziert ein USB-Gerät anhand VID/PID

        Args:
            vendor_id: USB Vendor ID (hex)
            product_id: USB Product ID (hex)
            description: Geräte-Beschreibung von lsusb

        Returns:
            Optional[Device]: Device-Objekt oder None
        """
        vendor_id_lower = vendor_id.lower()

        # Brother Vendor ID: 04f9 (UNTERSTÜTZT)
        if vendor_id_lower == "04f9":
            return self._identify_brother_device(vendor_id, product_id, description)

        # Andere bekannte Hersteller (NOCH NICHT UNTERSTÜTZT)
        if vendor_id_lower in USB_VENDORS:
            return self._identify_generic_device(
                vendor_id, product_id, description, supported=False
            )

        return None

    def _identify_generic_device(
        self,
        vendor_id: str,
        product_id: str,
        description: str,
        supported: bool = False,
    ) -> Optional[Device]:
        """
        Identifiziert ein generisches Gerät (noch nicht unterstützt)

        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID
            description: Geräte-Beschreibung
            supported: Ob das Gerät unterstützt wird

        Returns:
            Optional[Device]: Device-Objekt oder None
        """
        vendor_id_lower = vendor_id.lower()
        manufacturer = USB_VENDORS.get(vendor_id_lower, "Unbekannt")

        # Versuche Modell aus Beschreibung zu extrahieren
        # Format: "Vendor_Name Model_Name"
        model = "Unbekanntes Modell"
        if manufacturer in description:
            # Extrahiere alles nach dem Herstellernamen
            parts = description.split(manufacturer, 1)
            if len(parts) > 1:
                model = parts[1].strip()
                # Bereinige Kommas und extra Whitespace
                model = model.split(",")[0].strip()

        if not model or model == "Unbekanntes Modell":
            model = f"{vendor_id}:{product_id}"

        # Annahme: Wenn es ein Drucker-Hersteller ist, ist es wahrscheinlich ein Multifunktionsgerät
        device_type = DeviceType.MULTIFUNCTION

        connection_uri = f"usb://{manufacturer}/{model}?serial=unknown"

        device = Device(
            manufacturer=manufacturer,
            model=model,
            device_type=device_type,
            connection_type=ConnectionType.USB,
            connection_uri=connection_uri,
            vendor_id=vendor_id,
            product_id=product_id,
            status=DeviceStatus.DETECTED,
            supported=supported,
            support_url=HARDWARE_SUPPORT_URL if not supported else None,
            driver_installed=False,
        )

        if supported:
            self.logger.info(f"Gerät erkannt: {device}")
        else:
            self.logger.warning(
                f"Nicht unterstütztes Gerät erkannt: {device} - "
                f"Feature-Request unter: {HARDWARE_SUPPORT_URL}"
            )

        return device

    def _identify_brother_device(
        self, vendor_id: str, product_id: str, description: str
    ) -> Optional[Device]:
        """
        Identifiziert Brother-Geräte

        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID
            description: Geräte-Beschreibung

        Returns:
            Optional[Device]: Device-Objekt oder None
        """
        # Brother VID/PID Datenbank
        # Quelle: https://github.com/OpenPrinting/cups-filters
        brother_devices = {
            "0273": {
                "model": "MFC-L2700DN",
                "type": DeviceType.MULTIFUNCTION,
            },
            "0274": {
                "model": "MFC-L2700DW",
                "type": DeviceType.MULTIFUNCTION,
            },
            "0366": {
                "model": "MFC-L3770CDW",
                "type": DeviceType.MULTIFUNCTION,
            },
            # Weitere Brother-Geräte können hier hinzugefügt werden
        }

        device_info = brother_devices.get(product_id.lower())
        if not device_info:
            self.logger.warning(f"Unbekanntes Brother-Gerät: {vendor_id}:{product_id}")
            return None

        # Erstelle Device-Objekt
        model = device_info["model"]
        device_type = device_info["type"]

        connection_uri = f"usb://Brother/{model}?serial=unknown"

        device = Device(
            manufacturer="Brother",
            model=model,
            device_type=device_type,
            connection_type=ConnectionType.USB,
            connection_uri=connection_uri,
            vendor_id=vendor_id,
            product_id=product_id,
            status=DeviceStatus.DETECTED,
            driver_installed=False,
        )

        self.logger.info(f"Brother-Gerät erkannt: {device}")
        return device

    def get_device_by_uri(self, uri: str) -> Optional[Device]:
        """
        Findet ein Gerät anhand der URI

        Args:
            uri: Connection URI

        Returns:
            Optional[Device]: Device oder None
        """
        all_devices = self.scan_all()
        for device in all_devices:
            if device.connection_uri == uri:
                return device
        return None

    def is_device_connected(self, device: Device) -> bool:
        """
        Prüft ob ein Gerät verbunden ist

        Args:
            device: Zu prüfendes Gerät

        Returns:
            bool: True wenn verbunden
        """
        if device.is_usb():
            usb_devices = self.scan_usb()
            for usb_dev in usb_devices:
                if (
                    usb_dev.vendor_id == device.vendor_id
                    and usb_dev.product_id == device.product_id
                ):
                    return True
            return False

        if device.is_network():
            network_devices = self.scan_network()
            for net_dev in network_devices:
                if net_dev.ip_address == device.ip_address:
                    return True
            return False

        return False
