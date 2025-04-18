import pytest
from unittest.mock import patch
from app.core.telegram_client import TelegramClient
from app.core.user_model import UserModel  # Importar o modelo de usuário
from pymongo import MongoClient  # Importar o cliente MongoDB

@pytest.fixture
def telegram_client():
    mongo_client = MongoClient()  # Criar uma instância do cliente MongoDB
    user_model = UserModel(mongo_client)  # Passar o cliente MongoDB para o modelo de usuário
    return TelegramClient(user_model)  # Passar o modelo de usuário para o cliente

def test_telegram_notification(telegram_client):
    with patch('app.core.telegram_client.TelegramClient.send_notification') as mock_send:
        mock_send.return_value = {'success': True, 'message': 'Notificação enviada com sucesso'}
        response = telegram_client.send_notification({'message': 'Teste', 'channel': 'telegram'})
        assert response['success'] is True
        assert response['message'] == 'Notificação enviada com sucesso'

def test_fetch_monitoring_data(telegram_client):
    with patch('app.core.telegram_client.TelegramClient.fetch_monitoring_data') as mock_fetch:
        mock_fetch.return_value = [
            {'id': 1, 'message': 'Monitoramento ativo', 'status': 'active'},
            {'id': 2, 'message': 'E-mail importante recebido', 'status': 'alert'}
        ]
        data = telegram_client.fetch_monitoring_data()
        assert len(data) == 2
        assert data[0]['message'] == 'Monitoramento ativo'
        assert data[1]['message'] == 'E-mail importante recebido'
