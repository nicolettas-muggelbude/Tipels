#!/bin/bash
# Tipels - System-Dependencies installieren
# Für Ubuntu/Debian/Linux Mint

set -e

echo "================================================"
echo "Tipels - System-Dependencies installieren"
echo "================================================"
echo ""

# Prüfe ob apt verfügbar ist
if ! command -v apt &> /dev/null; then
    echo "FEHLER: apt nicht gefunden. Dieses Skript funktioniert nur auf Debian/Ubuntu-basierten Systemen."
    exit 1
fi

echo "Aktualisiere Paketlisten..."
sudo apt-get update

echo ""
echo "Installiere Python- und GTK-Dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    python3-dbus \
    gir1.2-gtk-3.0

echo ""
echo "Installiere CUPS (Drucker)..."
sudo apt-get install -y \
    cups \
    cups-client \
    printer-driver-brlaser

echo ""
echo "Installiere SANE (Scanner)..."
sudo apt-get install -y \
    sane \
    sane-utils \
    libsane-dev

echo ""
echo "Installiere Netzwerk-Tools..."
sudo apt-get install -y \
    avahi-daemon \
    avahi-utils \
    nmap

echo ""
echo "Installiere Build-Tools (optional, für Entwicklung)..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libcairo2-dev \
    libgirepository1.0-dev

echo ""
echo "================================================"
echo "✓ System-Dependencies erfolgreich installiert!"
echo "================================================"
echo ""
echo "Nächste Schritte:"
echo "  1. Virtual Environment erstellen: python3 -m venv venv"
echo "  2. Aktivieren: source venv/bin/activate"
echo "  3. Python-Pakete installieren: make install-dev"
echo ""
