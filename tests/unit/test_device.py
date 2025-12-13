"""
Tests für Device-Datenklassen
"""

import pytest
from tipels.core.device import (
    Device,
    Printer,
    Scanner,
    DeviceType,
    ConnectionType,
    DeviceStatus,
)


class TestDevice:
    """Tests für Device-Klasse"""

    def test_device_creation(self):
        """Test: Device erstellen"""
        device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            vendor_id="04f9",
            product_id="0273",
        )

        assert device.manufacturer == "Brother"
        assert device.model == "MFC-L2700DN"
        assert device.device_type == DeviceType.MULTIFUNCTION
        assert device.connection_type == ConnectionType.USB
        assert device.vendor_id == "04f9"
        assert device.product_id == "0273"
        assert device.status == DeviceStatus.DETECTED
        assert device.supported is True  # Default
        assert device.support_url is None

    def test_device_str(self):
        """Test: Device String-Repräsentation"""
        device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
        )

        assert str(device) == "Brother MFC-L2700DN (usb)"

    def test_device_get_full_name(self):
        """Test: Device vollständiger Name"""
        device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
        )

        assert device.get_full_name() == "Brother MFC-L2700DN"

    def test_device_is_usb(self):
        """Test: Device ist USB"""
        usb_device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
        )

        assert usb_device.is_usb() is True

        network_device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.NETWORK,
            connection_uri="ipp://192.168.1.100",
        )

        assert network_device.is_usb() is False

    def test_device_is_network(self):
        """Test: Device ist Netzwerk"""
        network_device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.NETWORK,
            connection_uri="ipp://192.168.1.100",
            ip_address="192.168.1.100",
        )

        assert network_device.is_network() is True

    def test_device_is_configured(self):
        """Test: Device ist konfiguriert"""
        detected_device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            status=DeviceStatus.DETECTED,
        )

        assert detected_device.is_configured() is False

        configured_device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            status=DeviceStatus.CONFIGURED,
        )

        assert configured_device.is_configured() is True

        ready_device = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            status=DeviceStatus.READY,
        )

        assert ready_device.is_configured() is True

    def test_device_is_printer(self):
        """Test: Device ist Drucker"""
        printer = Device(
            manufacturer="Brother",
            model="HL-L2350DW",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/HL-L2350DW",
        )

        assert printer.is_printer() is True

        multifunction = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
        )

        assert multifunction.is_printer() is True

        scanner = Device(
            manufacturer="Brother",
            model="ADS-2700W",
            device_type=DeviceType.SCANNER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/ADS-2700W",
        )

        assert scanner.is_printer() is False

    def test_device_is_scanner(self):
        """Test: Device ist Scanner"""
        scanner = Device(
            manufacturer="Brother",
            model="ADS-2700W",
            device_type=DeviceType.SCANNER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/ADS-2700W",
        )

        assert scanner.is_scanner() is True

        multifunction = Device(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
        )

        assert multifunction.is_scanner() is True

    def test_unsupported_device(self):
        """Test: Nicht unterstütztes Gerät"""
        device = Device(
            manufacturer="HP",
            model="LaserJet Pro M404dn",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://HP/LaserJet",
            vendor_id="03f0",
            product_id="1234",
            supported=False,
            support_url="https://github.com/nicolettas-muggelbude/Tipels/issues/new?template=hardware_support.yml",
        )

        assert device.supported is False
        assert device.support_url is not None
        assert "github.com" in device.support_url
        assert "hardware_support" in device.support_url


class TestPrinter:
    """Tests für Printer-Klasse"""

    def test_printer_creation(self):
        """Test: Printer erstellen"""
        printer = Printer(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            supports_color=False,
            supports_duplex=True,
            max_paper_size="A4",
        )

        assert printer.supports_color is False
        assert printer.supports_duplex is True
        assert printer.max_paper_size == "A4"

    def test_printer_with_scanner_type_fails(self):
        """Test: Printer kann nicht vom Typ SCANNER sein"""
        with pytest.raises(ValueError, match="Printer kann nicht vom Typ SCANNER sein"):
            Printer(
                manufacturer="Brother",
                model="ADS-2700W",
                device_type=DeviceType.SCANNER,
                connection_type=ConnectionType.USB,
                connection_uri="usb://Brother/ADS-2700W",
            )

    def test_printer_toner_level(self):
        """Test: Printer Toner-Level"""
        printer = Printer(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.PRINTER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            toner_level=75,
        )

        assert printer.toner_level == 75


class TestScanner:
    """Tests für Scanner-Klasse"""

    def test_scanner_creation(self):
        """Test: Scanner erstellen"""
        scanner = Scanner(
            manufacturer="Brother",
            model="ADS-2700W",
            device_type=DeviceType.SCANNER,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/ADS-2700W",
            supports_adf=True,
            max_scan_size="A4",
            max_resolution=1200,
        )

        assert scanner.supports_adf is True
        assert scanner.max_scan_size == "A4"
        assert scanner.max_resolution == 1200

    def test_scanner_with_printer_type_fails(self):
        """Test: Scanner kann nicht vom Typ PRINTER sein"""
        with pytest.raises(ValueError, match="Scanner kann nicht vom Typ PRINTER sein"):
            Scanner(
                manufacturer="Brother",
                model="HL-L2350DW",
                device_type=DeviceType.PRINTER,
                connection_type=ConnectionType.USB,
                connection_uri="usb://Brother/HL-L2350DW",
            )

    def test_scanner_multifunction(self):
        """Test: Scanner als Multifunktionsgerät"""
        scanner = Scanner(
            manufacturer="Brother",
            model="MFC-L2700DN",
            device_type=DeviceType.MULTIFUNCTION,
            connection_type=ConnectionType.USB,
            connection_uri="usb://Brother/MFC-L2700DN",
            supports_adf=True,
        )

        assert scanner.device_type == DeviceType.MULTIFUNCTION
        assert scanner.is_scanner() is True
