#!/bin/bash
# Generiere PNG-Icons aus SVG-Logos
# Benötigt: inkscape oder imagemagick (convert)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Generiere PNG-Icons aus SVG..."
echo ""

# Prüfe verfügbare Tools
if command -v inkscape &> /dev/null; then
    TOOL="inkscape"
    echo "Verwende: inkscape"
elif command -v convert &> /dev/null; then
    TOOL="convert"
    echo "Verwende: imagemagick (convert)"
else
    echo "FEHLER: Weder inkscape noch imagemagick (convert) gefunden!"
    echo "Installiere eines der Tools:"
    echo "  sudo apt install inkscape"
    echo "  sudo apt install imagemagick"
    exit 1
fi

echo ""

# Icon-Größen für Linux Desktop
SIZES=(16 22 24 32 48 64 128 256 512)

for size in "${SIZES[@]}"; do
    echo "Generiere ${size}x${size}..."

    if [ "$TOOL" = "inkscape" ]; then
        inkscape tipels-icon.svg \
            --export-type=png \
            --export-filename="tipels-${size}.png" \
            --export-width=$size \
            --export-height=$size
    else
        convert tipels-icon.svg \
            -resize ${size}x${size} \
            tipels-${size}.png
    fi
done

echo ""
echo "✓ PNG-Icons erfolgreich generiert!"
echo ""
echo "Generierte Dateien:"
ls -lh tipels-*.png
