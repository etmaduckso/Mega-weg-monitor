import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

def get_chat_id():
    response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates')
    data = response.json()
    print(data)  # Exibe a resposta para verificar o chat_id

if __name__ == "__main__":
    get_chat_id()
