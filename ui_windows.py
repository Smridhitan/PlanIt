import tkinter as tk
from tkinter import X, Y, BOTH, LEFT, RIGHT, W, E, EW, END, CENTER
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database import Database
from styles import PAD_SM, PAD_MD, PAD_LG

db = Database()

def format_error(e):
    msg = str(e).lower()
    if "1045" in msg or "access denied" in msg: return "Access denied. Please check credentials."
    elif "1049" in msg or "unknown database" in msg: return "Database not found."
    elif "2003" in msg or "can't connect" in msg: return "Could not connect to server."
    elif "1062" in msg or "duplicate entry" in msg: return "Duplicate entry. Record exists."
    elif "1452" in msg or "foreign key constraint" in msg: return "Invalid reference ID."
    elif "invalid" in msg: return "Invalid input format."
    elif "45000" in msg:
        parts = str(e).split(":")
        return parts[-1].strip() if len(parts) > 1 else str(e)
    return f"Error: {e}"

def _entry(parent, placeholder=""):
    e = tb.Entry(parent, width=30)
    if placeholder: e.insert(0, placeholder)
    return e

def _section_header(parent, title, subtitle=None):
    tb.Label(parent, text=title, style="Heading.TLabel").pack(anchor=W, pady=(0, 4))
    if subtitle: tb.Label(parent, text=subtitle, style="Muted.TLabel").pack(anchor=W, pady=(0, PAD_LG))
    else: tb.Frame(parent, height=PAD_MD).pack()

def build_form(parent, fields, submit_callback, btn_text="Submit", btn_style="primary"):
    form = tb.Frame(parent)
    form.pack(fill=X, pady=PAD_MD)
    form.columnconfigure(1, weight=1)
    entries = {}
    
    for i, (key, label, widget_type) in enumerate(fields):
        tb.Label(form, text=label, style="Form.TLabel").grid(row=i, column=0, sticky=W, pady=PAD_SM, padx=(0, PAD_MD))
        if widget_type == 'entry':
            e = tb.Entry(form, width=35)
            e.grid(row=i, column=1, sticky=EW, pady=PAD_SM)
            entries[key] = e
        elif isinstance(widget_type, list):
            e = tb.Combobox(form, width=33, values=widget_type, state="readonly")
            if widget_type: e.current(0)
            e.grid(row=i, column=1, sticky=EW, pady=PAD_SM)
            entries[key] = e
            
    status_var = tk.StringVar()
    status_lbl = tb.Label(parent, textvariable=status_var, font=("Helvetica", 10))
    status_lbl.pack(anchor=W, pady=(5,0))
    
    def on_submit():
        try:
            kwargs = {k: v.get() for k,v in entries.items()}
            res = submit_callback(**kwargs)
            if res:
                status_var.set(f"✓ {res}")
            else:
                status_var.set("✓ Operation successful.")
            status_lbl.configure(bootstyle="success")
        except Exception as e:
            status_var.set(f"✕ {format_error(e)}")
            status_lbl.configure(bootstyle="danger")
            
    tb.Button(parent, text=btn_text, command=on_submit, bootstyle=btn_style).pack(anchor=W, pady=PAD_MD)
    return entries

def build_treeview(parent, columns, fetch_callback):
    frame = tb.Frame(parent)
    frame.pack(fill=BOTH, expand=True, pady=PAD_MD)
    tree = tb.Treeview(frame, columns=columns, show="headings", height=8)
    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, anchor=CENTER, width=120)
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    scroll = tb.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    scroll.pack(side=RIGHT, fill=Y)
    
    status = tb.Label(parent, text="", bootstyle="danger")
    status.pack(anchor=W)

    def refresh():
        tree.delete(*tree.get_children())
        try:
            data = fetch_callback()
            if data:
                for row in data: tree.insert("", END, values=row)
            status.configure(text="")
        except Exception as e:
            status.configure(text=f"Fail to load: {format_error(e)}")

    refresh()
    tb.Button(parent, text="Refresh Data", command=refresh, bootstyle="outline-secondary").pack(anchor=E, pady=PAD_SM)
    return tree

# ==========================================
# PANELS
# ==========================================

