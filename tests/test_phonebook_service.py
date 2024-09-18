import unittest
from unittest.mock import MagicMock, mock_open, patch
from app.services.phonebook_service import PhoneBookService


class TestPhoneBookService(unittest.TestCase):

    def setUp(self):
        # Mocking the Contacts model
        self.contacts = MagicMock()
        self.service = PhoneBookService()
        self.service.contacts = self.contacts  # Injecting the mocked Contacts into the service

    @patch('builtins.open', new_callable=mock_open,
           read_data='first_name,last_name,phone,email,address\nJohn,Doe,123456789,john@example.com,123 Maple St\nJane,Smith,987654321,jane@example.com,456 Oak St')
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv(self, mock_logger, mock_file):
        # Simulate the bulk add method
        self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Verifying that bulk_add was called correctly
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '123456789', 'email': 'john@example.com',
             'address': '123 Maple St'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '987654321', 'email': 'jane@example.com',
             'address': '456 Oak St'}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

    @patch('builtins.open', new_callable=mock_open,
           read_data='first_name,last_name,phone\nJohn,Doe,123456789\nJane,Smith,987654321')
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv_missing_fields(self, mock_logger, mock_file):
        # Test CSV file with missing fields (no email, no address)
        self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Verifying that bulk_add was called with records missing optional fields
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '123456789', 'email': None, 'address': None},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '987654321', 'email': None, 'address': None}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv_file_not_found(self, mock_logger, mock_file):
        # Test for file not found
        with self.assertRaises(FileNotFoundError):
            self.service.bulk_add_contacts_from_csv('invalid/path/contacts.csv')

        # Ensuring bulk_add was never called
        self.contacts.bulk_add.assert_not_called()


if __name__ == '__main__':
    unittest.main()
