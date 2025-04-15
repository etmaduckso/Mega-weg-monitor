import unittest
from unittest.mock import patch, MagicMock
from app.core.email_handler import EmailHandler
from app.core.telegram_client import TelegramClient

class TestEmailTelegramIntegration(unittest.TestCase):
    def setUp(self):
        self.email_handler = EmailHandler()
        self.telegram_client = TelegramClient()

    @patch('app.core.email_handler.EmailHandler.check_new_emails')
    @patch('app.core.email_handler.EmailHandler.parse_email')
    @patch('app.core.telegram_client.TelegramClient.send_alert')
    def test_new_email_triggers_telegram_alert(self, mock_send_alert, mock_parse_email, mock_check_new_emails):
        # Mock new emails
        mock_check_new_emails.return_value = ['1']

        # Mock parsed email
        mock_email = MagicMock()
        mock_email.get.return_value = 'Test Subject'
        mock_email['From'] = 'sender@example.com'
        mock_email['Date'] = 'Mon, 1 Jan 2023 12:00:00 +0000'
        mock_parse_email.return_value = mock_email

        # Mock successful alert sending
        mock_send_alert.return_value = True

        # Simulate the process of checking for new emails and sending alerts
        new_emails = self.email_handler.check_new_emails()
        for email_id in new_emails:
            email_data = self.email_handler.parse_email(email_id)
            if email_data:
                alert_sent = self.telegram_client.send_alert(
                    equipment_id="TEST-001",
                    alert_type=3,
                    user="Test User",
                    extra_info={
                        'Subject': email_data.get('subject', 'No subject'),
                        'From': email_data.get('from', 'Unknown sender'),
                        'Date': email_data.get('date', 'Unknown date')
                    }
                )
                self.assertTrue(alert_sent)

        # Assert that the methods were called as expected
        mock_check_new_emails.assert_called_once()
        mock_parse_email.assert_called_once_with('1')
        mock_send_alert.assert_called_once()

if __name__ == '__main__':
    unittest.main()
