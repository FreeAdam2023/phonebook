import csv
import re

from tabulate import tabulate

from app.models.contact import Contacts
from utils.utils import error_reporter
from utils.logger import setup_logger  # Import the logger setup

# Application log
app_logger = setup_logger('app_logger', 'logs/app.log')

# Audit log
audit_logger = setup_logger('audit_logger', 'logs/audit.log')


class PhoneBookService:

    def __init__(self):
        self.contacts = Contacts()

    def _prompt_user_choice(self):
        """Prompt the user for their choice on how to handle duplicate phone number."""
        print("The phone number already exists. What would you like to do?")
        print("1. Re-enter a new phone number")
        print("2. Update the existing contact information")
        choice = input("Enter 1 or 2: ").strip()

        while choice not in ['1', '2']:
            print("Invalid choice. Please enter 1 to re-enter or 2 to update.")
            choice = input("Enter 1 or 2: ").strip()

        return choice

    @error_reporter
    def add_contact(self, first_name, last_name, phone, email=None, address=None):
        """Add a new contact and display the result."""
        # Construct new contact data
        new_data = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "address": address
        }

        # Add the contact
        self.contacts.add(**new_data)

        # Log the action
        app_logger.info(f"Added new contact: {first_name} {last_name}, Phone: {phone}")
        audit_logger.info(f"Contact added: {first_name} {last_name} (Sensitive info logged).")

        # Display the newly added contact
        print("\nNew contact added successfully:")
        self._display_contact(new_data)

    def _display_contact(self, contact):
        """Helper to format and display a single contact."""
        print(f"Name: {contact['first_name']} {contact['last_name']}")
        print(f"Phone: {contact['phone']}")
        if 'email' in contact and contact['email']:
            print(f"Email: {contact['email']}")
        if 'address' in contact and contact['address']:
            print(f"Address: {contact['address']}")
        print("-" * 40)  # Separator for visual clarity

    @error_reporter
    def update_contact_by_phone(self, phone, **fields):
        """Update contact information."""
        # Validate and format the phone number if it's in the fields to be updated
        if 'phone' in fields:
            fields['phone'] = self._validate_and_format_phone(fields['phone'])

        # Pass the phone as a dictionary for the WHERE clause
        self.contacts.update({'phone': phone}, **fields)

        # Log the update action
        app_logger.info(f"Updated contact with phone: {phone}, Fields: {fields}")

        # Audit log for changes to sensitive data
        audit_logger.info(f"Updated contact with phone: {phone}, Changes: {fields}")

    @error_reporter
    def delete_contact(self, phone):
        """Delete a contact."""
        self.contacts.delete(**{"phone": phone})

        # Log the deletion in both app and audit logs
        app_logger.info(f"Deleted contact with phone: {phone}")
        audit_logger.info(f"Deleted contact with phone: {phone} (Sensitive data removed).")

    @error_reporter
    def _fetch_and_display_contacts(self, search_term=None, limit=10, offset=0):
        """General method to fetch and display contacts, with optional search."""
        if search_term:
            search_term = self._format_search_term(search_term)
            contacts = self.contacts.search_contact(search_term, limit=limit, offset=offset)
            total_contacts = self.contacts.count_contacts(search_term)  # Assuming a method to count search results
        else:
            contacts = self.contacts.get_all_contacts(limit=limit, offset=offset)
            total_contacts = self.contacts.count_contacts()

        if not contacts:
            print(f"No contacts found{' for search term: ' + search_term if search_term else '.'}")
            return

        self._display_contacts_as_table(contacts, total_contacts, limit)

    @error_reporter
    def handle_view_contacts(self):
        """Handle viewing all contacts with pagination."""
        self._fetch_and_display_contacts()

    @error_reporter
    def handle_search_contact(self):
        """Handle searching for a contact by name or phone number with pagination."""
        search_term = input("Enter search term (name or phone): ").strip()
        self._fetch_and_display_contacts(search_term)

    @error_reporter
    def _format_search_term(self, search_term):
        """Format a phone number prefix to (xxx)xxx-xxxx format for partial searches."""
        if search_term.isdigit() or re.match(r'^\(\d{3}\)\d{3}-\d{4}$', search_term):
            search_term = re.sub(r'\D', '', search_term)
            if len(search_term) <= 3:
                return f"({search_term})"
            elif len(search_term) <= 6:
                return f"({search_term[:3]}){search_term[3:]}"
            else:
                return f"({search_term[:3]}){search_term[3:6]}-{search_term[6:]}"
        return search_term

    @error_reporter
    def _display_contacts_as_table(self, contacts, total_contacts, limit=10):
        """Helper method to display contacts in a table format using tabulate, with optional pagination."""
        total_pages = (total_contacts + limit - 1) // limit
        offset = 0
        current_page = 1

        while True:
            table_data = []
            headers = ["#", "First Name", "Last Name", "Phone", "Email", "Address"]

            for contact in contacts[offset:offset + limit]:
                table_data.append([
                    contact['id'] if 'id' in contact else 'N/A',
                    contact['first_name'] if 'first_name' in contact else 'N/A',
                    contact['last_name'] if 'last_name' in contact else 'N/A',
                    contact['phone'] if 'phone' in contact else 'N/A',
                    contact['email'] if 'email' in contact else 'N/A',
                    contact['address'] if 'address' in contact else 'N/A'
                ])

            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print(f"\nShowing page {current_page} of {total_pages}")

            next_action = input("Press 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()

            if next_action == 'n' and current_page < total_pages:
                offset += limit
                current_page += 1
            elif next_action == 'p' and current_page > 1:
                offset -= limit
                current_page -= 1
            elif next_action == 'q':
                break
            else:
                print("Invalid input, please try again.")

    @error_reporter
    def bulk_add_contacts(self, records):
        """Bulk add contacts."""
        for record in records:
            record['phone'] = self._validate_and_format_phone(record['phone'])
        self.contacts.bulk_add(records)
        app_logger.info(f"Bulk added {len(records)} contacts.")

    @error_reporter
    def bulk_add_contacts_from_csv(self, csv_file_path):
        """Bulk add contacts from a CSV file with detailed error reporting."""
        records = self._parse_csv(csv_file_path)
        if records:
            self.bulk_add_contacts(records)
            app_logger.info(f"Bulk added contacts from CSV file: {csv_file_path}, Total records: {len(records)}")
        else:
            print("No valid records found to add.")
            app_logger.warning(f"No valid records found in CSV file: {csv_file_path}")

    @error_reporter
    def _parse_csv(self, csv_file_path):
        """Helper method to parse CSV and validate records."""
        records = []
        required_fields = {'first_name', 'last_name', 'phone'}

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            if not required_fields.issubset(reader.fieldnames):
                raise ValueError(f"CSV file is missing required headers: {required_fields - set(reader.fieldnames)}")

            for row in reader:
                if not all(row[field] for field in required_fields):
                    print(f"Skipping row with missing required data: {row}")
                    app_logger.warning(f"Skipping invalid row in CSV: {row}")
                    continue

                records.append({
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row['phone'],
                    'email': row.get('email'),
                    'address': row.get('address')
                })

        return records

    def _validate_and_format_phone(self, phone, check_duplicata=True):
        """Validate, format and check for duplicate phone number."""
        while True:
            if re.match(r'^\(\d{3}\)\d{3}-\d{4}$', phone):
                phone = re.sub(r'[^\d]', '', phone)
            elif re.match(r'^\d{10}$', phone):
                pass
            else:
                print("Invalid phone number format. Please enter in (xxx)xxx-xxxx or xxxxxxxxxx format.")
                phone = input("Re-enter phone number: ").strip()
                continue

            formatted_phone = f"({phone[:3]}){phone[3:6]}-{phone[6:]}"

            if check_duplicata:
                existing_contact = self.contacts.find_by_phone(formatted_phone)
                if existing_contact:
                    print(f"Phone number {formatted_phone} already exists for the following contact:")
                    self._display_contact(existing_contact)
                    user_choice = input(
                        "Would you like to (1) re-enter a new phone number or (2) cancel the operation? Enter 1 or 2: ").strip()
                    if user_choice == '1':
                        phone = input("Re-enter phone number: ").strip()
                        continue
                    elif user_choice == '2':
                        print("Operation cancelled.")
                        return None
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                        continue
                else:
                    return formatted_phone
            else:
                return formatted_phone

    def _validate_email(self, email):
        """Validate email format."""
        while email:
            if re.match(r'^\S+@\S+\.\S+$', email):
                return email
            else:
                print("Invalid email format. Please enter a valid email.")
                email = input("Re-enter email (optional, press enter to skip): ").strip()
        return None

    def _validate_name(self, name, field_name):
        """Validate that the name is not empty and contains only letters."""
        while True:
            if name and name.isalpha():
                return name
            else:
                print(f"Invalid {field_name}. It must only contain letters and cannot be empty.")
                name = input(f"Re-enter {field_name}: ").strip()

    @error_reporter
    def handle_add_contact(self):
        """Handle adding a new contact with field validation at input time."""
        # Validate first name
        first_name = self._validate_name(input("First name: ").strip(), "first name")

        # Validate last name
        last_name = self._validate_name(input("Last name: ").strip(), "last name")

        # Validate phone number and check for duplicates
        phone = self._validate_and_format_phone(input("Phone number: ").strip())
        if phone is None:
            print("Contact addition cancelled.")
            return  # If the user cancels, stop the process

        # Validate email (optional)
        email = self._validate_email(input("Email (optional, press enter to skip): ").strip())

        # Validate address (optional, no format needed, can be empty)
        address = input("Address (optional): ").strip() or None

        # Add contact
        self.add_contact(first_name, last_name, phone, email, address)
        print("Contact added successfully.")

    @error_reporter
    def handle_delete_contact(self):
        """Handle deleting a contact by phone number or contact ID."""
        print("Delete Contact: You can delete by phone number or contact ID (number).")
        delete_choice = input("Would you like to delete by (1) Phone number or (2) Contact ID? Enter 1 or 2: ").strip()

        if delete_choice == '1':
            # Delete by phone number
            phone = input("Enter phone number of the contact to delete: ").strip()
            if not phone:
                print("Phone number is required to delete contact.")
                return
            delete_info = self.contacts.find_by_phone(phone)
            self.delete_contact(phone=phone)
            print(f"Contact with info {delete_info['id']}. {delete_info['first_name']} {delete_info['last_name']}, "
                  f"Phone: {delete_info['phone']} deleted successfully.")
            app_logger.info(f"Deleted contact with phone: {phone}, info: {delete_info}")

        elif delete_choice == '2':
            # Delete by contact ID
            try:
                contact_id = int(input("Enter the contact ID to delete: ").strip())
            except ValueError:
                print("Invalid contact ID. Please enter a valid number.")
                return
            delete_info = self.contacts.fetch_one(**{'id': contact_id})
            self.contacts.delete(**{'id': contact_id})
            print(f"Contact with info {delete_info['id']}. {delete_info['first_name']} {delete_info['last_name']}, "
                  f"Phone: {delete_info['phone']} deleted successfully.")
            app_logger.info(f"Deleted contact with ID: {contact_id}, info: {delete_info}")
        else:
            print("Invalid option. Please enter 1 or 2.")
            return

    @error_reporter
    def handle_update_contact(self):
        """Handle updating a contact's information."""
        print("Update Contact: You can update by phone number or contact ID (number).")
        update_choice = input("Would you like to update by (1) Phone number or (2) Contact ID? Enter 1 or 2: ").strip()

        existing_contact = None

        if update_choice == '1':
            # Update by phone number
            phone = input("Enter phone number of the contact to update: ").strip()
            phone = self._validate_and_format_phone(phone, check_duplicata=False)
            if not phone:
                print("Phone number is required to update contact.")
                return

            # Fetch existing contact by phone before updating
            existing_contact = self.contacts.find_by_phone(phone)
            if not existing_contact:
                print(f"No contact found with phone: {phone}")
                return
        elif update_choice == '2':
            # Update by contact ID
            try:
                contact_id = int(input("Enter the contact ID to update: ").strip())
            except ValueError:
                print("Invalid contact ID. Please enter a valid number.")
                return

            # Fetch existing contact by ID before updating
            existing_contact = self.contacts.fetch_one(id=contact_id)
            if not existing_contact:
                print(f"No contact found with ID: {contact_id}")
                return
        else:
            print("Invalid option. Please enter 1 or 2.")
            return

        # Display current contact information before update
        print("\n--- Current Contact Information ---")
        self._display_contact(existing_contact)

        # Collect new details from the user with validation
        first_name = self._validate_name(input("New first name (leave empty to skip): ").strip(), "first name") or None
        last_name = self._validate_name(input("New last name (leave empty to skip): ").strip(), "last name") or None
        email = self._validate_email(input("New email (leave empty to skip): ").strip()) or None
        address = input("New address (leave empty to skip): ").strip() or None

        # Collect all updated fields
        updated_fields = {k: v for k, v in
                          {'first_name': first_name, 'last_name': last_name, 'email': email, 'address': address}.items()
                          if v}

        if not updated_fields:
            print("No valid fields to update.")
            return

        # Perform the update
        if update_choice == '1':
            # Update by phone number
            self.contacts.update_contact_by_phone(phone, **updated_fields)
            print(f"Contact with phone {phone} updated successfully.")
            app_logger.info(f"Updated contact with phone: {phone}, Changes: {updated_fields}")
        elif update_choice == '2':
            # Update by contact ID
            self.contacts.update_contact_by_id(contact_id, **updated_fields)
            print(f"Contact with ID {contact_id} updated successfully.")
            app_logger.info(f"Updated contact with ID: {contact_id}, Changes: {updated_fields}")

        # Fetch updated contact information
        updated_contact = self.contacts.find_by_phone(phone) if update_choice == '1' else self.contacts.fetch_one(
            id=contact_id)

        # Display updated contact information after update
        print("\n--- Updated Contact Information ---")
        self._display_contact(updated_contact)

        # Compare and display the differences between old and new contact information
        print("\n--- Changes ---")
        self._display_changes(existing_contact, updated_contact)

    def _display_changes(self, old_contact, new_contact):
        """Helper to display the differences between old and new contact."""
        fields = ['first_name', 'last_name', 'email', 'address']
        for field in fields:
            old_value = old_contact[field]
            new_value = new_contact[field]
            if old_value != new_value:
                print(f"{field.capitalize()}: '{old_value}' -> '{new_value}'")

    @error_reporter
    def display_summary(self):
        """Display a summary of the contacts in the phone book."""
        total_contacts = self.contacts.count_contacts()
        print("\n--- Phone Book Summary ---")
        print(f"Total Contacts: {total_contacts}")

        if total_contacts > 0:
            print("Here are a few of your contacts:")
            # Display the first 3 contacts as a summary
            contacts = self.contacts.get_all_contacts(limit=3)
            for contact in contacts:
                print(f"{contact['id']}. {contact['first_name']} {contact['last_name']}, Phone: {contact['phone']}")
        else:
            print("No contacts found in the phone book.")
        print("---------------------------")
