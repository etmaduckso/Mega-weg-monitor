import unittest
from unittest.mock import Mock, patch
from app.core.email_handler import EmailHandler  # Corrigido o caminho do import

class TestEmailHandler(unittest.TestCase):
    @patch('imaplib.IMAP4_SSL')
    def test_connection(self, mock_imap):
        handler = EmailHandler()
        handler.mail = mock_imap.return_value
        
        handler.mail.login.return_value = ('OK', [b'Logged in'])
        self.assertTrue(handler.connect())
        
        handler.mail.login.return_value = ('NO', [b'Auth failed'])
        self.assertFalse(handler.connect())

if __name__ == '__main__':
    unittest.main()
