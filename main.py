import tkinter as tk
from ui_windows import open_event_window, open_resource_window, open_view_window

def main():
    root = tk.Tk()
    root.title("DBMS Trigger System Dashboard")
    root.geometry("400x300")

    tk.Label(root, text="Organizer Dashboard", font=("Arial", 16)).pack(pady=20)

    # Use lambda to pass 'root' as parent
    tk.Button(root, text="Add Event", width=25, command=lambda: open_event_window(root)).pack(pady=5)
    tk.Button(root, text="Allocate Resource", width=25, command=lambda: open_resource_window(root)).pack(pady=5)
    tk.Button(root, text="View Data", width=25, command=lambda: open_view_window(root)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
