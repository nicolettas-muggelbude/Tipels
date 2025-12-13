"""
Tipels - ASCII Art Banner für CLI
"""

BANNER = r"""
  ╔════════════════════════════════════════╗
  ║                                        ║
  ║   🐔  Tipels  🖨️                       ║
  ║                                        ║
  ║   Drucker & Scanner Setup für Linux   ║
  ║                                        ║
  ║    >  >  >  → 🖨️                       ║
  ║   🐾 🐾 🐾                              ║
  ║                                        ║
  ╚════════════════════════════════════════╝
"""

BANNER_SIMPLE = r"""
╔══════════════════════════════════════╗
║  Tipels - Drucker & Scanner Setup    ║
╚══════════════════════════════════════╝
"""

BANNER_MINIMAL = """
Tipels v{version} - Drucker & Scanner Setup
"""


def get_banner(style="simple", version="0.1.0"):
    """
    Gibt Banner für CLI zurück

    Args:
        style: "full", "simple" oder "minimal"
        version: Version string

    Returns:
        str: Banner-Text
    """
    if style == "full":
        return BANNER
    elif style == "simple":
        return BANNER_SIMPLE
    elif style == "minimal":
        return BANNER_MINIMAL.format(version=version)
    else:
        return BANNER_SIMPLE
