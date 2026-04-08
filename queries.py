import mysql.connector

class queries: 


    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "College@24"
        self.database = "Dbms_Project"

    def connect_to_dbms(self):
        """Establish and return a database connection."""
        return mysql.connector.connect(host = self.host, user = self.user, password=self.password, database=self.database)
    # USER FUNCTIONS

    def add_user(self, first_name, last_name, dob, email_id, phone_no): #To be called when there is a new sign up
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Users (first_name, last_name, DOB, email_id, phone_no)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, dob, email_id, phone_no))
        conn.commit()
        conn.close()


    def view_users(self): #To be used by the admin to check the details of all users
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("SELECT * FROM Users")
        data = curr.fetchall()
        conn.close()
        return data


    def delete_user(self, user_id): #To used by admin to delete a specific user
        if int(user_id) < 0:
            raise ValueError("User ID cannot be negative.")
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        if curr.rowcount == 0:
            conn.close()
            raise ValueError("User does not exist.")
        conn.commit()
        conn.close()



    # EVENT FUNCTIONS

    def add_event(self, event_name, event_type, start_date, end_date, fees, deadline, status, description, slots, venue_id): #To be used by an organizer to create a new event
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Event (event_name, event_type, start_date, end_date, registration_fees, registration_deadline, event_status, description, total_registrations, available_slots, venue_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (event_name, event_type, start_date, end_date, fees, deadline, status, description, 0, slots, venue_id))
        conn.commit()
        conn.close()


    def view_events(self): #this function would be used to display the details of the event to the users on the dashboard
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT e.event_id, e.event_name, e.event_type, e.start_date, e.end_date, v.venue_name
            FROM Event e
            JOIN Venue v ON e.venue_id = v.venue_id
        """)
        data = curr.fetchall()
        conn.close()
        return data


    def view_event_details(self, event_id): #To give users details of an event when they click on a specific event from the dashboard
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT e.event_name, e.start_date, e.end_date, e.registration_deadline,
                v.venue_name, e.description, e.registration_fees
            FROM Event e
            JOIN Venue v ON e.venue_id = v.venue_id
            WHERE e.event_id = %s
        """, (event_id,))
        data = curr.fetchone()
        conn.close()
        return data


    def delete_event(self, event_id): #Organizer can delete event
        if int(event_id) < 0:
            raise ValueError("Event ID cannot be negative.")
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("DELETE FROM Event WHERE event_id = %s", (event_id,))
        if curr.rowcount == 0:
            conn.close()
            raise ValueError("Event does not exist.")
        conn.commit()
        conn.close()



    # SESSION FUNCTIONS

    def add_session(self, event_id, speaker_id, title, date, start_time, end_time, total_slots):
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Session (event_id, speaker_user_id, title, session_date, start_time, end_time, total_slots, slots_filled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
        """, (event_id, speaker_id, title, date, start_time, end_time, total_slots))
        conn.commit()
        conn.close()
        
    def delete_session(self, session_id):
        if int(session_id) < 0:
            raise ValueError("Session ID cannot be negative.")
        conn = self.connect_to_dbms()
        curr = conn.cursor()

        curr.execute("""
            DELETE FROM Session
            WHERE session_id = %s
        """, (session_id,))
        
        if curr.rowcount == 0:
            conn.close()
            raise ValueError("Session does not exist.")

        conn.commit()
        conn.close()

    def view_sessions(self, event_id):
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("SELECT * FROM Session WHERE event_id = %s", (event_id,))
        data = curr.fetchall()
        conn.close()
        return data


    def view_session_details(self, session_id):
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT s.title, s.session_date, s.start_time, s.end_time,
                s.total_slots, s.slots_filled
            FROM Session s
            WHERE s.session_id = %s
        """, (session_id,))
        data = curr.fetchone()
        conn.close()
        return data



    # REGISTRATION FUNCTIONS

    def register_for_event(self, user_id, event_id, date, id_type, id_number): #Users can register for an event
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Event_Registration
            (user_id, event_id, registration_date, registration_status, govt_id_type, govt_id_number)
            VALUES (%s, %s, %s, 'Pending', %s, %s)
        """, (user_id, event_id, date, id_type, id_number))
        conn.commit()
        conn.close()


    def register_for_session(self, user_id, session_id, date, status, id_type, id_number): 
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Session_Registration
            (user_id, session_id, session_registration_date, session_registration_status, govt_id_type, govt_id_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, session_id, date, status, id_type, id_number))
        conn.commit()
        conn.close()



    # RESOURCE FUNCTIONS

    def add_resource(self, name, type, total, available, status, location): #Admin can add a resource to the inventory 
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Resource (resource_name, resource_type, total_quantity, available_quantity, status, storage_location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, type, total, available, status, location))
        conn.commit()
        conn.close()


    def view_resources(self): #Organisers can see resources
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("SELECT * FROM Resource")
        data = curr.fetchall()
        conn.close()
        return data


    def delete_resource(self, resource_id): #Admin can delete resources 
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("DELETE FROM Resource WHERE resource_id = %s", (resource_id,))
        conn.commit()
        conn.close()


    def allocate_resource_to_session(self, session_id, resource_id, quantity, start_time, end_time): #Organiser can take resources from the inventory
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Resource_Allocation
            (session_id, resource_id, quantity_allocated, allocation_status, start_time, end_time)
            VALUES (%s, %s, %s, 'Allocated', %s, %s)
        """, (session_id, resource_id, quantity, start_time, end_time))

        conn.commit()
        conn.close()



    # VENUE FUNCTIONS

    def view_available_venues(self, start_date, end_date, city): #Organizer can select a venue from the list of available venues
        conn = self.connect_to_dbms()
        curr = conn.cursor()

        curr.execute("""
            SELECT v.*
            FROM Venue v
            WHERE v.city = %s
            AND v.venue_status = 'Available'
            AND v.venue_id NOT IN (
                SELECT e.venue_id
                FROM Event e
                WHERE NOT (
                    e.end_date < %s
                    OR e.start_date > %s
                )
            )
        """, (city, start_date, end_date))

        data = curr.fetchall()
        conn.close()
        return data


    # VENDOR FUNCTIONS

    def add_vendor(self, name, type, contact, phone, email, street, city, state, pincode, courier): #Users can sell materials 
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO Vendor
            (vendor_name, vendor_type, contact_person, phone_no, email, street, city, state, pincode, courier_facility)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, type, contact, phone, email, street, city, state, pincode, courier))
        conn.commit()
        conn.close()


    def view_vendors(self, type, city): #Organisers can choose from a list of vendors to get materials 
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT vendor_name, vendor_type
            FROM Vendor
            WHERE vendor_type = %s AND city = %s
        """, (type, city))
        data = curr.fetchall()
        conn.close()
        return data



    # ANALYTICS FUNCTIONS

    def get_most_popular_event(self): #to get the most popular event 
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT event_name, total_registrations
            FROM Event
            ORDER BY total_registrations DESC
            LIMIT 1
        """)
        data = curr.fetchone()
        conn.close()
        return data


    def get_event_revenue(self): #to get the the revenue generated from the event
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT e.event_name, SUM(p.amount)
            FROM Event e
            JOIN Event_Registration er ON e.event_id = er.event_id
            JOIN Payment p ON er.registration_id = p.registration_id
            WHERE p.payment_status = 'Success'
            GROUP BY e.event_name
        """)
        data = curr.fetchall()
        conn.close()
        return data


    def get_resources_used(self, session_id):
        conn = self.connect_to_dbms()
        curr = conn.cursor()
        curr.execute("""
            SELECT r.resource_name, ra.quantity_allocated
            FROM Resource_Allocation ra
            JOIN Resource r ON ra.resource_id = r.resource_id
            WHERE ra.session_id = %s
        """, (session_id,))
        data = curr.fetchall()
        conn.close()
        return data



    #PAYMENT FUNCTIONS

    def add_payment(self, registration_id, amount, payment_mode, payment_status):
        conn = self.connect_to_dbms()
        curr = conn.cursor()

        curr.execute(""""
            INSERT INTO Payment
            (registration_id, amount, payment_mode, payment_status)
            VALUES (%s, %s, %s, %s)
        """, (registration_id, amount, payment_mode, payment_status))

        conn.commit()
        conn.close()