def build_users_panel(parent):
    notebook = tb.Notebook(parent)
    
    tab_add = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_add, text=" Add User ")
    _section_header(tab_add, "Register New User", "Add a new user to the platform.")
    build_form(tab_add, [
        ('first_name', 'First Name', 'entry'), ('last_name', 'Last Name', 'entry'),
        ('dob', 'DOB (YYYY-MM-DD)', 'entry'), ('email_id', 'Email', 'entry'), ('phone_no', 'Phone No', 'entry')
    ], lambda **k: db.add_user(k['first_name'], k['last_name'], k['dob'], k['email_id'], k['phone_no']))
    
    tab_view = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_view, text=" View / Delete ")
    _section_header(tab_view, "All Users", "Browse all registered users.")
    build_treeview(tab_view, ("ID", "First Name", "Last Name", "DOB", "Email", "Phone"), db.view_users)
    _section_header(tab_view, "Delete User")
    build_form(tab_view, [('user_id', 'User ID', 'entry')], lambda **k: db.delete_user(k['user_id']), "Delete", "danger")
    
    return notebook

def build_event_panel(parent):
    notebook = tb.Notebook(parent)
    
    tab_add = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_add, text=" Add Event ")
    _section_header(tab_add, "Create Event", "Register a new event.")
    build_form(tab_add, [
        ('event_name', 'Event Name', 'entry'), 
        ('event_type', 'Event Type', ['Workshop', 'Performance', 'Panel Discussion', 'Keynote Talk']),
        ('start_date', 'Start Date (YYYY-MM-DD)', 'entry'), ('end_date', 'End Date (YYYY-MM-DD)', 'entry'),
        ('fees', 'Fees', 'entry'), ('deadline', 'Reg. Deadline (YYYY-MM-DD)', 'entry'),
        ('status', 'Status', ['Draft', 'Upcoming', 'Ongoing', 'Completed', 'Cancelled']),
        ('desc', 'Description', 'entry'), ('slots', 'Available Slots', 'entry'), ('venue_id', 'Venue ID', 'entry')
    ], lambda **k: db.add_event(k['event_name'], k['event_type'], k['start_date'], k['end_date'], k['fees'], k['deadline'], k['status'], k['desc'], k['slots'], k['venue_id']))
    
    tab_view = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_view, text=" View / Delete ")
    _section_header(tab_view, "All Events", "Browse all events.")
    build_treeview(tab_view, ("Event Name", "Start Date", "End Date", "Venue Name"), db.view_events)
    _section_header(tab_view, "Delete Event")
    build_form(tab_view, [('event_id', 'Event ID', 'entry')], lambda **k: db.delete_event(k['event_id']), "Delete", "danger")
    
    return notebook

def build_sessions_panel(parent):
    notebook = tb.Notebook(parent)
    
    tab_add = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_add, text=" Add Session ")
    _section_header(tab_add, "Create Session", "Add a session to an event.")
    build_form(tab_add, [
        ('event_id', 'Event ID', 'entry'), ('speaker_id', 'Speaker ID', 'entry'),
        ('title', 'Session Title', 'entry'), ('date', 'Date (YYYY-MM-DD)', 'entry'),
        ('start_time', 'Start Time (HH:MM:SS)', 'entry'), ('end_time', 'End Time (HH:MM:SS)', 'entry'),
        ('total_slots', 'Total Slots', 'entry')
    ], lambda **k: db.add_session(k['event_id'], k['speaker_id'], k['title'], k['date'], k['start_time'], k['end_time'], k['total_slots']))
    
    tab_del = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_del, text=" Delete Session ")
    _section_header(tab_del, "Delete Session")
    build_form(tab_del, [('session_id', 'Session ID', 'entry')], lambda **k: db.delete_session(k['session_id']), "Delete", "danger")
    
    return notebook

