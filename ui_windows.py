import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from database import Database
from styles import PAD_SM, PAD_MD, PAD_LG

db = Database()

def format_error(e):
    """Convert raw system/database errors into user-friendly messages."""
    msg = str(e).lower()
    if "1045" in msg or "access denied" in msg:
        return "Access denied. Please check database credentials."
    elif "1049" in msg or "unknown database" in msg:
        return "Database not found. Ensure 'Dbms_Project' exists."
    elif "2003" in msg or "can't connect" in msg:
        return "Could not connect. Is the MySQL server running locally?"
    elif "1062" in msg or "duplicate entry" in msg:
        return "Duplicate entry. This record already exists."
    elif "1452" in msg or "foreign key constraint" in msg:
        return "Invalid reference. Ensure the Venue or Resource ID exists."
    elif "invalid literal for int" in msg or "invalid int" in msg:
        return "Please enter a valid whole number for quantities or IDs."
    return "An unexpected database error occurred. Try again."

# ── Helpers ──

def _labeled_field(parent, label, row, widget_factory):
    """Create a label + widget pair on a grid row."""
    tb.Label(parent, text=label, style="Form.TLabel").grid(
        row=row, column=0, sticky=W, pady=PAD_SM, padx=(0, PAD_MD)
    )
    widget = widget_factory(parent)
    widget.grid(row=row, column=1, sticky=EW, pady=PAD_SM)
    return widget

def _entry(parent, placeholder=""):
    e = tb.Entry(parent, width=30)
    if placeholder:
        e.insert(0, placeholder)
    return e

def _section_header(parent, title, subtitle=None):
    """Render a clean section header."""
    tb.Label(parent, text=title, style="Heading.TLabel").pack(anchor=W, pady=(0, 4))
    if subtitle:
        tb.Label(parent, text=subtitle, style="Muted.TLabel").pack(anchor=W, pady=(0, PAD_LG))
    else:
        # spacing
        tb.Frame(parent, height=PAD_MD).pack()

# ═══════════════════════════════════════════
#  EVENT PANEL
# ═══════════════════════════════════════════

def build_event_panel(parent):
    panel = tb.Frame(parent)

    _section_header(panel, "Create New Event", "Fill in the details below to register an event.")

    form = tb.Frame(panel)
    form.pack(fill=X)
    form.columnconfigure(1, weight=1)

    entry_name  = _labeled_field(form, "Event Name", 0, lambda p: _entry(p))
    entry_type  = _labeled_field(form, "Event Type", 1,
        lambda p: tb.Combobox(p, width=28, state="readonly",
            values=["Workshop", "Performance", "Panel Discussion", "Keynote Talk", "Seminar", "Other"]))
    entry_type.current(0)

    entry_start = _labeled_field(form, "Start Date", 2, lambda p: _entry(p, "YYYY-MM-DD"))
    entry_end   = _labeled_field(form, "End Date",   3, lambda p: _entry(p, "YYYY-MM-DD"))
    entry_fees  = _labeled_field(form, "Fees",       4, lambda p: _entry(p, "0.00"))
    entry_venue = _labeled_field(form, "Venue ID",   5, lambda p: _entry(p, "1"))

    # Status feedback label
    status_var = tk.StringVar(value="")
    status_lbl = tb.Label(panel, textvariable=status_var, style="Muted.TLabel")
    status_lbl.pack(anchor=W, pady=(PAD_MD, 0))

    def submit():
        try:
            db.add_event(
                entry_name.get(), entry_type.get(),
                entry_start.get(), entry_end.get(),
                entry_fees.get(), entry_venue.get()
            )
            status_var.set("✓  Event created successfully.")
            status_lbl.configure(bootstyle="success")
        except Exception as e:
            status_var.set(f"✕  {format_error(e)}")
            status_lbl.configure(bootstyle="danger")

    btn_frame = tb.Frame(panel)
    btn_frame.pack(anchor=W, pady=PAD_LG)
    tb.Button(btn_frame, text="Submit Event", command=submit, bootstyle="primary", width=18).pack(side=LEFT)

    return panel

# ═══════════════════════════════════════════
#  RESOURCE PANEL
# ═══════════════════════════════════════════

