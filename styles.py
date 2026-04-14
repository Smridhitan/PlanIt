# ── Design Tokens & Style Configuration ──

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ── Fonts ──
FONT_FAMILY  = "Helvetica"
FONT_HEADING = (FONT_FAMILY, 20, "bold")
FONT_SUBHEAD = (FONT_FAMILY, 14, "bold")
FONT_BODY    = (FONT_FAMILY, 11)
FONT_SMALL   = (FONT_FAMILY, 9)
FONT_NAV     = (FONT_FAMILY, 12)
FONT_NAV_ACT = (FONT_FAMILY, 12, "bold")

# ── Spacing ──
PAD_SM = 8
PAD_MD = 16
PAD_LG = 32
SIDEBAR_WIDTH = 210

def apply_theme_styles(is_dark=False):
    """Apply theme dynamically and register custom widget styles globally."""
    style = tb.Style()
    
    theme_name = "darkly" if is_dark else "cosmo"
    if theme_name in style.theme_names():
        style.theme_use(theme_name)

    accent_color = style.colors.primary

    # Sidebar nav buttons (inactive)
    style.configure("Nav.TButton",
        font=FONT_NAV,
        padding=(PAD_MD, 12),
        anchor="w",
        relief="flat",
        borderwidth=0,
    )

    # Active nav button
    style.configure("NavActive.TButton",
        font=FONT_NAV_ACT,
        padding=(PAD_MD, 12),
        anchor="w",
        relief="flat",
        borderwidth=0,
    )

    # Panel headings
    style.configure("Heading.TLabel", font=FONT_HEADING)
    style.configure("Subheading.TLabel", font=FONT_SUBHEAD)
    style.configure("Muted.TLabel", font=FONT_SMALL, foreground=style.colors.secondary)

    # Form label
    style.configure("Form.TLabel", font=FONT_BODY)