def build_registrations_panel(parent):
    notebook = tb.Notebook(parent)
    
    tab_event = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_event, text=" Event Registration ")
    _section_header(tab_event, "Register for Event")
    build_form(tab_event, [
        ('user_id', 'User ID', 'entry'), ('event_id', 'Event ID', 'entry'),
        ('date', 'Date (YYYY-MM-DD)', 'entry'), ('status', 'Status', ['Confirmed', 'Pending']),
        ('id_type', 'Govt ID Type', ['Aadhar', 'Passport', 'Driving License', 'PAN']),
        ('id_number', 'Govt ID Number', 'entry')
    ], lambda **k: db.register_for_event(k['user_id'], k['event_id'], k['date'], k['status'], k['id_type'], k['id_number']))
    
    tab_session = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_session, text=" Session Registration ")
    _section_header(tab_session, "Register for Session")
    build_form(tab_session, [
        ('user_id', 'User ID', 'entry'), ('session_id', 'Session ID', 'entry'),
        ('date', 'Date (YYYY-MM-DD)', 'entry'), ('status', 'Status', ['Registered', 'Cancelled']),
        ('id_type', 'Govt ID Type', ['Aadhar', 'Passport', 'Driving License', 'PAN']),
        ('id_number', 'Govt ID Number', 'entry')
    ], lambda **k: db.register_for_session(k['user_id'], k['session_id'], k['date'], k['status'], k['id_type'], k['id_number']))
    
    return notebook

def build_resources_panel(parent):
    notebook = tb.Notebook(parent)
    
    tab_add = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_add, text=" Add / Delete Resource ")
    _section_header(tab_add, "Add Resource")
    build_form(tab_add, [
        ('name', 'Resource Name', 'entry'), ('type', 'Type', ['Furniture', 'Merchandise', 'Refreshments', 'Session_Requirement']),
        ('total', 'Total Qty', 'entry'), ('available', 'Available Qty', 'entry'),
        ('status', 'Status', ['Available', 'Allocated', 'Unavailable']), ('location', 'Location', 'entry')
    ], lambda **k: db.add_resource(k['name'], k['type'], k['total'], k['available'], k['status'], k['location']))
    
    _section_header(tab_add, "Delete Resource")
    build_form(tab_add, [('resource_id', 'Resource ID', 'entry')], lambda **k: db.delete_resource(k['resource_id']), "Delete", "danger")

    tab_alloc = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_alloc, text=" Allocate ")
    _section_header(tab_alloc, "Allocate Resource to Session")
    
    alloc_status = tk.StringVar(value="")
    status_lbl = tb.Label(tab_alloc, textvariable=alloc_status, style="Muted.TLabel")
    
    def on_alloc(session_id, resource_id, qty):
        # We wrapped `allocate_resource` in database.py to yield before and after
        before, after = db.allocate_resource(session_id, resource_id, qty)
        alloc_status.set(f"Previous Stock: {before} | Stock Remaining: {after}")
        status_lbl.configure(bootstyle="success")

    build_form(tab_alloc, [
        ('session_id', 'Session ID', 'entry'), ('resource_id', 'Resource ID', 'entry'), ('qty', 'Quantity', 'entry')
    ], on_alloc)
    status_lbl.pack(anchor=W, pady=PAD_MD)
    
    return notebook

def build_venues_panel(parent):
    notebook = tb.Notebook(parent)
    tab = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab, text=" Venues ")
    _section_header(tab, "Find Available Venues")
    
    form_frame = tb.Frame(tab)
    form_frame.pack(fill=X)
    e_start = _entry(form_frame)
    e_start.insert(0, "YYYY-MM-DD")
    e_end = _entry(form_frame)
    e_end.insert(0, "YYYY-MM-DD")
    e_city = _entry(form_frame)
    
    tb.Label(form_frame, text="Start Date:").grid(row=0, column=0, pady=5)
    e_start.grid(row=0, column=1, pady=5, padx=5)
    tb.Label(form_frame, text="End Date:").grid(row=0, column=2, pady=5)
    e_end.grid(row=0, column=3, pady=5, padx=5)
    tb.Label(form_frame, text="City:").grid(row=1, column=0, pady=5)
    e_city.grid(row=1, column=1, pady=5, padx=5)

    res_frame = tb.Frame(tab)
    res_frame.pack(fill=BOTH, expand=True, pady=PAD_MD)
    
    def on_search():
        for widget in res_frame.winfo_children(): widget.destroy()
        try:
            data = db.view_available_venues(e_start.get(), e_end.get(), e_city.get())
            build_treeview(res_frame, ("Venue ID", "Name", "Room", "Capacity", "Status", "Street", "City", "State", "Pincode"), lambda: data)
        except Exception as e:
            tb.Label(res_frame, text=f"Error: {format_error(e)}", bootstyle="danger").pack(anchor=W)

    tb.Button(form_frame, text="Search", command=on_search).grid(row=1, column=3, sticky=W, padx=5)
    return notebook

