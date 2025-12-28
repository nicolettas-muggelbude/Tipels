"""
Tipels - Brother Treiber-Datenbank

Enthält Informationen über verfügbare Treiber für Brother-Geräte
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DriverType(Enum):
    """Treiber-Typ"""

    OPENSOURCE = "opensource"  # OpenPrinting, brlaser, etc.
    OFFICIAL = "official"  # Brother Official Driver
    CUPS_GENERIC = "cups_generic"  # CUPS Generic PostScript


class DriverSource(Enum):
    """Treiber-Quelle"""

    REPOSITORY = "repository"  # Ubuntu/Debian Repository
    BROTHER_WEBSITE = "brother_website"  # Brother Download-Center
    OPENPRINTING = "openprinting"  # OpenPrinting.org


@dataclass
class DriverInfo:
    """Informationen über einen Treiber"""

    name: str  # z.B. "printer-driver-brlaser"
    driver_type: DriverType
    source: DriverSource

    # Repository-Info (falls source=REPOSITORY)
    package_name: Optional[str] = None  # z.B. "printer-driver-brlaser"

    # Brother Official (falls source=BROTHER_WEBSITE)
    download_url: Optional[str] = None  # URL zum .deb-Paket
    version: Optional[str] = None

    # Unterstützte Modelle (Regex-Pattern)
    supported_models: List[str] = None  # z.B. ["MFC-L.*", "DCP-L.*"]

    # Zusätzliche Infos
    description: Optional[str] = None
    requires_non_free: bool = False  # Benötigt non-free Repository


# Brother Treiber-Datenbank
BROTHER_DRIVERS = {
    # OpenPrinting/brlaser - Open-Source Treiber für Brother Laser-Drucker
    "brlaser": DriverInfo(
        name="brlaser",
        driver_type=DriverType.OPENSOURCE,
        source=DriverSource.REPOSITORY,
        package_name="printer-driver-brlaser",
        supported_models=[
            "MFC-L2700.*",
            "MFC-L2720.*",
            "MFC-L2740.*",
            "DCP-L2500.*",
            "DCP-L2520.*",
            "DCP-L2540.*",
            "HL-L2300.*",
            "HL-L2320.*",
            "HL-L2340.*",
            "HL-L2360.*",
            "HL-L2380.*",
        ],
        description="Open-Source-Treiber für Brother Monochrom-Laser-Drucker",
        requires_non_free=False,
    ),
    # Brother Scan Key Tool - Scanner-Unterstützung
    "brscan4": DriverInfo(
        name="brscan4",
        driver_type=DriverType.OPENSOURCE,
        source=DriverSource.REPOSITORY,
        package_name="brscan4",
        supported_models=[
            "MFC-.*",  # Alle MFC (Multi-Function)
            "DCP-.*",  # Alle DCP mit Scanner
        ],
        description="Brother Scanner-Treiber für SANE",
        requires_non_free=False,
    ),
    # Brother LPR Driver (Official) - Generisch
    "brother-lpr": DriverInfo(
        name="brother-lpr",
        driver_type=DriverType.OFFICIAL,
        source=DriverSource.BROTHER_WEBSITE,
        download_url="https://support.brother.com/g/b/downloadlist.aspx",
        supported_models=[".*"],  # Alle Brother-Modelle
        description="Offizieller Brother LPR-Treiber",
        requires_non_free=False,
    ),
    # Brother CUPS Wrapper (Official) - Generisch
    "brother-cups-wrapper": DriverInfo(
        name="brother-cups-wrapper",
        driver_type=DriverType.OFFICIAL,
        source=DriverSource.BROTHER_WEBSITE,
        download_url="https://support.brother.com/g/b/downloadlist.aspx",
        supported_models=[".*"],  # Alle Brother-Modelle
        description="Offizieller Brother CUPS-Wrapper",
        requires_non_free=False,
    ),
    # ========== Modellspezifische Brother Official Drivers (Fallback) ==========
    # Hinweis: Diese werden nur verwendet wenn:
    # 1. OpenPrinting-Treiber nicht verfügbar/funktioniert nicht
    # 2. User explizit Brother-Treiber wünscht
    # 3. Spezielle Features benötigt (Fax, erweiterte Funktionen)
    # MFC-L2700DN - LPR Driver
    "brother-lpr-mfcl2700dn": DriverInfo(
        name="brother-lpr-mfcl2700dn",
        driver_type=DriverType.OFFICIAL,
        source=DriverSource.BROTHER_WEBSITE,
        download_url="https://download.brother.com/welcome/dlf006893/mfcl2700dnlpr-3.5.1-1.i386.deb",
        version="3.5.1-1",
        supported_models=["MFC-L2700DN"],
        description="Brother LPR Driver für MFC-L2700DN",
        requires_non_free=False,
    ),
    # MFC-L2700DN - CUPS Wrapper
    "brother-cups-mfcl2700dn": DriverInfo(
        name="brother-cups-mfcl2700dn",
        driver_type=DriverType.OFFICIAL,
        source=DriverSource.BROTHER_WEBSITE,
        download_url="https://download.brother.com/welcome/dlf006895/mfcl2700dncupswrapper-3.5.1-1.i386.deb",
        version="3.5.1-1",
        supported_models=["MFC-L2700DN"],
        description="Brother CUPS Wrapper für MFC-L2700DN",
        requires_non_free=False,
    ),
    # MFC-L2700DW - LPR Driver
    "brother-lpr-mfcl2700dw": DriverInfo(
        name="brother-lpr-mfcl2700dw",
        driver_type=DriverType.OFFICIAL,
        source=DriverSource.BROTHER_WEBSITE,
        download_url="https://download.brother.com/welcome/dlf006893/mfcl2700dnlpr-3.5.1-1.i386.deb",
        version="3.5.1-1",
        supported_models=["MFC-L2700DW"],
        description="Brother LPR Driver für MFC-L2700DW",
        requires_non_free=False,
    ),
}

# Hinweis zu Brother-URLs:
# Die URLs sind modellspezifisch und können sich ändern.
# Für nicht gelistete Modelle: User zur Brother-Support-Seite leiten:
# https://support.brother.com/g/b/productsearch.aspx?c=de&lang=de&content=dl


# Spezifische Modell-zu-Treiber-Zuordnung
MODEL_DRIVER_MAPPING = {
    "MFC-L2700DN": {
        "preferred": "brlaser",
        "alternatives": ["brother-lpr", "brother-cups-wrapper"],
        "scanner": "brscan4",
    },
    "MFC-L2700DW": {
        "preferred": "brlaser",
        "alternatives": ["brother-lpr", "brother-cups-wrapper"],
        "scanner": "brscan4",
    },
    "MFC-L3770CDW": {
        "preferred": "brother-lpr",  # Farb-Laser, kein brlaser-Support
        "alternatives": ["brother-cups-wrapper"],
        "scanner": "brscan4",
    },
}


def get_recommended_driver(model: str, prefer_opensource: bool = True) -> Optional[str]:
    """
    Gibt den empfohlenen Treiber für ein Modell zurück

    Args:
        model: Brother-Modellname (z.B. "MFC-L2700DN")
        prefer_opensource: Bevorzuge Open-Source-Treiber (wird nur berücksichtigt
                           wenn mehrere Optionen verfügbar sind)

    Returns:
        Optional[str]: Treiber-Name oder None
    """
    mapping = MODEL_DRIVER_MAPPING.get(model)
    if not mapping:
        return None

    preferred = mapping.get("preferred")

    # Standardmäßig: bevorzugter Treiber
    # (prefer_opensource ist bereits im Mapping berücksichtigt)
    return preferred


def get_scanner_driver(model: str) -> Optional[str]:
    """
    Gibt den Scanner-Treiber für ein Modell zurück

    Args:
        model: Brother-Modellname

    Returns:
        Optional[str]: Scanner-Treiber-Name oder None
    """
    mapping = MODEL_DRIVER_MAPPING.get(model)
    if not mapping:
        return None

    return mapping.get("scanner")


def get_driver_info(driver_name: str) -> Optional[DriverInfo]:
    """
    Gibt Informationen über einen Treiber zurück

    Args:
        driver_name: Name des Treibers

    Returns:
        Optional[DriverInfo]: Treiber-Informationen oder None
    """
    return BROTHER_DRIVERS.get(driver_name)
