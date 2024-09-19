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
           read_data='first_name,last_name,phone,email,address\nJohn,Doe,1234567890,john@example.com,123 Maple St\nJane,Smith,9876543210,jane@example.com,456 Oak St')
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv(self, mock_logger, mock_file):
        # Mocking the find_by_phone to return None, so it doesn't detect duplicates
        self.contacts.find_by_phone.return_value = None

        # Simulate the bulk add method
        self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Verifying that bulk_add was called correctly
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '(123)456-7890', 'email': 'john@example.com',
             'address': '123 Maple St'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '(987)654-3210', 'email': 'jane@example.com',
             'address': '456 Oak St'}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

    @patch('builtins.open', new_callable=mock_open,
           read_data='first_name,last_name,phone\nJohn,Doe,2234567890\nJane,Smith,9876543220')
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv_missing_fields(self, mock_logger, mock_file):
        # Mocking the find_by_phone to return None, so it doesn't detect duplicates
        self.contacts.find_by_phone.return_value = None

        # Simulate the bulk add method
        self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Verifying that bulk_add was called with records missing optional fields
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '(223)456-7890',  'address': None, 'email': None},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '(987)654-3220',  'address': None, 'email': None}
        ]

        # Assert that the bulk_add method was called with the correctly formatted records
        self.contacts.bulk_add.assert_called_once_with(expected_records)



if __name__ == '__main__':
    unittest.main()
