from data.crud import CrudOperations
from utils.utils import error_reporter  # Import the error reporter decorator

class Contacts(CrudOperations):
    def __init__(self):
        super().__init__('contacts')  # Initialize the CrudOperations with the 'contacts' table
        self.create_contacts_table()

    @error_reporter
    def create_contacts_table(self):
        """
        Create the contacts table if it does not exist.
        """
        query = '''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self.execute(query)  # Use `execute` directly since `Contacts` inherits from `CrudOperations`

    @error_reporter
    def search_contact(self, search_term, limit=10, offset=0):
        """
        Search contacts by first name, last name, or phone number with pagination.
        """
        where_clause = "first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?"
        search_value = f"%{search_term}%"
        query = f"SELECT * FROM {self.table} WHERE {where_clause} LIMIT ? OFFSET ?"

        # Add pagination parameters (limit, offset) to the query
        return self.fetchall(query, (
        search_value, search_value, search_value, limit, offset))  # Use `fetchall` from `CrudOperations`

    @error_reporter
    def get_all_contacts(self, limit=10, offset=0):
        """
        Retrieve paginated contacts from the table.
        """
        return self.fetch_all(limit=limit, offset=offset)  # Use `fetch_all` method from `CrudOperations`

    @error_reporter
    def count_contacts(self, search_term=None):
        """
        Count the total number of contacts in the table, optionally filtered by a search term.
        If a search term is provided, it counts the number of contacts matching the term by first name, last name, or phone.
        """
        if search_term:
            where_clause = "first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?"
            search_value = f"%{search_term}%"
            query = f"SELECT COUNT(*) as count FROM {self.table} WHERE {where_clause}"
            rsp = self.fetchone(query, (search_value, search_value, search_value))
            return rsp['count'] if rsp else 0
        else:
            query = f"SELECT COUNT(*) as count FROM {self.table}"
            rsp = self.fetchone(query)
            return rsp['count'] if rsp else 0


    @error_reporter
    def find_by_phone(self, phone):
        """
        Find a contact by phone number.
        """
        query = f"SELECT * FROM {self.table} WHERE phone = ?"
        return self.fetchone(query, (phone,))  # Use `fetchone` to return a single record if found

    @error_reporter
    def update_contact_by_phone(self, phone, **fields):
        """Update contact by phone number."""
        self.update({'phone': phone}, **fields)

    @error_reporter
    def update_contact_by_id(self, contact_id, **fields):
        """Update contact by contact ID."""
        self.update({'id': contact_id}, **fields)