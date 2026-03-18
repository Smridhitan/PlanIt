import tkinter as tk
from tkinter import ttk
from ui_windows import open_event_window, open_resource_window, open_view_window

def setup_styles():
    style = ttk.Style()
    # Try using clam theme across OS for a cleaner modern look 
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    style.configure('TFrame', background='#fafafa')
    style.configure('TLabel', background='#fafafa', font=('Helvetica', 11))
    
    style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), anchor='center', foreground='#2c3e50')
    style.configure('Subtitle.TLabel', font=('Helvetica', 10, 'italic'), foreground='#7f8c8d')
    
    # Modern rounded/boxed button styling
    style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=12)
    
    # Specific accent button style if needed later
    style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'), foreground='white', background='#2980b9')
    style.map('Accent.TButton', background=[('active', '#3498db')])

def main():
    root = tk.Tk()
    root.title("DBMS System Control Panel")
    root.geometry("450x400")
    root.configure(bg="#fafafa")
    
    setup_styles()

    main_frame = ttk.Frame(root, padding="30 40 30 40")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Organizer Interface", style='Title.TLabel').pack(fill=tk.X, pady=(0, 5))
    ttk.Label(main_frame, text="Select an operation from the menu below", style='Subtitle.TLabel', anchor='center').pack(fill=tk.X, pady=(0, 30))

    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Button(buttons_frame, text="📅 Quick Add Event", command=lambda: open_event_window(root)).pack(fill=tk.X, pady=10)
    ttk.Button(buttons_frame, text="📦 Manage Resources (Trigger Demo)", command=lambda: open_resource_window(root)).pack(fill=tk.X, pady=10)
    ttk.Button(buttons_frame, text="📊 Open Analytics Dashboard", command=lambda: open_view_window(root)).pack(fill=tk.X, pady=10)

    # Footer note
    footer = tk.Label(root, text="Connected to MySQL (Locally)", bg="#fafafa", fg="#95a5a6", font=("Helvetica", 9))
    footer.pack(side=tk.BOTTOM, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
