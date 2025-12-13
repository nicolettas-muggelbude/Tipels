"""
Tests für Hardware-Detector
"""

import pytest
from unittest.mock import MagicMock

from tipels.core.detector import HardwareDetector
from tipels.core.device import DeviceType, ConnectionType, DeviceStatus
from tipels.core.logger import TipelsLogger


# Mock lsusb Ausgabe
MOCK_LSUSB_OUTPUT = """Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 04f9:0273 Brother Industries, Ltd MFC-L2700DN
Bus 001 Device 003: ID 046d:c52b Logitech, Inc. Unifying Receiver
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 002 Device 002: ID 04f9:0366 Brother Industries, Ltd MFC-L3770CDW
"""

# Mock avahi-browse Ausgabe (parsable format)
MOCK_AVAHI_OUTPUT = """+;eth0;IPv4;Brother MFC-L2700DN series;_printer._tcp;local
=;eth0;IPv4;Brother MFC-L2700DN series;_printer._tcp;local;BRN001BA9123456.local;192.168.1.100;9100;
+;eth0;IPv4;Brother MFC-L2700DN series;_ipp._tcp;local
=;eth0;IPv4;Brother MFC-L2700DN series;_ipp._tcp;local;BRN001BA9123456.local;192.168.1.100;631;
"""


