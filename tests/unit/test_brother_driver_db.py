"""
Tests für Brother Treiber-Datenbank
"""

import pytest

from tipels.drivers.brother.driver_db import (
    BROTHER_DRIVERS,
    MODEL_DRIVER_MAPPING,
    DriverSource,
    DriverType,
    get_driver_info,
    get_recommended_driver,
    get_scanner_driver,
)


class TestDriverDatabase:
    """Tests für Treiber-Datenbank"""

    def test_brlaser_driver_exists(self):
        """Test: brlaser-Treiber existiert in Datenbank"""
        assert "brlaser" in BROTHER_DRIVERS

        driver = BROTHER_DRIVERS["brlaser"]
        assert driver.name == "brlaser"
        assert driver.driver_type == DriverType.OPENSOURCE
        assert driver.source == DriverSource.REPOSITORY
        assert driver.package_name == "printer-driver-brlaser"
        assert driver.requires_non_free is False

    def test_brscan4_driver_exists(self):
        """Test: brscan4-Treiber existiert in Datenbank"""
        assert "brscan4" in BROTHER_DRIVERS

        driver = BROTHER_DRIVERS["brscan4"]
        assert driver.name == "brscan4"
        assert driver.driver_type == DriverType.OPENSOURCE
        assert driver.source == DriverSource.REPOSITORY
        assert driver.package_name == "brscan4"

    def test_brother_official_drivers_exist(self):
        """Test: Brother Official Drivers existieren"""
        assert "brother-lpr" in BROTHER_DRIVERS
        assert "brother-cups-wrapper" in BROTHER_DRIVERS

        lpr = BROTHER_DRIVERS["brother-lpr"]
        assert lpr.driver_type == DriverType.OFFICIAL
        assert lpr.source == DriverSource.BROTHER_WEBSITE

    def test_brlaser_supported_models(self):
        """Test: brlaser unterstützt MFC-L2700 Modelle"""
        driver = BROTHER_DRIVERS["brlaser"]

        # MFC-L2700.* sollte in supported_models sein
        assert any("MFC-L2700" in model for model in driver.supported_models)

    def test_model_driver_mapping_mfc_l2700dn(self):
        """Test: MFC-L2700DN hat korrektes Mapping"""
        assert "MFC-L2700DN" in MODEL_DRIVER_MAPPING

        mapping = MODEL_DRIVER_MAPPING["MFC-L2700DN"]
        assert mapping["preferred"] == "brlaser"
        assert "brother-lpr" in mapping["alternatives"]
        assert mapping["scanner"] == "brscan4"

    def test_get_recommended_driver_opensource(self):
        """Test: Empfohlener Treiber mit Open-Source-Präferenz"""
        driver = get_recommended_driver("MFC-L2700DN", prefer_opensource=True)

        assert driver == "brlaser"

    def test_get_recommended_driver_color_printer(self):
        """Test: Farb-Drucker bekommt brother-lpr (kein brlaser)"""
        driver = get_recommended_driver("MFC-L3770CDW", prefer_opensource=True)

        # Farb-Laser: brother-lpr bevorzugt (kein brlaser-Support)
        assert driver == "brother-lpr"

    def test_get_recommended_driver_unknown_model(self):
        """Test: Unbekanntes Modell gibt None zurück"""
        driver = get_recommended_driver("UNKNOWN-MODEL")

        assert driver is None

    def test_get_scanner_driver(self):
        """Test: Scanner-Treiber abrufen"""
        scanner_driver = get_scanner_driver("MFC-L2700DN")

        assert scanner_driver == "brscan4"

    def test_get_scanner_driver_unknown_model(self):
        """Test: Unbekanntes Modell gibt None für Scanner zurück"""
        scanner_driver = get_scanner_driver("UNKNOWN-MODEL")

        assert scanner_driver is None

    def test_get_driver_info(self):
        """Test: Treiber-Informationen abrufen"""
        info = get_driver_info("brlaser")

        assert info is not None
        assert info.name == "brlaser"
        assert info.driver_type == DriverType.OPENSOURCE
        assert info.package_name == "printer-driver-brlaser"

    def test_get_driver_info_unknown(self):
        """Test: Unbekannter Treiber gibt None zurück"""
        info = get_driver_info("unknown-driver")

        assert info is None

    def test_all_drivers_have_valid_types(self):
        """Test: Alle Treiber haben gültige Typen"""
        for driver_name, driver in BROTHER_DRIVERS.items():
            assert isinstance(driver.driver_type, DriverType)
            assert isinstance(driver.source, DriverSource)
            assert driver.name == driver_name

    def test_repository_drivers_have_package_names(self):
        """Test: Repository-Treiber haben package_name"""
        for driver in BROTHER_DRIVERS.values():
            if driver.source == DriverSource.REPOSITORY:
                assert driver.package_name is not None
                assert len(driver.package_name) > 0

    def test_official_drivers_have_download_url(self):
        """Test: Official Drivers haben download_url"""
        for driver in BROTHER_DRIVERS.values():
            if driver.driver_type == DriverType.OFFICIAL:
                assert driver.download_url is not None
                assert "brother.com" in driver.download_url

    def test_all_models_have_preferred_driver(self):
        """Test: Alle Modelle haben bevorzugten Treiber"""
        for model, mapping in MODEL_DRIVER_MAPPING.items():
            assert "preferred" in mapping
            preferred = mapping["preferred"]
            assert preferred in BROTHER_DRIVERS

    def test_all_multifunction_models_have_scanner_driver(self):
        """Test: Alle MFC-Modelle haben Scanner-Treiber"""
        for model, mapping in MODEL_DRIVER_MAPPING.items():
            if model.startswith("MFC-"):
                assert "scanner" in mapping
                scanner = mapping["scanner"]
                assert scanner in BROTHER_DRIVERS
