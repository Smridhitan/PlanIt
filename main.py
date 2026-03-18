import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from styles import (
    apply_theme_styles, PAD_SM, PAD_MD, PAD_LG, SIDEBAR_WIDTH,
    FONT_HEADING, FONT_SMALL
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
        # We start in Light form
        self.is_dark = False
        self.root = tb.Window(themename="cosmo", title="PlanIt — Event Organizer", size=(960, 580))
        self.root.minsize(800, 500)
        apply_theme_styles(self.is_dark)

        self.active_nav = None
        self.nav_buttons = {}
        self.content_area = None
        self.theme_btn = None

        self._build_layout()
        # Show first panel by default
        self._switch_panel(NAV_ITEMS[0][0])
        self.root.mainloop()

    def _toggle_theme(self):
        """Switch between Light (cosmo) and Dark (darkly) modes live."""
        self.is_dark = not self.is_dark
        apply_theme_styles(self.is_dark)
        
        # Ensure our frame and notebook redraw completely!
        self.theme_btn.configure(text="☀️  Light Mode" if self.is_dark else "🌙  Dark Mode")
        
        # A hard refresh of the current panel ensures Treeview colors update smoothly.
        if self.active_nav:
            k = self.active_nav
            self.active_nav = None # flush state to force a redraw
            self._switch_panel(k)


    # ── Layout ──
    def _build_layout(self):
        # Sidebar using standard tb defaults instead of forced hex bg
        sidebar = tb.Frame(self.root, width=SIDEBAR_WIDTH)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        # App brand
        brand = tb.Label(sidebar, text="PlanIt", font=FONT_HEADING, bootstyle="primary", anchor="w")
        brand.pack(fill=X, padx=PAD_LG, pady=(PAD_LG, PAD_SM))

        tagline = tb.Label(sidebar, text="Event Organizer", style="Muted.TLabel", anchor="w")
        tagline.pack(fill=X, padx=PAD_LG, pady=(0, PAD_LG))

        # Separator
        sep = tb.Separator(sidebar, orient=HORIZONTAL)
        sep.pack(fill=X, padx=PAD_MD, pady=(0, PAD_MD))

        # Nav buttons
        for key, label, _ in NAV_ITEMS:
            btn = tb.Button(
                sidebar, text=f"  {label}", style="Nav.TButton",
                command=lambda k=key: self._switch_panel(k),
            )
            btn.pack(fill=X, padx=PAD_SM, pady=2)
            self.nav_buttons[key] = btn

        # Theme toggle button
        self.theme_btn = tb.Button(
            sidebar, text="🌙  Dark Mode", style="Nav.TButton",
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side=BOTTOM, fill=X, padx=PAD_SM, pady=(0, PAD_MD))

        # Footer
        footer = tb.Label(sidebar, text="MySQL • Connected", style="Muted.TLabel")
        footer.pack(side=BOTTOM, pady=PAD_MD)

        # Content area
        # Put inside a primary dark/light frame
        self.content_area = tb.Frame(self.root)
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
