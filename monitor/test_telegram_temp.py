import requests

def send_test_message():
    """Envia uma mensagem de teste para o Telegram usando os parâmetros especificados"""
    token = "6551651698:AAGOcSuXHkG6Kp9y7pKsWBCZZdmLv7oKmOc"
    chat_id = "1395823978"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    message = (
        "🧪 *Teste de Conexão*\n\n"
        f"Se você está vendo esta mensagem no chat {chat_id}, significa que:\n"
        "✅ Bot está funcionando\n"
        "✅ Chat ID está correto\n"
        "✅ Sistema está pronto"
    )
    
    try:
        print(f"Enviando mensagem de teste para chat_id {chat_id} usando token {token[:8]}...")
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        })
        
        if response.status_code == 200:
            print(f"✅ Mensagem enviada com sucesso para chat_id {chat_id}!")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem para chat_id {chat_id}: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para chat_id {chat_id}: {e}")
        return False

if __name__ == "__main__":
    send_test_message()