import csv
import re
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

    def _validate_and_format_phone(self, phone):
        """Validate and format the phone number to xxx-xxx-xxxx format."""
        phone = re.sub(r'\D', '', phone)  # Remove non-digit characters
        if len(phone) != 10:
            raise ValueError("Phone number must be 10 digits long.")
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

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
        # Validate and format the phone number
        phone = self._validate_and_format_phone(phone)

        # Check if the phone number already exists
        existing_contact = self.contacts.find_by_phone(phone)
        if existing_contact:
            # Display the existing contact information in a formatted way
            print("\nDuplicate phone number found. Existing contact details:")
            self._display_contact(existing_contact)

            # Ask the user whether to update the contact or re-enter phone number
            user_choice = self._prompt_user_choice()

            if user_choice == '1':
                # Re-enter a new phone number
                new_phone = input("Enter a new phone number: ").strip()
                try:
                    new_phone = self._validate_and_format_phone(new_phone)
                    # Ensure the new phone number is also not a duplicate
                    if self.contacts.find_by_phone(new_phone):
                        raise ValueError("This new phone number already exists.")
                    phone = new_phone
                except ValueError as e:
                    print(e)
                    return

            elif user_choice == '2':
                # Update the existing contact's information
                update_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "address": address
                }
                self.update_contact_by_phone(phone, **update_data)
                app_logger.info(f"Updated existing contact: {first_name} {last_name}, Phone: {phone}")
                print(f"Updated existing contact: {first_name} {last_name}, Phone: {phone}")
                return

        # If phone is not a duplicate, proceed with adding the contact
        new_data = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "address": address
        }
        self.contacts.add(**new_data)

        # Log the action in the application log
        app_logger.info(f"Added new contact: {first_name} {last_name}, Phone: {phone}")

        # Audit log for sensitive information
        audit_logger.info(f"Contact added: {first_name} {last_name} (Sensitive info logged).")

        # Display the newly added contact
        print("\nNew contact added successfully:")
        self._display_contact(new_data)

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
    def search_contact(self, search_term):
        """Search contacts by name or phone number."""
        results = self.contacts.search_contact(search_term)
        if results:
            print("\nSearch Results:")
            for contact in results:
                self._display_contact(contact)
            app_logger.info(f"Search results for: {search_term}, Found {len(results)} contacts.")
        else:
            print(f"No contacts found for search term: {search_term}")
            app_logger.info(f"No search results found for: {search_term}")
        return results

    @error_reporter
    def get_all_contacts(self, limit=10, offset=0):
        """Get all contacts with pagination support and display them."""
        contacts = self.contacts.get_all_contacts(limit=limit, offset=offset)
        if contacts:
            print("\nAll contacts:")
            for contact in contacts:
                self._display_contact(contact)
            app_logger.info(f"Displayed {len(contacts)} contacts (limit={limit}, offset={offset}).")
        else:
            print("No contacts found.")
            app_logger.info("No contacts found.")
        return contacts

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

            # Validate CSV headers
            if not required_fields.issubset(reader.fieldnames):
                raise ValueError(f"CSV file is missing required headers: {required_fields - set(reader.fieldnames)}")

            for row in reader:
                # Ensure required fields are present in each row
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

    def _display_contact(self, contact):
        """Helper to format and display a single contact."""
        print(f"Name: {contact['first_name']} {contact['last_name']}")
        print(f"Phone: {contact['phone']}")
        if contact['email']:
            print(f"Email: {contact['email']}")
        if contact['address']:
            print(f"Address: {contact['address']}")
        print("-" * 40)  # Separator for visual clarity