class TestHardwareDetector:
    """Tests für HardwareDetector"""

    @pytest.fixture
    def mock_logger(self):
        """Mock Logger"""
        logger = MagicMock(spec=TipelsLogger)
        return logger

    @pytest.fixture
    def detector_with_mocks(self, mock_logger):
        """HardwareDetector mit Mock-Commands"""
        mock_lsusb = MagicMock(return_value=MOCK_LSUSB_OUTPUT)
        mock_avahi = MagicMock(return_value=MOCK_AVAHI_OUTPUT)

        detector = HardwareDetector(
            logger=mock_logger,
            lsusb_command=mock_lsusb,
            avahi_command=mock_avahi,
        )

        return detector, mock_lsusb, mock_avahi

    def test_detector_initialization(self, mock_logger):
        """Test: Detector initialisieren"""
        detector = HardwareDetector(logger=mock_logger)
        assert detector.logger == mock_logger

    def test_scan_usb_devices(self, detector_with_mocks):
        """Test: USB-Geräte scannen"""
        detector, mock_lsusb, _ = detector_with_mocks

        devices = detector.scan_usb()

        # lsusb sollte aufgerufen worden sein
        mock_lsusb.assert_called_once()

        # 2 Brother-Geräte sollten erkannt worden sein
        assert len(devices) == 2

        # Erstes Gerät prüfen (MFC-L2700DN)
        device1 = devices[0]
        assert device1.manufacturer == "Brother"
        assert device1.model == "MFC-L2700DN"
        assert device1.vendor_id == "04f9"
        assert device1.product_id == "0273"
        assert device1.device_type == DeviceType.MULTIFUNCTION
        assert device1.connection_type == ConnectionType.USB
        assert device1.status == DeviceStatus.DETECTED

        # Zweites Gerät prüfen (MFC-L3770CDW)
        device2 = devices[1]
        assert device2.manufacturer == "Brother"
        assert device2.model == "MFC-L3770CDW"
        assert device2.vendor_id == "04f9"
        assert device2.product_id == "0366"

    def test_scan_network_devices(self, detector_with_mocks):
        """Test: Netzwerk-Geräte scannen"""
        detector, _, mock_avahi = detector_with_mocks

        devices = detector.scan_network()

        # avahi-browse sollte aufgerufen worden sein
        mock_avahi.assert_called_once()

        # 2 Netzwerk-Geräte sollten erkannt worden sein
        # (1x _printer._tcp, 1x _ipp._tcp vom selben physischen Gerät)
        assert len(devices) == 2

        # Erstes Gerät prüfen (printer service)
        device1 = devices[0]
        assert device1.manufacturer == "Brother"
        assert device1.model == "MFC-L2700DN"
        assert device1.connection_type == ConnectionType.NETWORK
        assert device1.ip_address == "192.168.1.100"
        assert device1.hostname == "BRN001BA9123456.local"
        assert "socket://" in device1.connection_uri

        # Zweites Gerät prüfen (IPP service)
        device2 = devices[1]
        assert device2.manufacturer == "Brother"
        assert device2.model == "MFC-L2700DN"
        assert device2.connection_type == ConnectionType.NETWORK
        assert "ipp://" in device2.connection_uri

    def test_scan_all_devices(self, detector_with_mocks):
        """Test: Alle Geräte scannen"""
        detector, mock_lsusb, mock_avahi = detector_with_mocks

        devices = detector.scan_all()

        # Beide Commands sollten aufgerufen worden sein
        mock_lsusb.assert_called_once()
        mock_avahi.assert_called_once()

        # 2 USB + 2 Netzwerk = 4 Geräte
        assert len(devices) == 4

    def test_scan_usb_no_output(self, mock_logger):
        """Test: USB-Scan ohne Ausgabe"""
        mock_lsusb = MagicMock(return_value="")
        detector = HardwareDetector(logger=mock_logger, lsusb_command=mock_lsusb)

        devices = detector.scan_usb()

        assert len(devices) == 0

    def test_scan_network_no_output(self, mock_logger):
        """Test: Netzwerk-Scan ohne Ausgabe"""
        mock_avahi = MagicMock(return_value="")
        detector = HardwareDetector(logger=mock_logger, avahi_command=mock_avahi)

        devices = detector.scan_network()

        assert len(devices) == 0

    def test_identify_unknown_usb_vendor(self, detector_with_mocks):
        """Test: Unbekannter USB-Hersteller"""
        detector, _, _ = detector_with_mocks

        # HP Vendor ID (nicht implementiert)
        device = detector._identify_usb_device("03f0", "1234", "HP LaserJet")

        assert device is None

    def test_identify_unknown_brother_product(self, detector_with_mocks):
        """Test: Unbekanntes Brother-Produkt"""
        detector, _, _ = detector_with_mocks

        # Brother Vendor ID, aber unbekannte Product ID
        device = detector._identify_brother_device("04f9", "9999", "Brother Unknown")

        assert device is None

    def test_get_device_by_uri(self, detector_with_mocks):
        """Test: Gerät anhand URI finden"""
        detector, _, _ = detector_with_mocks

        # Suche nach USB-Gerät
        device = detector.get_device_by_uri("usb://Brother/MFC-L2700DN?serial=unknown")

        assert device is not None
        assert device.manufacturer == "Brother"
        assert device.model == "MFC-L2700DN"

    def test_get_device_by_uri_not_found(self, detector_with_mocks):
        """Test: Gerät nicht gefunden"""
        detector, _, _ = detector_with_mocks

        device = detector.get_device_by_uri("usb://HP/LaserJet")

        assert device is None

    def test_is_device_connected_usb(self, detector_with_mocks):
        """Test: USB-Gerät ist verbunden"""
        detector, _, _ = detector_with_mocks

        # Erstelle Device-Objekt
        from tipels.core.device import Device

        device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            vendor_id="04f9",
            product_id="0273",
        )

        # Gerät sollte verbunden sein (in Mock-Ausgabe enthalten)
        assert detector.is_device_connected(device) is True

    def test_is_device_not_connected_usb(self, detector_with_mocks):
        """Test: USB-Gerät ist nicht verbunden"""
        detector, _, _ = detector_with_mocks

        from tipels.core.device import Device

        device = Device(
            manufacturer="HP",
            model="LaserJet",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://HP/LaserJet",
            vendor_id="03f0",
            product_id="1234",
        )

        # Gerät sollte nicht verbunden sein
        assert detector.is_device_connected(device) is False

    def test_is_device_connected_network(self, detector_with_mocks):
        """Test: Netzwerk-Gerät ist verbunden"""
        detector, _, _ = detector_with_mocks

        from tipels.core.device import Device

        device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.NETWORK,
            connection_uri="ipp://192.168.1.100",
            ip_address="192.168.1.100",
        )

        # Gerät sollte verbunden sein (in Mock-Ausgabe enthalten)
        assert detector.is_device_connected(device) is True

    def test_is_device_not_connected_network(self, detector_with_mocks):
        """Test: Netzwerk-Gerät ist nicht verbunden"""
        detector, _, _ = detector_with_mocks

        from tipels.core.device import Device

        device = Device(
            manufacturer="HP",
            model="LaserJet",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.NETWORK,
            connection_uri="ipp://192.168.1.200",
            ip_address="192.168.1.200",
        )

        # Gerät sollte nicht verbunden sein
        assert detector.is_device_connected(device) is False

    def test_network_device_identification_no_model(self, detector_with_mocks):
        """Test: Netzwerk-Gerät ohne erkennbares Modell"""
        detector, _, _ = detector_with_mocks

        # Service-Name ohne erkennbares Modell
        device = detector._identify_network_device(
            service_name="Brother Printer",
            hostname="brother.local",
            ip_address="192.168.1.100",
            port="9100",
            service_type="_printer._tcp",
        )

        # Sollte None zurückgeben (kein Modell erkannt)
        assert device is None

    def test_network_device_ipp_uri(self, detector_with_mocks):
        """Test: Netzwerk-Gerät IPP URI"""
        detector, _, _ = detector_with_mocks

        device = detector._identify_network_device(
            service_name="Brother MFC-L2700DN series",
            hostname="brother.local",
            ip_address="192.168.1.100",
            port="631",
            service_type="_ipp._tcp",
        )

        assert device is not None
        assert device.connection_uri == "ipp://192.168.1.100:631/ipp/print"

    def test_network_device_socket_uri(self, detector_with_mocks):
        """Test: Netzwerk-Gerät Socket URI"""
        detector, _, _ = detector_with_mocks

        device = detector._identify_network_device(
            service_name="Brother MFC-L2700DN series",
            hostname="brother.local",
            ip_address="192.168.1.100",
            port="9100",
            service_type="_printer._tcp",
        )

        assert device is not None
        assert device.connection_uri == "socket://192.168.1.100:9100"
