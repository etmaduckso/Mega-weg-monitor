import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from unittest.mock import patch
from app.core.telegram_client import TelegramClient

class TestTelegramClient(unittest.TestCase):
    @patch('requests.post')
    def test_send_alert(self, mock_post):
        mock_post.return_value.status_code = 200
        
        client = TelegramClient()
        result = client.send_alert("12345", 1, "Usuário Teste")
        
        self.assertTrue(result)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
