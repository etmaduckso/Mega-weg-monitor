import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    print("ERRO: Token do Telegram não encontrado no arquivo .env")
    exit()

# Teste de conexão básica
try:
    print("Testando token...")
    response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe', timeout=10)
    print("Resposta da API:", response.json())
    
    if response.json().get('ok'):
        print("\n✅ Token válido! Configure o CHAT_ID:")
        print("1. Envie uma mensagem para seu bot")
        print("2. Execute: python test_telegram_chat_id.py")
    else:
        print("\n❌ Token inválido ou bot não existe")
        print("Crie um novo bot com @BotFather e atualize o .env")
        
except Exception as e:
    print(f"Erro na conexão: {type(e).__name__} - {e}")
