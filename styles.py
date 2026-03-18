# ── Design Tokens & Style Configuration ──
# Single source of truth for the app's visual language.

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ── Colors ──
BG_SIDEBAR   = "#f1f5f9"   # slate-100
BG_CONTENT   = "#ffffff"
BG_HEADER    = "#ffffff"
ACCENT       = "#3b82f6"   # blue-500
ACCENT_HOVER = "#2563eb"   # blue-600
TEXT_PRIMARY  = "#1e293b"   # slate-800
TEXT_MUTED    = "#94a3b8"   # slate-400
BORDER       = "#e2e8f0"   # slate-200
SUCCESS      = "#22c55e"
WARNING      = "#f59e0b"
DANGER       = "#ef4444"

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
SIDEBAR_WIDTH = 200

def configure_styles():
    """Apply the cosmo theme and register custom widget styles."""
    style = tb.Style()
    if "cosmo" in style.theme_names():
        style.theme_use("cosmo")

    # Sidebar nav buttons (inactive)
    style.configure("Nav.TButton",
        font=FONT_NAV,
        padding=(PAD_MD, 12),
        anchor="w",
        relief="flat",
        borderwidth=0,
    )
    style.map("Nav.TButton",
        background=[("active", BORDER)],
    )

    # Active nav button
    style.configure("NavActive.TButton",
        font=FONT_NAV_ACT,
        padding=(PAD_MD, 12),
        anchor="w",
        relief="flat",
        borderwidth=0,
        foreground=ACCENT,
    )
    style.map("NavActive.TButton",
        background=[("active", BORDER)],
    )

    # Panel heading
    style.configure("Heading.TLabel", font=FONT_HEADING, foreground=TEXT_PRIMARY)
    style.configure("Subheading.TLabel", font=FONT_SUBHEAD, foreground=TEXT_PRIMARY)
    style.configure("Muted.TLabel", font=FONT_SMALL, foreground=TEXT_MUTED)

    # Form label
    style.configure("Form.TLabel", font=FONT_BODY, foreground=TEXT_PRIMARY)

    return style
