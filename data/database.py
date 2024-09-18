import sqlite3


class Database:
    def __init__(self, db_name='phonebook.db'):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row

    def execute(self, query, params=None):
        self.connect()
        if params is None:
            params = ()
        cursor = self.conn.execute(query, params)
        return cursor

    def fetchall(self, query, params=None):
        self.connect()
        if params is None:
            params = ()
        cursor = self.conn.execute(query, params)
        results = cursor.fetchall()
        return results

    def fetchone(self, query, params=None):
        self.connect()
        if params is None:
            params = ()
        cursor = self.conn.execute(query, params)
        result = cursor.fetchone()
        return result

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def begin_transaction(self):
        self.connect()
        self.conn.execute('BEGIN TRANSACTION')

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()
