"""
@Time ： 2024-09-16
@Auth ： Adam Lyu
"""
def validate_fields(fields, schema):
    for field, value in fields.items():
        if field not in schema:
            raise ValueError(f"Field {field} is not in schema")
        # Example: You can add more specific validation based on the schema type if needed
