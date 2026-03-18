import tkinter as tk
from tkinter import messagebox
from database import Database

db = Database()

def open_event_window(root):
    event_win = tk.Toplevel(root)
    event_win.title("Add Event")

    tk.Label(event_win, text="Add Event", font=("Arial", 14)).pack(pady=10)

    entry_name = tk.Entry(event_win, width=30)
    entry_name.insert(0, "Event Name")
    entry_name.pack(pady=2)

    entry_type = tk.Entry(event_win, width=30)
    entry_type.insert(0, "Workshop / Performance / Panel Discussion / Keynote Talk")
    entry_type.pack(pady=2)

    entry_start = tk.Entry(event_win, width=30)
    entry_start.insert(0, "YYYY-MM-DD")
    entry_start.pack(pady=2)

    entry_end = tk.Entry(event_win, width=30)
    entry_end.insert(0, "YYYY-MM-DD")
    entry_end.pack(pady=2)

    entry_fees = tk.Entry(event_win, width=30)
    entry_fees.insert(0, "Fees")
    entry_fees.pack(pady=2)

    entry_venue = tk.Entry(event_win, width=30)
    entry_venue.insert(0, "Venue ID")
    entry_venue.pack(pady=2)

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
            messagebox.showinfo("Success", "Event Added")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(event_win, text="Add Event", command=submit_event).pack(pady=10)


def open_resource_window(root):
    res_win = tk.Toplevel(root)
    res_win.title("Allocate Resource")

    tk.Label(res_win, text="Allocate Resource", font=("Arial", 14)).pack(pady=10)

    entry_session = tk.Entry(res_win, width=30)
    entry_session.insert(0, "Session ID")
    entry_session.pack(pady=2)

    entry_resource = tk.Entry(res_win, width=30)
    entry_resource.insert(0, "Resource ID")
    entry_resource.pack(pady=2)

    entry_qty = tk.Entry(res_win, width=30)
    entry_qty.insert(0, "Quantity")
    entry_qty.pack(pady=2)

    result_box = tk.Text(res_win, height=10, width=50)
    result_box.pack(pady=10)

    def allocate():
        try:
            session_id = entry_session.get()
            resource_id = entry_resource.get()
            quantity = int(entry_qty.get())

            before, after = db.allocate_resource(session_id, resource_id, quantity)

            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, "RESOURCE TRIGGER DEMO\n\n")
            result_box.insert(tk.END, f"Before: {before}\n")
            result_box.insert(tk.END, f"After : {after}\n\n")
            result_box.insert(tk.END, f"Allocated: {quantity}\n")
            result_box.insert(tk.END, f"Change   : -{quantity}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(res_win, text="Allocate", command=allocate).pack(pady=5)


def open_view_window(root):
    view_win = tk.Toplevel(root)
    view_win.title("View Data")

    text_box = tk.Text(view_win, height=20, width=80)
    text_box.pack(pady=10)

    def show_events():
        try:
            rows = db.get_events()
            text_box.delete(1.0, tk.END)
            for row in rows:
                text_box.insert(tk.END, str(row) + "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_resources():
        try:
            rows = db.get_resources()
            text_box.delete(1.0, tk.END)
            for row in rows:
                text_box.insert(tk.END, str(row) + "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(view_win, text="View Events", command=show_events).pack(pady=5)
    tk.Button(view_win, text="View Resources", command=show_resources).pack(pady=5)
