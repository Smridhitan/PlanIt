import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from styles import (
    configure_styles, BG_SIDEBAR, BG_CONTENT, BORDER,
    TEXT_MUTED, ACCENT, PAD_SM, PAD_MD, PAD_LG, SIDEBAR_WIDTH,
    FONT_HEADING, FONT_SMALL, FONT_NAV
)
from ui_windows import build_event_panel, build_resource_panel, build_view_panel

# ── Navigation items ──
NAV_ITEMS = [
    ("Events",     "Add Event",            build_event_panel),
    ("Resources",  "Allocate Resources",   build_resource_panel),
    ("Dashboard",  "Analytics Dashboard",  build_view_panel),
]

class App:
    def __init__(self):
        self.root = tb.Window(themename="cosmo", title="PlanIt — Event Organizer", size=(960, 580))
        self.root.minsize(800, 500)
        configure_styles()

        self.active_nav = None
        self.nav_buttons = {}
        self.content_area = None

        self._build_layout()
        # Show first panel by default
        self._switch_panel(NAV_ITEMS[0][0])
        self.root.mainloop()

    # ── Layout ──
    def _build_layout(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=SIDEBAR_WIDTH)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        # App brand
        brand = tk.Label(sidebar, text="PlanIt", font=FONT_HEADING, bg=BG_SIDEBAR, fg=ACCENT, anchor="w")
        brand.pack(fill=X, padx=PAD_LG, pady=(PAD_LG, PAD_SM))

        tagline = tk.Label(sidebar, text="Event Organizer", font=FONT_SMALL, bg=BG_SIDEBAR, fg=TEXT_MUTED, anchor="w")
        tagline.pack(fill=X, padx=PAD_LG, pady=(0, PAD_LG))

        # Separator
        sep = tk.Frame(sidebar, height=1, bg=BORDER)
        sep.pack(fill=X, padx=PAD_MD, pady=(0, PAD_MD))

        # Nav buttons
        for key, label, _ in NAV_ITEMS:
            btn = tb.Button(
                sidebar, text=f"  {label}", style="Nav.TButton",
                command=lambda k=key: self._switch_panel(k),
            )
            btn.pack(fill=X, padx=PAD_SM, pady=2)
            self.nav_buttons[key] = btn

        # Footer
        footer = tk.Label(sidebar, text="MySQL • Connected", font=FONT_SMALL, bg=BG_SIDEBAR, fg=TEXT_MUTED)
        footer.pack(side=BOTTOM, pady=PAD_MD)

        # Content area
        self.content_area = tk.Frame(self.root, bg=BG_CONTENT)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True)

    # ── Panel switching ──
    def _switch_panel(self, key):
        if self.active_nav == key:
            return

        # Update nav highlight
        if self.active_nav and self.active_nav in self.nav_buttons:
            self.nav_buttons[self.active_nav].configure(style="Nav.TButton")
        self.nav_buttons[key].configure(style="NavActive.TButton")
        self.active_nav = key

        # Clear content area
        for child in self.content_area.winfo_children():
            child.destroy()

        # Build new panel
        for nav_key, _, builder in NAV_ITEMS:
            if nav_key == key:
                panel = builder(self.content_area)
                panel.pack(fill=BOTH, expand=True, padx=PAD_LG, pady=PAD_LG)
                break

def main():
    App()

if __name__ == "__main__":
    main()
