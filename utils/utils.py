"""
@Time ： 2024-09-17
@Auth ： Adam Lyu
"""
import traceback


def error_reporter(func):
    """
    A decorator to provide detailed error reporting with function name and stack trace.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            function_name = func.__name__  # Get the name of the function
            error_details = traceback.format_exc()  # Capture the full stack trace
            print(f"Error in {function_name}: {e}\nDetails: {error_details}")
            raise e  # Re-raise the exception after logging the error

    return wrapper
