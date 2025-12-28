"""
Tipels GTK GUI - Info Dialog

Scrollbares Info-Fenster mit Version, Credits und Beschreibung
"""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from tipels import (
    __authors__,
    __copyright__,
    __description__,
    __documenters__,
    __license__,
    __long_description__,
    __version__,
    __website__,
    __website_label__,
)


class InfoDialog(Gtk.Dialog):
    """
    Scrollbares Info-Fenster mit allen Projekt-Informationen.

    Zeigt Version, Credits, Beschreibung, Lizenz und Website.
    """

    def __init__(self, parent):
        """
        Initialisiert InfoDialog.

        Args:
            parent: Parent-Window
        """
        super().__init__(
            title="Über Tipels", transient_for=parent, modal=True, destroy_with_parent=True
        )

        self.set_default_size(500, 600)
        self.set_border_width(0)

        # Content aufbauen
        self._build_content()

        # Buttons
        self.add_button("Schließen", Gtk.ResponseType.CLOSE)

        self.show_all()

    def _build_content(self):
        """Baut den scrollbaren Content auf."""
        # ScrolledWindow
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(400)

        # Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(30)
        content_box.set_margin_bottom(30)
        content_box.set_margin_start(40)
        content_box.set_margin_end(40)

        # Logo/Icon
        icon = Gtk.Image.new_from_icon_name("printer", Gtk.IconSize.DIALOG)
        icon.set_pixel_size(96)
        content_box.pack_start(icon, False, False, 0)

        # Titel
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>Tipels</span>")
        title.set_halign(Gtk.Align.CENTER)
        content_box.pack_start(title, False, False, 0)

        # Version
        version_label = Gtk.Label()
        version_label.set_markup(f"<span size='large'>Version {__version__}</span>")
        version_label.set_halign(Gtk.Align.CENTER)
        version_label.get_style_context().add_class("dim-label")
        content_box.pack_start(version_label, False, False, 0)

        # Separator
        content_box.pack_start(Gtk.Separator(), False, False, 10)

        # Beschreibung
        desc_label = Gtk.Label()
        desc_label.set_halign(Gtk.Align.CENTER)
        # & muss escaped werden für Markup
        desc_escaped = __description__.replace("&", "&amp;")
        desc_label.set_markup(f"<b>{desc_escaped}</b>")
        content_box.pack_start(desc_label, False, False, 0)

        long_desc_label = Gtk.Label(label=__long_description__)
        long_desc_label.set_halign(Gtk.Align.CENTER)
        long_desc_label.set_line_wrap(True)
        long_desc_label.set_max_width_chars(50)
        long_desc_label.set_justify(Gtk.Justification.CENTER)
        content_box.pack_start(long_desc_label, False, False, 0)

        # Separator
        content_box.pack_start(Gtk.Separator(), False, False, 10)

        # Credits
        credits_frame = Gtk.Frame(label="Credits")
        credits_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        credits_box.set_margin_top(10)
        credits_box.set_margin_bottom(10)
        credits_box.set_margin_start(20)
        credits_box.set_margin_end(20)

        # Autoren
        authors_label = Gtk.Label()
        authors_label.set_markup("<b>Entwickelt von:</b>")
        authors_label.set_halign(Gtk.Align.START)
        credits_box.pack_start(authors_label, False, False, 0)

        for author in __authors__:
            author_label = Gtk.Label(label=f"• {author}")
            author_label.set_halign(Gtk.Align.START)
            author_label.set_margin_start(10)
            credits_box.pack_start(author_label, False, False, 0)

        # Dokumentation
        credits_box.pack_start(Gtk.Box(), False, False, 5)
        docs_label = Gtk.Label()
        docs_label.set_markup("<b>Dokumentation:</b>")
        docs_label.set_halign(Gtk.Align.START)
        credits_box.pack_start(docs_label, False, False, 0)

        for doc in __documenters__:
            doc_label = Gtk.Label(label=f"• {doc}")
            doc_label.set_halign(Gtk.Align.START)
            doc_label.set_margin_start(10)
            credits_box.pack_start(doc_label, False, False, 0)

        credits_frame.add(credits_box)
        content_box.pack_start(credits_frame, False, False, 0)

        # Separator
        content_box.pack_start(Gtk.Separator(), False, False, 10)

        # Copyright
        copyright_label = Gtk.Label(label=__copyright__)
        copyright_label.set_halign(Gtk.Align.CENTER)
        copyright_label.get_style_context().add_class("dim-label")
        content_box.pack_start(copyright_label, False, False, 0)

        # Lizenz
        license_label = Gtk.Label()
        license_label.set_markup(f"<small>Lizenz: {__license__}</small>")
        license_label.set_halign(Gtk.Align.CENTER)
        license_label.get_style_context().add_class("dim-label")
        content_box.pack_start(license_label, False, False, 0)

        # Separator
        content_box.pack_start(Gtk.Separator(), False, False, 10)

        # Website
        website_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        website_box.set_halign(Gtk.Align.CENTER)

        website_icon = Gtk.Image.new_from_icon_name("web-browser-symbolic", Gtk.IconSize.BUTTON)
        website_box.pack_start(website_icon, False, False, 0)

        website_link = Gtk.LinkButton.new_with_label(__website__, __website_label__)
        website_box.pack_start(website_link, False, False, 0)

        content_box.pack_start(website_box, False, False, 0)

        # Content in ScrolledWindow
        scrolled.add(content_box)

        # ScrolledWindow in Dialog Content Area
        content_area = self.get_content_area()
        content_area.pack_start(scrolled, True, True, 0)
