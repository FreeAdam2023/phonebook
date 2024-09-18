from phonebook.data.crud import CrudOperations
from phonebook.utils.utils import error_reporter  # Import the error reporter decorator

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
    def search_contact(self, search_term):
        """
        Search contacts by first name, last name, or phone number.
        """
        where_clause = "first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?"
        search_value = f"%{search_term}%"
        query = f"SELECT * FROM {self.table} WHERE {where_clause}"
        return self.fetchall(query, (search_value, search_value, search_value))  # Use `fetchall` from `CrudOperations`

    @error_reporter
    def get_all_contacts(self, limit=10, offset=0):
        """
        Retrieve paginated contacts from the table.
        """
        return self.fetch_all(limit=limit, offset=offset)  # Use `fetch_all` method from `CrudOperations`

    @error_reporter
    def count_contacts(self):
        """
        Count the total number of contacts in the table.
        """
        query = f"SELECT COUNT(*) FROM {self.table}"
        return self.fetchone(query)[0]  # Use `fetchone` from `CrudOperations`
