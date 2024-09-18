import traceback
from phonebook.utils.schema_parser import get_table_schema
from phonebook.utils.validators import validate_fields
from phonebook.data.database import Database  # Now inheriting from this class
import sqlite3  # Assuming you're using sqlite3

class CrudOperations(Database):
    def __init__(self, table: str):
        super().__init__()  # Initialize the Database class
        self.table = table
        self.schema = get_table_schema(self, table)  # Use inherited Database methods
        self.conn.row_factory = sqlite3.Row  # Set the row factory to return dictionaries

    def transactional(func):
        """
        Transaction decorator to manage transaction lifecycle with enhanced error reporting.
        """
        def wrapper(self, *args, **kwargs):
            try:
                self.connect()  # Use inherited Database connect method
                self.conn.execute('BEGIN TRANSACTION')
                result = func(self, *args, **kwargs)
                self.conn.commit()
                return result
            except Exception as e:
                self.conn.rollback()
                error_details = traceback.format_exc()  # Get full stack trace
                raise Exception(f"Error in {func.__name__} with args {args}, kwargs {kwargs}. "
                                f"Original error: {e}\nTraceback: {error_details}")
            finally:
                self.close()
        return wrapper

    @transactional
    def add(self, **fields):
        validate_fields(fields, self.schema)
        columns = ', '.join(fields.keys())
        placeholders = ', '.join('?' for _ in fields)
        query = f"INSERT INTO {self.table} ({columns}, created_at) VALUES ({placeholders}, CURRENT_TIMESTAMP)"
        self.execute(query, tuple(fields.values()))  # Use inherited execute method

    @transactional
    def update(self, where, **fields):
        validate_fields(fields, self.schema)
        set_clause = ', '.join(f"{k} = ?" for k in fields)
        where_clause = ' AND '.join(f"{k} = ?" for k in where)
        query = f"UPDATE {self.table} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE {where_clause}"
        self.execute(query, tuple(fields.values()) + tuple(where.values()))

    @transactional
    def delete(self, **where):
        where_clause = ' AND '.join(f"{k} = ?" for k in where)
        query = f"DELETE FROM {self.table} WHERE {where_clause}"
        self.execute(query, tuple(where.values()))

    @transactional
    def bulk_add(self, records):
        if not records:
            return
        first_record = records[0]
        validate_fields(first_record, self.schema)
        columns = ', '.join(first_record.keys())
        placeholders = ', '.join('?' for _ in first_record)
        query = f"INSERT INTO {self.table} ({columns}, created_at) VALUES ({placeholders}, CURRENT_TIMESTAMP)"
        self.conn.executemany(query, [tuple(record.values()) for record in records])

    def fetch_one(self, **where):
        """
        Fetch a single record based on the given condition(s).
        Returns a dictionary.
        """
        where_clause = ' AND '.join(f"{k} = ?" for k in where)
        query = f"SELECT * FROM {self.table} WHERE {where_clause} LIMIT 1"
        row = self.fetchone(query, tuple(where.values()))
        return dict(row) if row else None  # Return the row as a dictionary

    def fetch_all(self, limit=10, offset=0, **where):
        """
        Fetch all records that match the given condition(s) with pagination support.
        Args:
            limit: Number of records to return per page.
            offset: The starting point in the records for the current page.
            where: Optional filtering conditions.

        Returns:
            List of dictionaries with pagination.
        """
        if where:
            where_clause = ' AND '.join(f"{k} = ?" for k in where)
            query = f"SELECT * FROM {self.table} WHERE {where_clause} LIMIT ? OFFSET ?"
            params = tuple(where.values()) + (limit, offset)
        else:
            query = f"SELECT * FROM {self.table} LIMIT ? OFFSET ?"
            params = (limit, offset)

        rows = self.fetchall(query, params)
        return [dict(row) for row in rows] if rows else []  # Return list of dictionaries
