import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

db = Database()

def create_labeled_entry(parent, label_text, row, placeholder=""):
    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
    entry = ttk.Entry(parent, width=32)
    entry.grid(row=row, column=1, sticky=tk.E, pady=8, padx=5)
    if placeholder:
        entry.insert(0, placeholder)
    return entry

def open_event_window(root):
    event_win = tk.Toplevel(root)
    event_win.title("Event Management")
    event_win.geometry("450x420")
    
    # Force focus
    event_win.grab_set()

    frame = ttk.Frame(event_win, padding="20 20 20 20")
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Create New Event", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    entry_name = create_labeled_entry(frame, "Event Name:", 1)
    
    ttk.Label(frame, text="Event Type:").grid(row=2, column=0, sticky=tk.W, pady=8, padx=5)
    type_var = tk.StringVar()
    entry_type = ttk.Combobox(frame, textvariable=type_var, width=30, state="readonly")
    entry_type['values'] = ("Workshop", "Performance", "Panel Discussion", "Keynote Talk", "Seminar", "Other")
    entry_type.current(0)
    entry_type.grid(row=2, column=1, sticky=tk.E, pady=8, padx=5)

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
            messagebox.showinfo("Success", "Event Added Successfully!", parent=event_win)
            event_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=event_win)

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=7, column=0, columnspan=2, pady=25)
    
    ttk.Button(btn_frame, text="Cancel", command=event_win.destroy).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Submit Event", command=submit_event, style='Accent.TButton').pack(side=tk.LEFT, padx=10)

def open_resource_window(root):
    res_win = tk.Toplevel(root)
    res_win.title("Resource Manager")
    res_win.geometry("500x420")
    
    res_win.grab_set()

    frame = ttk.Frame(res_win, padding="30 30 30 30")
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Allocate Resources", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    entry_session = create_labeled_entry(frame, "Session ID:", 1)
    entry_resource = create_labeled_entry(frame, "Resource ID:", 2)
    entry_qty = create_labeled_entry(frame, "Quantity Required:", 3)

    result_var = tk.StringVar()
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
                      f"• Remaining Available: {after}\n")
            result_var.set(report)

        except Exception as e:
            messagebox.showerror("Allocation Failed", f"Could not complete allocation request.\nReason: {str(e)}", parent=res_win)

    ttk.Button(frame, text="Confirm Allocation", command=allocate, style='Accent.TButton').grid(row=4, column=0, columnspan=2, pady=20)

    # Result Box
    result_label = ttk.Label(frame, textvariable=result_var, justify="left", anchor="w", background="#2a2e33", foreground="#a6e3a1", relief="flat", padding=15)
    result_label.grid(row=5, column=0, columnspan=2, fill="x", pady=10)


def populate_treeview(tree, columns, rows):
    # Setup Treeview Columns
    tree["columns"] = columns
    tree["show"] = "headings"
    
    # Create Headings with styling and proportional widths
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor=tk.CENTER)
        
    # Adding scrollbar
    scrollbar = ttk.Scrollbar(tree, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Insert Data rows
    for count, row in enumerate(rows):
        tag = "even" if count % 2 == 0 else "odd"
        tree.insert("", "end", values=row, tags=(tag,))
        
    tree.tag_configure("even", background="#f5f5f5")
    tree.tag_configure("odd", background="#ffffff")

def open_view_window(root):
    view_win = tk.Toplevel(root)
    view_win.title("Analytics Dashboard")
    view_win.geometry("700x450")

    frame = ttk.Frame(view_win, padding="15 15 15 15")
    frame.pack(fill=tk.BOTH, expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    # Event Tab
    tab_events = ttk.Frame(notebook)
    notebook.add(tab_events, text="📅 Event Registry")
    
    tree_events = ttk.Treeview(tab_events, height=15)
    tree_events.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    try:
        event_rows = db.get_events()
        populate_treeview(tree_events, ("Event ID", "Event Name", "Start Date", "End Date"), event_rows)
    except Exception as e:
        ttk.Label(tab_events, text=f"Error loading events: {str(e)}", foreground="red").pack(pady=20)

    # Resource Tab
    tab_resources = ttk.Frame(notebook)
    notebook.add(tab_resources, text="📦 Inventory Audit")
    
    tree_resources = ttk.Treeview(tab_resources, height=15)
    tree_resources.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    try:
        resource_rows = db.get_resources()
        populate_treeview(tree_resources, ("Resource ID", "Resource Name", "Available Qty"), resource_rows)
    except Exception as e:
        ttk.Label(tab_resources, text=f"Error loading resources: {str(e)}", foreground="red").pack(pady=20)

    ttk.Button(frame, text="Close Dashboard", command=view_win.destroy).pack(side=tk.RIGHT)
