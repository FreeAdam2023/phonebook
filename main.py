import logging
from phonebook.app.services.phonebook_service import PhoneBookService
from phonebook.utils.utils import error_reporter
from phonebook.utils.logger import setup_logger  # Import logger setup

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
def handle_add_contact(service):
    """Handle adding a new contact."""
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    phone = input("Phone number: ").strip()
    email = input("Email (optional): ").strip() or None
    address = input("Address (optional): ").strip() or None
    service.add_contact(first_name, last_name, phone, email, address)
    print("Contact added successfully.")

    # Log the addition of the contact
    app_logger.info(f"Added contact: {first_name} {last_name}, Phone: {phone}")


@error_reporter
def handle_view_contacts(service):
    """Handle viewing all contacts with pagination."""
    limit = 10  # Change this number if you want to see more contacts per page.
    offset = 0
    while True:
        service.get_all_contacts(limit=limit, offset=offset)
        next_page = input("Press 'n' for next page, or 'q' to quit: ").strip().lower()
        if next_page == 'n':
            offset += limit
        else:
            break


@error_reporter
def handle_search_contact(service):
    """Handle searching for a contact by name or phone number."""
    search_term = input("Enter search term (name or phone): ").strip()
    results = service.search_contact(search_term)
    if results:
        for contact in results:
            print(contact)
        app_logger.info(f"Search results for: {search_term}, Found {len(results)} contacts.")
    else:
        print("No matching contacts found.")
        app_logger.info(f"No contacts found for search term: {search_term}")


@error_reporter
def handle_update_contact(service):
    """Handle updating a contact's information."""
    phone = input("Enter phone number of the contact to update: ").strip()
    if not phone:
        print("Phone number is required to update contact.")
        return
    first_name = input("New first name (leave empty to skip): ").strip() or None
    last_name = input("New last name (leave empty to skip): ").strip() or None
    email = input("New email (leave empty to skip): ").strip() or None
    address = input("New address (leave empty to skip): ").strip() or None
    service.update_contact(phone, first_name=first_name, last_name=last_name, email=email, address=address)
    print("Contact updated successfully.")

    # Log the update
    app_logger.info(f"Updated contact: Phone: {phone}, Changes: {fields}")


@error_reporter
def handle_delete_contact(service):
    """Handle deleting a contact by phone number."""
    phone = input("Enter phone number of the contact to delete: ").strip()
    service.delete_contact(phone)
    print("Contact deleted successfully.")

    # Log the deletion
    app_logger.info(f"Deleted contact with phone: {phone}")


@error_reporter
def main():
    """Main program loop to handle user input and perform actions."""
    service = PhoneBookService()
    while True:
        option = main_menu()
        if option == "1":
            handle_add_contact(service)
        elif option == "2":
            handle_view_contacts(service)
        elif option == "3":
            handle_search_contact(service)
        elif option == "4":
            handle_update_contact(service)
        elif option == "5":
            handle_delete_contact(service)
        elif option == "6":
            print("Exiting Phone Book Manager.")
            app_logger.info("Exited the Phone Book Manager.")
            break
        else:
            print("Invalid option, please choose a valid menu item.")
            app_logger.warning(f"Invalid option selected: {option}")


if __name__ == "__main__":
    main()
