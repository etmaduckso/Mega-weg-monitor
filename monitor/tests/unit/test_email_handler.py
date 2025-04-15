import unittest
from unittest.mock import Mock, patch, MagicMock
from app.core.email_handler import EmailHandler
from app.core.notification_client import NotificationClient

class TestEmailHandler(unittest.TestCase):
    @patch('imaplib.IMAP4_SSL')
    def test_connection(self, mock_imap):
        mock_notification_client = MagicMock(spec=NotificationClient)
        handler = EmailHandler(notification_clients=[mock_notification_client])
        handler.mail = mock_imap.return_value

        # Simulate IMAP server responses
        call_tracker = {'count': 0}

        def mock_login(*args, **kwargs):
            call_tracker['count'] += 1
            if call_tracker['count'] == 1:
                return ('OK', [b'Logged in'])
            else:
                return ('NO', [b'Auth failed'])

        handler.mail.login.side_effect = mock_login

        # Add debug logging to trace the mocked responses
        print(f"Mocked login responses: {handler.mail.login.side_effect}")

        # Test successful login
        self.assertTrue(handler.connect())
        print("First connection attempt passed.")

        # Test failed login
        self.assertFalse(handler.connect())
        print("Second connection attempt failed as expected.")

        # Verify the mock was called with correct arguments
        handler.mail.login.assert_called_with(handler.username, handler.password)

if __name__ == '__main__':
    unittest.main()
