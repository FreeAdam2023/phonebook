import unittest
from unittest.mock import MagicMock, mock_open, patch
from phonebook.app.services.phonebook_service import PhoneBookService


class TestPhoneBookService(unittest.TestCase):

    def setUp(self):
        # Mocking the Contacts model
        self.contacts = MagicMock()
        self.service = PhoneBookService()
        self.service.contacts = self.contacts  # Injecting the mocked Contacts into the service

    @patch('builtins.open', new_callable=mock_open,
           read_data='first_name,last_name,phone,email,address\nJohn,Doe,123456789,john@example.com,123 Elm St\nJane,Smith,987654321,jane@example.com,456 Oak St')
    @patch('phonebook.app.services.phonebook_service.app_logger')
    def test_bulk_add_contacts_from_csv(self, mock_logger, mock_file):
        # Simulate the bulk add method
        self.service.bulk_add_contacts_from_csv('phonebook/tests/test_data/contacts.csv')

        # Verifying that bulk_add was called correctly
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '123456789', 'email': 'john@example.com',
             'address': '123 Elm St'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '987654321', 'email': 'jane@example.com',
             'address': '456 Oak St'}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

        # Verifying that logger info was called
        mock_logger.info.assert_called_once_with('Bulk added contacts from CSV file: phonebook/tests/test_data/contacts.csv, Total records: 2')

    @patch('builtins.open', new_callable=mock_open,
           read_data='first_name,last_name,phone\nJohn,Doe,123456789\nJane,Smith,987654321')
    @patch('phonebook.app.services.phonebook_service.app_logger')
    def test_bulk_add_contacts_from_csv_missing_fields(self, mock_logger, mock_file):
        # Test CSV file with missing fields (no email, no address)
        self.service.bulk_add_contacts_from_csv('phonebook/tests/test_data/contacts.csv')

        # Verifying that bulk_add was called with records missing optional fields
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '123456789', 'email': None, 'address': None},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '987654321', 'email': None, 'address': None}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

        # Verifying logger output for missing fields
        mock_logger.info.assert_called_once_with('Bulk added contacts from CSV file: phonebook/tests/test_data/contacts.csv, Total records: 2')

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('phonebook.app.services.phonebook_service.app_logger')
    def test_bulk_add_contacts_from_csv_file_not_found(self, mock_logger, mock_file):
        # Test for file not found
        with self.assertRaises(FileNotFoundError):
            self.service.bulk_add_contacts_from_csv('invalid/path/contacts.csv')

        # Ensuring bulk_add was never called
        self.contacts.bulk_add.assert_not_called()

        # Verifying that an error was logged
        mock_logger.error.assert_called_once_with('An error occurred while processing invalid/path/contacts.csv: [Errno 2] No such file or directory: \'invalid/path/contacts.csv\'\nTraceback (most recent call last):\n...')

    @patch('builtins.open', new_callable=mock_open, read_data='invalid,csv,data\nnot,valid,structure')
    @patch('phonebook.app.services.phonebook_service.app_logger')
    def test_bulk_add_contacts_from_csv_invalid_structure(self, mock_logger, mock_file):
        # Test for invalid CSV structure
        with patch('builtins.print') as mock_print:
            self.service.bulk_add_contacts_from_csv('phonebook/tests/test_data/invalid.csv')
            mock_print.assert_called_once_with('No valid records found to add.')

        # Ensuring bulk_add was never called due to the error
        self.contacts.bulk_add.assert_not_called()

        # Verify logging of invalid structure
        mock_logger.warning.assert_called_once_with('No valid records found in CSV file: phonebook/tests/test_data/invalid.csv')


if __name__ == '__main__':
    unittest.main()
