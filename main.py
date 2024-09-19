from app.services.phonebook_service import PhoneBookService
from tabulate import tabulate  # Import the tabulate library for table formatting
from utils.utils import error_reporter
from utils.logger import setup_logger

# Setup loggers
app_logger = setup_logger('app_logger', 'logs/app.log')
audit_logger = setup_logger('audit_logger', 'logs/audit.log')


@error_reporter
def main_menu():
    """Display the main menu and prompt user for an option."""
    print("\nPhone Book Manager")
    print("1. Add a contact")
    print("2. View all contacts")
    print("3. Search contact")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Exit")
    return input("Choose an option: ")

@error_reporter
def main():
    """Main program loop to handle user input and perform actions."""
    service = PhoneBookService()

    # Display contact summary before showing the menu
    service.display_summary()

    while True:
        option = main_menu()
        if option == "1":
            service.handle_add_contact()
        elif option == "2":
            service.handle_view_contacts()
        elif option == "3":
            service.handle_search_contact()
        elif option == "4":
            service.handle_update_contact()
        elif option == "5":
            service.handle_delete_contact()
        elif option == "6":
            print("Exiting Phone Book Manager.")
            app_logger.info("Exited the Phone Book Manager.")
            break
        else:
            print("Invalid option, please choose a valid menu item.")
            app_logger.warning(f"Invalid option selected: {option}")


if __name__ == "__main__":
    main()
