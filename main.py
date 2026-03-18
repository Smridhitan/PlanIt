import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ui_windows import open_event_window, open_resource_window, open_view_window

def main():
    # 'darkly' is a beautiful, modern flat dark theme inspired by Bootstrap
    root = tb.Window(themename="darkly", title="DBMS System Control Panel", size=(450, 420))
    
    main_frame = tb.Frame(root, padding=40)
    main_frame.pack(fill=BOTH, expand=True)

    tb.Label(main_frame, text="Organizer Interface", font=('Helvetica', 22, 'bold'), bootstyle="primary").pack(fill=X, pady=(0, 5))
    tb.Label(main_frame, text="Select an operation from the menu below", font=('Helvetica', 12), bootstyle="secondary").pack(fill=X, pady=(0, 30))

    buttons_frame = tb.Frame(main_frame)
    buttons_frame.pack(fill=BOTH, expand=True)

    tb.Button(buttons_frame, text="📅 Quick Add Event", command=lambda: open_event_window(root), bootstyle="info-outline", width=30).pack(pady=10, ipady=6)
    tb.Button(buttons_frame, text="📦 Manage Resources \n(Trigger Demo)", command=lambda: open_resource_window(root), bootstyle="warning-outline", width=30).pack(pady=10, ipady=8)
    tb.Button(buttons_frame, text="📊 Open Analytics Dashboard", command=lambda: open_view_window(root), bootstyle="success", width=30).pack(pady=10, ipady=6)

    footer = tb.Label(root, text="Connected to MySQL (Locally) • Secure Connection", bootstyle="secondary", font=("Helvetica", 9))
    footer.pack(side=BOTTOM, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
