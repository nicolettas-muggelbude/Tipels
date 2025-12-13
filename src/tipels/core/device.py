"""
Tipels - Device Datenklassen

Datenklassen für Drucker und Scanner
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DeviceType(Enum):
    """Gerätetyp"""
    PRINTER = "printer"
    SCANNER = "scanner"
    MULTIFUNCTION = "multifunction"  # Drucker + Scanner


class ConnectionType(Enum):
    """Verbindungsart"""
    USB = "usb"
    NETWORK = "network"
    BLUETOOTH = "bluetooth"
    UNKNOWN = "unknown"


class DeviceStatus(Enum):
    """Gerätestatus"""
    DETECTED = "detected"  # Erkannt, aber nicht konfiguriert
    CONFIGURED = "configured"  # In CUPS/SANE konfiguriert
    READY = "ready"  # Bereit zur Nutzung
    ERROR = "error"  # Fehler
    OFFLINE = "offline"  # Offline/Nicht erreichbar


@dataclass
class Device:
    """Basis-Datenklasse für Geräte (Drucker/Scanner)"""

    # Identifikation
    manufacturer: str  # z.B. "Brother"
    model: str  # z.B. "MFC-L2700DN"
    device_type: DeviceType

    # Verbindung
    connection_type: ConnectionType
    connection_uri: str  # z.B. "usb://Brother/MFC-L2700DN" oder "ipp://192.168.1.100"

    # Hardware-IDs (USB)
    vendor_id: Optional[str] = None  # USB Vendor ID (z.B. "04f9")
    product_id: Optional[str] = None  # USB Product ID (z.B. "0273")

    # Netzwerk
    ip_address: Optional[str] = None  # Bei Netzwerk-Geräten
    hostname: Optional[str] = None  # mDNS/Avahi Hostname

    # Status
    status: DeviceStatus = DeviceStatus.DETECTED

    # Unterstützung
    supported: bool = True  # Von Tipels unterstützt?
    support_url: Optional[str] = None  # URL zum Request-Feature wenn nicht unterstützt

    # Treiber-Informationen
    driver_installed: bool = False
    driver_name: Optional[str] = None
    driver_version: Optional[str] = None

    # CUPS/SANE Namen
    cups_name: Optional[str] = None  # Name in CUPS
    sane_name: Optional[str] = None  # Name in SANE

    def __str__(self) -> str:
        """String-Repräsentation"""
        return f"{self.manufacturer} {self.model} ({self.connection_type.value})"

    def get_full_name(self) -> str:
        """Vollständiger Gerätename"""
        return f"{self.manufacturer} {self.model}"

    def is_usb(self) -> bool:
        """Prüft ob USB-Gerät"""
        return self.connection_type == ConnectionType.USB

    def is_network(self) -> bool:
        """Prüft ob Netzwerk-Gerät"""
        return self.connection_type == ConnectionType.NETWORK

    def is_configured(self) -> bool:
        """Prüft ob Gerät konfiguriert ist"""
        return self.status in [DeviceStatus.CONFIGURED, DeviceStatus.READY]

    def is_printer(self) -> bool:
        """Prüft ob Drucker"""
        return self.device_type in [DeviceType.PRINTER, DeviceType.MULTIFUNCTION]

    def is_scanner(self) -> bool:
        """Prüft ob Scanner"""
        return self.device_type in [DeviceType.SCANNER, DeviceType.MULTIFUNCTION]


@dataclass
class Printer(Device):
    """Drucker-spezifische Datenklasse"""

    # Drucker-Funktionen
    supports_color: bool = False
    supports_duplex: bool = False
    max_paper_size: str = "A4"

    # Status
    toner_level: Optional[int] = None  # 0-100%
    paper_level: Optional[int] = None  # 0-100%

    def __post_init__(self):
        """Post-Initialisierung"""
        if self.device_type == DeviceType.SCANNER:
            raise ValueError("Printer kann nicht vom Typ SCANNER sein")


@dataclass
class Scanner(Device):
    """Scanner-spezifische Datenklasse"""

    # Scanner-Funktionen
    supports_adf: bool = False  # Automatischer Dokumenteneinzug
    max_scan_size: str = "A4"
    max_resolution: int = 1200  # DPI

    def __post_init__(self):
        """Post-Initialisierung"""
        if self.device_type == DeviceType.PRINTER:
            raise ValueError("Scanner kann nicht vom Typ PRINTER sein")