def build_resource_panel(parent):
    panel = tb.Frame(parent)

    _section_header(panel, "Allocate Resources", "Allocate inventory and observe the database trigger in action.")

    form = tb.Frame(panel)
    form.pack(fill=X)
    form.columnconfigure(1, weight=1)

    entry_session  = _labeled_field(form, "Session ID",  0, lambda p: _entry(p))
    entry_resource = _labeled_field(form, "Resource ID", 1, lambda p: _entry(p))
    entry_qty      = _labeled_field(form, "Quantity",    2, lambda p: _entry(p))

    # Trigger result card
    result_frame = tb.Labelframe(panel, text="Trigger Output", padding=PAD_MD)
    result_frame.pack(fill=X, pady=PAD_LG)

    result_var = tk.StringVar(value="Waiting for allocation…")
    result_lbl = tb.Label(result_frame, textvariable=result_var, style="Muted.TLabel", justify=LEFT)
    result_lbl.pack(anchor=W)

    def allocate():
        try:
            sid = entry_session.get()
            rid = entry_resource.get()
            qty = int(entry_qty.get())
            before, after = db.allocate_resource(sid, rid, qty)

            result_var.set(
                f"Trigger executed successfully.\n\n"
                f"Stock before:   {before}\n"
                f"Allocated:       {qty}\n"
                f"Stock after:     {after}"
            )
            result_lbl.configure(bootstyle="success")
        except Exception as e:
            result_var.set(f"✕  Allocation failed: {format_error(e)}")
            result_lbl.configure(bootstyle="danger")

    tb.Button(panel, text="Confirm Allocation", command=allocate, bootstyle="warning", width=20).pack(anchor=W, pady=(0, PAD_SM))

    return panel

# ═══════════════════════════════════════════
#  ANALYTICS DASHBOARD PANEL
# ═══════════════════════════════════════════

def build_view_panel(parent):
    panel = tb.Frame(parent)

    _section_header(panel, "Analytics Dashboard", "Browse event and resource records from the database.")

    notebook = tb.Notebook(panel)
    notebook.pack(fill=BOTH, expand=True)

    # ── Events tab ──
    tab_events = tb.Frame(notebook, padding=PAD_SM)
    notebook.add(tab_events, text="  Events  ")

    ev_cols = ("ID", "Event Name", "Start Date", "End Date")
    tree_ev = tb.Treeview(tab_events, columns=ev_cols, show="headings", height=14)
    for c in ev_cols:
        tree_ev.heading(c, text=c)
        tree_ev.column(c, anchor=CENTER, width=150)
    tree_ev.pack(fill=BOTH, expand=True)

    scroll_ev = tb.Scrollbar(tab_events, orient=VERTICAL, command=tree_ev.yview)
    tree_ev.configure(yscrollcommand=scroll_ev.set)
    scroll_ev.place(relx=1.0, rely=0, relheight=1.0, anchor=NE)

    try:
        for row in db.get_events():
            tree_ev.insert("", END, values=row)
    except Exception as e:
        tb.Label(tab_events, text=f"Could not load events: {format_error(e)}", bootstyle="danger").pack(pady=20)

    # ── Resources tab ──
    tab_res = tb.Frame(notebook, padding=PAD_SM)
    notebook.add(tab_res, text="  Resources  ")

    res_cols = ("ID", "Resource Name", "Available Qty")
    tree_res = tb.Treeview(tab_res, columns=res_cols, show="headings", height=14)
    for c in res_cols:
        tree_res.heading(c, text=c)
        tree_res.column(c, anchor=CENTER, width=180)
    tree_res.pack(fill=BOTH, expand=True)

    scroll_res = tb.Scrollbar(tab_res, orient=VERTICAL, command=tree_res.yview)
    tree_res.configure(yscrollcommand=scroll_res.set)
    scroll_res.place(relx=1.0, rely=0, relheight=1.0, anchor=NE)

    try:
        for row in db.get_resources():
            tree_res.insert("", END, values=row)
    except Exception as e:
        tb.Label(tab_res, text=f"Could not load resources: {format_error(e)}", bootstyle="danger").pack(pady=20)

    return panel
