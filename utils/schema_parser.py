"""
@Time ： 2024-09-16
@Auth ： Adam Lyu
"""


def get_table_schema(db, table_name):
    query = f"PRAGMA table_info({table_name})"
    columns = db.fetchall(query)
    schema = {col['name']: col['type'] for col in columns}
    return schema
