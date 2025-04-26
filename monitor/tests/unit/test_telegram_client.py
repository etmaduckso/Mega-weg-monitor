import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from unittest.mock import Mock, patch, MagicMock
from app.core.telegram_client import TelegramClient
from app.core.user_model import UserModel

class TestTelegramClient(unittest.TestCase):
    def setUp(self):
        # Criar mock do UserModel
        self.mock_user_model = MagicMock(spec=UserModel)
        self.mock_user_model.get_active_chat_ids.return_value = ['123456789']
        self.mock_user_model.get_users_by_email.return_value = [
            {
                'chat_id': '123456789',
                'is_active': True,
                'notification_preferences': {
                    'receive_criticals': True,
                    'receive_moderates': True,
                    'receive_low': True
                }
            }
        ]
        
        # Criar instância do TelegramClient com o mock
        self.client = TelegramClient(user_model=self.mock_user_model)

    @patch('requests.post')
    def test_send_alert(self, mock_post):
        # Configurar o mock do requests.post
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'ok': True}

        # Testar envio de alerta
        result = self.client.send_alert(
            equipment_id='TEST-001',
            alert_type=1,
            user='test@example.com',
            extra_info={
                'subject': 'Test Subject',
                'from': 'sender@example.com',
                'date': '2025-04-24 19:45:00',
                'body': 'Test message body'
            }
        )
        
        # Verificar se o alerta foi enviado com sucesso
        self.assertTrue(result)
        
        # Verificar se o UserModel foi consultado corretamente
        self.mock_user_model.get_users_by_email.assert_called_once()
        
        # Verificar se o requests.post foi chamado com os parâmetros corretos
        mock_post.assert_called_once()
        
        # Verificar se a URL e os dados da mensagem estão corretos na chamada
        args, kwargs = mock_post.call_args
        self.assertIn('/sendMessage', kwargs.get('url', ''))
        self.assertIn('123456789', kwargs.get('json', {}).get('chat_id', ''))

    def test_notification_preferences(self):
        # Teste para verificar se as preferências de notificação são respeitadas
        self.mock_user_model.get_users_by_email.return_value = [
            {
                'chat_id': '123456789',
                'is_active': True,
                'notification_preferences': {
                    'receive_criticals': False,
                    'receive_moderates': True,
                    'receive_low': True
                }
            }
        ]
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            
            # Tentar enviar alerta crítico quando as notificações críticas estão desativadas
            result = self.client.send_alert(
                equipment_id='TEST-001',
                alert_type=1,  # Alerta crítico
                user='test@example.com',
                extra_info={'subject': 'Test'}
            )
            
            # Verificar que nenhuma mensagem foi enviada
            mock_post.assert_not_called()
            self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
