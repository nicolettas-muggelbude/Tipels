# Tipels - Icons und Logos

Dieses Verzeichnis enthält alle Icons und Logos für Tipels.

## Dateien

### SVG (Vektor-Format)
- **tipels-logo.svg** - Vollständiges Logo mit Text und Hühnerfußabdrücken
- **tipels-icon.svg** - Vereinfachtes Icon (ohne Text) für Desktop-Integration

### PNG (Raster-Format)
PNG-Icons in verschiedenen Größen werden aus den SVG-Dateien generiert.

## Logo-Konzept

Das Tipels-Logo zeigt **Hühnerfußabdrücke**, die zum Drucker führen:

- **"Tipels"** = kleine Schritte/Füßchen (tipeln)
- **Hühnerfußspuren** = symbolisieren den einfachen Weg zur Drucker-/Scanner-Einrichtung
- **Drucker-Symbol** = das Ziel der Installation
- **Farbschema**: Blau-Töne (vertrauenswürdig, technisch, professionell)

## PNG-Icons generieren

```bash
# Installiere inkscape oder imagemagick
sudo apt install inkscape
# oder
sudo apt install imagemagick

# Generiere PNGs
./generate-pngs.sh
```

Dies erstellt Icons in folgenden Größen:
- 16x16 (Menü)
- 22x22 (Panel)
- 24x24 (Panel)
- 32x32 (Liste)
- 48x48 (Desktop)
- 64x64 (Dialog)
- 128x128 (Einstellungen)
- 256x256 (High-DPI)
- 512x512 (Extra High-DPI)

## Verwendung

### In der Anwendung
```python
from pathlib import Path

ICON_PATH = Path(__file__).parent / "data" / "icons" / "tipels-icon.svg"
```

### In .desktop-Datei
```ini
Icon=tipels
```

### In Dokumentation
```markdown
![Tipels Logo](data/icons/tipels-logo.svg)
```

## Lizenz

Die Icons sind Teil von Tipels und unterliegen der GPLv3-Lizenz.

---

**Design**: Hühnerfußabdrücke führen zum Drucker - einfach wie Tipels! 🐔➡️🖨️
