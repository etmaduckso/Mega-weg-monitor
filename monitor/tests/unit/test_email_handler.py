import unittest
from unittest.mock import Mock, patch, MagicMock
from app.core.email_handler import EmailHandler
from app.core.notification_client import NotificationClient

class TestEmailHandler(unittest.TestCase):
    @patch('imaplib.IMAP4_SSL')
    def test_connection(self, mock_imap):
        # Configurar o mock do cliente de notificação
        mock_notification_client = MagicMock(spec=NotificationClient)
        
        # Criar instância do EmailHandler com MongoDB mockado
        mock_mongo_db = MagicMock()
        handler = EmailHandler(notification_clients=[mock_notification_client], mongo_db=mock_mongo_db)
        
        # Configurar o mock do IMAP
        mock_imap_instance = mock_imap.return_value
        
        # Simular primeira tentativa bem-sucedida
        mock_imap_instance.login.return_value = ('OK', [b'Logged in'])
        self.assertTrue(handler._connect())
        
        # Simular falha na segunda tentativa
        mock_imap_instance.login.return_value = ('NO', [b'Invalid credentials'])
        self.assertFalse(handler._connect())
        
        # Verificar chamadas ao método login
        mock_imap_instance.login.assert_called_with(handler.username, handler.password)
        
        # Verificar que o status foi atualizado corretamente
        self.assertEqual(handler.monitoring_stats['connection_status'], 'error')

    def test_check_new_emails(self):
        # TODO: Implementar teste de verificação de novos e-mails
        pass

    def test_parse_email(self):
        # TODO: Implementar teste de parsing de e-mail
        pass

if __name__ == '__main__':
    unittest.main()
