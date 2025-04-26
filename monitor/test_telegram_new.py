import requests
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1395823978')

def escape_markdown(text):
    """Escapa caracteres especiais do Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def send_test_message():
    """Envia uma mensagem de teste para o Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    message = (
        "🧪 *Teste de Conexão*\n\n"
        "Se você está vendo esta mensagem, significa que:\n"
        "✅ Bot está funcionando\n"
        "✅ Chat ID está correto\n"
        "✅ Sistema está pronto"
    )
    
    try:
        print("Enviando mensagem de teste...")
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'MarkdownV2'
        })
        
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

if __name__ == "__main__":
    send_test_message()