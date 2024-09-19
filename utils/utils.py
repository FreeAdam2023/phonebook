"""
@Time ： 2024-09-17
@Auth ： Adam Lyu
"""

import traceback
import logging

def error_reporter(func):
    """
    Decorator for error reporting with logging.
    Logs the error and allows the program to continue running.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(f"Error in function {func.__name__}: {str(e)}\n{error_details}")
            print(f"An error occurred: {str(e)}. Continuing execution...")
            # Don't raise the error again, just log it and continue
    return wrapper


def input_with_exit(prompt):
    """Prompt user for input and support returning to the previous menu."""
    user_input = input(f"{prompt} (or 'b' to go back): ").strip()
    if user_input.lower() == 'b':
        return None  # Signal to go back
    return user_input

