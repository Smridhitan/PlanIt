import mysql.connector

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "College@24"
        self.database = "Dbms_Project"

    def get_connection(self):
        """Establish and return a database connection."""
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def add_event(self, name, event_type, start, end, fees, venue):
        """Insert a new event into the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO Event 
        (event_name, event_type, start_date, end_date, registration_fees, event_status, total_registrations, available_slots, venue_id)
        VALUES (%s, %s, %s, %s, %s, 'Upcoming', 0, 50, %s)
        """, (name, event_type, start, end, fees, venue))
        conn.commit()
        conn.close()

    def allocate_resource(self, session_id, resource_id, quantity):
        """Allocate a resource and observe the trigger."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check quantity before
        cursor.execute("SELECT available_quantity FROM Resource WHERE resource_id = %s", (resource_id,))
        before_row = cursor.fetchone()
        if not before_row:
            conn.close()
            raise ValueError("Resource not found.")
        before = before_row[0]

        # Allocate (Should trigger the DB to decrease available_quantity)
        cursor.execute("""
        INSERT INTO Resource_Allocation 
        (session_id, resource_id, quantity_allocated, allocation_status)
        VALUES (%s, %s, %s, 'Allocated')
        """, (session_id, resource_id, quantity))
        conn.commit()

        # Check quantity after
        cursor.execute("SELECT available_quantity FROM Resource WHERE resource_id = %s", (resource_id,))
        after = cursor.fetchone()[0]
        
        conn.close()
        return before, after

    def get_events(self):
        """Fetch all events."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, event_name, start_date, end_date FROM Event")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_resources(self):
        """Fetch all resources."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT resource_id, resource_name, available_quantity FROM Resource")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_sessions(self):
        """Fetch all sessions."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, event_id, title, session_date, start_time, end_time FROM Session")
        rows = cursor.fetchall()
        conn.close()
        return rows
