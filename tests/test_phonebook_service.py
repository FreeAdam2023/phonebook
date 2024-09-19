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
        # Simulate the bulk add method
        self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Verifying that bulk_add was called correctly
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '1234567890', 'email': 'john@example.com',
             'address': '123 Maple St'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '9876543210', 'email': 'jane@example.com',
             'address': '456 Oak St'}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

    @patch('builtins.open', new_callable=mock_open,
           read_data='first_name,last_name,phone\nJohn,Doe,2234567890\nJane,Smith,9876543220')
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv_missing_fields(self, mock_logger, mock_file):
        # Test CSV file with missing fields (no email, no address)
        self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Verifying that bulk_add was called with records missing optional fields
        expected_records = [
            {'first_name': 'John', 'last_name': 'Doe', 'phone': '2234567890', 'email': None, 'address': None},
            {'first_name': 'Jane', 'last_name': 'Smith', 'phone': '9876543220', 'email': None, 'address': None}
        ]
        self.contacts.bulk_add.assert_called_once_with(expected_records)

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    def test_bulk_add_contacts_from_csv_file_not_found(self, mock_logger, mock_file):
        # Test for file not found
        with self.assertRaises(FileNotFoundError):
            self.service.bulk_add_contacts_from_csv('tests/test_data/contacts.csv')

        # Ensuring bulk_add was never called
        self.contacts.bulk_add.assert_not_called()

    # @patch('app.services.phonebook_service.app_logger')  # Mocking logger
    # def test_handle_batch_delete_contacts(self, mock_logger):
    #     # Mock the fetched contacts to be deleted
    #     self.contacts.fetch_one.side_effect = [
    #         {'id': '1', 'first_name': 'John', 'last_name': 'Doe', 'phone': '1234567890'},
    #         {'id': '2', 'first_name': 'Jane', 'last_name': 'Smith', 'phone': '9876543210'}
    #     ]
    #
    #     # Simulating user input for IDs to delete
    #     with patch('builtins.input', return_value='1,2'):
    #         self.service.handle_batch_delete_contacts()
    #
    #     # Ensuring delete was called with the correct IDs
    #     self.contacts.delete.assert_any_call(id='1')
    #     self.contacts.delete.assert_any_call(id='2')
    #
    #     # Ensuring logger called with correct info
    #     mock_logger.info.assert_called_with(
    #         "Deleted contacts: [{'id': '1', 'first_name': 'John', 'last_name': 'Doe', 'phone': '1234567890'}, "
    #         "{'id': '2', 'first_name': 'Jane', 'last_name': 'Smith', 'phone': '9876543210'}]")
    #
    #     # Verifying the output
    #     expected_output = "Deleted contacts:\nID: 1, Name: John Doe, Phone: 1234567890\nID: 2, Name: Jane Smith, Phone: 9876543210\nBatch delete completed successfully."
    #     with patch('builtins.print') as mock_print:
    #         self.service.handle_batch_delete_contacts()
    #         mock_print.assert_called_with(expected_output)


if __name__ == '__main__':
    unittest.main()