def build_vendors_panel(parent):
    notebook = tb.Notebook(parent)
    
    tab_add = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_add, text=" Add Vendor ")
    _section_header(tab_add, "Register Vendor")
    build_form(tab_add, [
        ('name', 'Name', 'entry'), ('type', 'Type', ['Stationery', 'Music', 'Food', 'Decoration', 'Technical', 'Other']),
        ('contact', 'Contact Person', 'entry'), ('phone', 'Phone', 'entry'), ('email', 'Email', 'entry'),
        ('street', 'Street', 'entry'), ('city', 'City', ['Delhi', 'Bangalore', 'Mumbai', 'Pune', 'Chennai']),
        ('state', 'State', 'entry'), ('pincode', 'Pincode', 'entry'), ('courier', 'Courier Facility (1/0)', 'entry')
    ], lambda **k: db.add_vendor(k['name'], k['type'], k['contact'], k['phone'], k['email'], k['street'], k['city'], k['state'], k['pincode'], int(k['courier'])))
    
    tab_view = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab_view, text=" View Vendors ")
    _section_header(tab_view, "Search Vendors")
    form_frame = tb.Frame(tab_view)
    form_frame.pack(fill=X)
    e_type = tb.Combobox(form_frame, values=['Stationery', 'Music', 'Food', 'Decoration', 'Technical', 'Other'])
    e_type.current(0)
    e_city = _entry(form_frame)
    tb.Label(form_frame, text="Type:").grid(row=0, column=0, pady=5)
    e_type.grid(row=0, column=1, pady=5, padx=5)
    tb.Label(form_frame, text="City:").grid(row=0, column=2, pady=5)
    e_city.grid(row=0, column=3, pady=5, padx=5)

    res_frame = tb.Frame(tab_view)
    res_frame.pack(fill=BOTH, expand=True, pady=PAD_MD)
    
    def on_search():
        for widget in res_frame.winfo_children(): widget.destroy()
        try:
            data = db.view_vendors(e_type.get(), e_city.get())
            build_treeview(res_frame, ("Vendor Name", "Vendor Type"), lambda: data)
        except Exception as e:
            tb.Label(res_frame, text=f"Error: {format_error(e)}", bootstyle="danger").pack(anchor=W)

    tb.Button(form_frame, text="Search", command=on_search).grid(row=0, column=4, sticky=W, padx=5)
    
    return notebook

def build_analytics_panel(parent):
    notebook = tb.Notebook(parent)
    tab = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab, text=" Dashboard ")
    _section_header(tab, "Analytics Dashboard", "Key metrics and popular events.")
    
    res_var = tk.StringVar(value="Click a button below to fetch metrics.")
    res_lbl = tb.Label(tab, textvariable=res_var, font=("Helvetica", 14), justify=LEFT)
    res_lbl.pack(pady=PAD_LG, anchor=W)
    
    btn_frame = tb.Frame(tab)
    btn_frame.pack(anchor=W)
    
    def get_pop():
        try:
            r = db.get_most_popular_event()
            res_var.set(f"Most Popular Event:\n{r[0]} ({r[1]} registrations)")
        except Exception as e: res_var.set(format_error(e))
        
    def get_rev():
        try:
            r = db.get_event_revenue()
            txt = "Event Revenue:\n" + "\n".join([f"{x[0]}: ₹{x[1]}" for x in r])
            res_var.set(txt)
        except Exception as e: res_var.set(format_error(e))

    tb.Button(btn_frame, text="Most Popular Event", bootstyle="info", command=get_pop).pack(side=LEFT, padx=5)
    tb.Button(btn_frame, text="Event Revenue", bootstyle="info", command=get_rev).pack(side=LEFT, padx=5)
    return notebook

def build_payments_panel(parent):
    notebook = tb.Notebook(parent)
    tab = tb.Frame(notebook, padding=PAD_MD)
    notebook.add(tab, text=" Add Payment ")
    _section_header(tab, "Process Payment")
    build_form(tab, [
        ('reg_id', 'Registration ID', 'entry'), ('amount', 'Amount', 'entry'),
        ('mode', 'Mode', ['UPI', 'Card', 'NetBanking', 'Cash']),
        ('status', 'Status', ['Success', 'Failed', 'Pending'])
    ], lambda **k: db.add_payment(k['reg_id'], k['amount'], k['mode'], k['status']))
    return notebook
