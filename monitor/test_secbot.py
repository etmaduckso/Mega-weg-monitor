import requests
import time

def send_test_message():
    """Envia uma mensagem de teste para o Telegram usando o token do Secbot"""
    token = "8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E"
    chat_id = "1395823978"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    message = (
        "🧪 *Teste do Bot Secbot (@Monitorsecbot)*\n\n"
        f"Se você está vendo esta mensagem no chat {chat_id}, significa que:\n"
        "✅ Bot está funcionando\n"
        "✅ Chat ID está correto\n"
        "✅ Configuração foi atualizada com sucesso\n\n"
        "🕒 Enviado em: " + time.strftime("%d/%m/%Y %H:%M:%S")
    )
    
    try:
        print(f"Enviando mensagem de teste para chat_id {chat_id} usando token do Secbot...")
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

# Também podemos testar o token alternativo do Mega Bot
def send_test_message_mega_bot():
    """Envia uma mensagem de teste para o Telegram usando o token do Mega Bot"""
    token = "8093384059:AAEstu6mw9P0AF8gt60gtOA3aHDRo0REcpk"
    chat_id = "1395823978"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    message = (
        "🧪 *Teste do Bot Mega Bot (@Secmegabot)*\n\n"
        f"Se você está vendo esta mensagem no chat {chat_id}, significa que:\n"
        "✅ Bot está funcionando\n"
        "✅ Chat ID está correto\n"
        "✅ Bot alternativo disponível\n\n"
        "🕒 Enviado em: " + time.strftime("%d/%m/%Y %H:%M:%S")
    )
    
    try:
        print(f"Enviando mensagem de teste para chat_id {chat_id} usando token do Mega Bot...")
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
    print("Testando comunicação com o bot Secbot...")
    send_test_message()
    
    print("\nTestando comunicação com o bot Mega Bot (alternativo)...")
    send_test_message_mega_bot()