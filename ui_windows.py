import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from database import Database

db = Database()

def create_labeled_entry(parent, label_text, row, placeholder=""):
    tb.Label(parent, text=label_text, font=("Helvetica", 11)).grid(row=row, column=0, sticky=W, pady=12, padx=5)
    entry = tb.Entry(parent, width=35)
    entry.grid(row=row, column=1, sticky=E, pady=12, padx=5)
    if placeholder:
        entry.insert(0, placeholder)
    return entry

def open_event_window(root):
    event_win = tb.Toplevel(root)
    event_win.title("Event Management")
    event_win.geometry("500x520")
    event_win.grab_set()

    frame = tb.Frame(event_win, padding=35)
    frame.pack(fill=BOTH, expand=True)

    tb.Label(frame, text="Create New Event", font=('Helvetica', 18, 'bold'), bootstyle="info").grid(row=0, column=0, columnspan=2, pady=(0, 25))

    entry_name = create_labeled_entry(frame, "Event Name:", 1)
    
    tb.Label(frame, text="Event Type:", font=("Helvetica", 11)).grid(row=2, column=0, sticky=W, pady=12, padx=5)
    entry_type = tb.Combobox(frame, width=33, state="readonly", values=["Workshop", "Performance", "Panel Discussion", "Keynote Talk", "Seminar", "Other"])
    entry_type.current(0)
    entry_type.grid(row=2, column=1, sticky=E, pady=12, padx=5)

    entry_start = create_labeled_entry(frame, "Start Date (YYYY-MM-DD):", 3, "2026-04-01")
    entry_end = create_labeled_entry(frame, "End Date (YYYY-MM-DD):", 4, "2026-04-02")
    entry_fees = create_labeled_entry(frame, "Registration Fees ($):", 5, "0.00")
    entry_venue = create_labeled_entry(frame, "Venue ID:", 6, "1")

    def submit_event():
        try:
            db.add_event(
                entry_name.get(),
                entry_type.get(),
                entry_start.get(),
                entry_end.get(),
                entry_fees.get(),
                entry_venue.get()
            )
            Messagebox.show_info("Event Added Successfully!", "Success", parent=event_win)
            event_win.destroy()
        except Exception as e:
            Messagebox.show_error(str(e), "Error", parent=event_win)

    btn_frame = tb.Frame(frame)
    btn_frame.grid(row=7, column=0, columnspan=2, pady=30)
    
    tb.Button(btn_frame, text="Cancel", command=event_win.destroy, bootstyle="secondary-link", width=15).pack(side=LEFT, padx=10)
    tb.Button(btn_frame, text="Submit Event", command=submit_event, bootstyle="info", width=15).pack(side=LEFT, padx=10)


def open_resource_window(root):
    res_win = tb.Toplevel(root)
    res_win.title("Resource Manager")
    res_win.geometry("550x450")
    res_win.grab_set()

    frame = tb.Frame(res_win, padding=35)
    frame.pack(fill=BOTH, expand=True)

    tb.Label(frame, text="Allocate Resources", font=('Helvetica', 18, 'bold'), bootstyle="warning").grid(row=0, column=0, columnspan=2, pady=(0, 25))

    entry_session = create_labeled_entry(frame, "Session ID:", 1)
    entry_resource = create_labeled_entry(frame, "Resource ID:", 2)
    entry_qty = create_labeled_entry(frame, "Quantity Required:", 3)

    result_var = tb.StringVar()
    result_var.set("Ready for allocation. System trigger is active.")
    
    def allocate():
        try:
            session_id = entry_session.get()
            resource_id = entry_resource.get()
            quantity = int(entry_qty.get())
            
            before, after = db.allocate_resource(session_id, resource_id, quantity)
            
            report = (f"🔥 DB TRIGGER EXECUTED SUCCESSFULLY!\n\n"
                      f"• Initial Stock: {before}\n"
                      f"• Quantity Deducted: {quantity}\n"
                      f"• Remaining Available: {after}")
            result_var.set(report)

        except Exception as e:
            Messagebox.show_error(f"Could not complete allocation request.\nReason: {str(e)}", "Allocation Failed", parent=res_win)

    tb.Button(frame, text="Confirm Allocation", command=allocate, bootstyle="warning", width=20).grid(row=4, column=0, columnspan=2, pady=25)

    result_label = tb.Label(frame, textvariable=result_var, justify="left", bootstyle="inverse-dark", padding=20)
    result_label.grid(row=5, column=0, columnspan=2, fill="x", pady=10)


def open_view_window(root):
    view_win = tb.Toplevel(root)
    view_win.title("Analytics Dashboard")
    view_win.geometry("800x500")

    frame = tb.Frame(view_win, padding=20)
    frame.pack(fill=BOTH, expand=True)

    notebook = tb.Notebook(frame, bootstyle="info")
    notebook.pack(fill=BOTH, expand=True, pady=(0, 20))

    # Event Tab
    tab_events = tb.Frame(notebook)
    notebook.add(tab_events, text="📅 Event Registry")
    
    tree_events = tb.Treeview(tab_events, bootstyle="info", columns=("Event ID", "Event Name", "Start Date", "End Date"), show="headings", height=15)
    tree_events.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    for col in ("Event ID", "Event Name", "Start Date", "End Date"):
        tree_events.heading(col, text=col)
        tree_events.column(col, anchor=CENTER)

    try:
        event_rows = db.get_events()
        for row in event_rows:
            tree_events.insert("", "end", values=row)
    except Exception as e:
        tb.Label(tab_events, text=f"Error loading events: {str(e)}", bootstyle="danger").pack(pady=20)

    # Resource Tab
    tab_resources = tb.Frame(notebook)
    notebook.add(tab_resources, text="📦 Inventory Audit")
    
    tree_resources = tb.Treeview(tab_resources, bootstyle="warning", columns=("Resource ID", "Resource Name", "Available Qty"), show="headings", height=15)
    tree_resources.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    for col in ("Resource ID", "Resource Name", "Available Qty"):
        tree_resources.heading(col, text=col)
        tree_resources.column(col, anchor=CENTER)

    try:
        resource_rows = db.get_resources()
        for row in resource_rows:
            tree_resources.insert("", "end", values=row)
    except Exception as e:
        tb.Label(tab_resources, text=f"Error loading resources: {str(e)}", bootstyle="danger").pack(pady=20)

    tb.Button(frame, text="Close Dashboard", command=view_win.destroy, bootstyle="secondary").pack(side=RIGHT)
