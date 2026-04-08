from queries import queries

class Database(queries):
    def __init__(self):
        super().__init__()

    def allocate_resource(self, session_id, resource_id, quantity):
        """Allocate a resource and observe the trigger."""
        conn = self.connect_to_dbms()
        cursor = conn.cursor()
        
        # Check quantity before
        cursor.execute("SELECT available_quantity FROM Resource WHERE resource_id = %s", (resource_id,))
        before_row = cursor.fetchone()
        if not before_row:
            conn.close()
            raise ValueError("Resource not found.")
        before = before_row[0]

        # Allocate (Should trigger the DB to decrease available_quantity)
        super().allocate_resource_to_session(session_id, resource_id, quantity, '00:00', '23:59')

        # Check quantity after
        conn = self.connect_to_dbms() # Super method closes connection
        cursor = conn.cursor()
        cursor.execute("SELECT available_quantity FROM Resource WHERE resource_id = %s", (resource_id,))
        after = cursor.fetchone()[0]
        
        conn.close()
        return before, after

    # Aliasing methods that UI forms currently use
    def get_events(self):
        return self.view_events()

    def get_resources(self):
        conn = self.connect_to_dbms()
        cursor = conn.cursor()
        # The view_resources returns all columns. The previous get_resources returned specifically:
        # resource_id, resource_name, available_quantity
        cursor.execute("SELECT resource_id, resource_name, available_quantity FROM Resource")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_sessions(self):
        conn = self.connect_to_dbms()
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, event_id, title, session_date, start_time, end_time FROM Session")
        rows = cursor.fetchall()
        conn.close()
        return rows
