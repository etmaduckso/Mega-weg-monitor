import requests
import os
import sys
import json
import configparser
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Tenta carregar os tokens do arquivo config.ini
def get_tokens_from_config():
    try:
        config = configparser.ConfigParser()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path)
            
            # Verificar se a seção TELEGRAM existe e tem o token
            global_token = None
            if 'TELEGRAM' in config and 'token' in config['TELEGRAM']:
                global_token = config['TELEGRAM']['token'].strip()
                # Remover eventuais comentários no final da linha
                if '#' in global_token:
                    global_token = global_token.split('#')[0].strip()
                print(f"Token global lido do config.ini: {global_token}")
            
            # Também busca o token específico para sooretama1@megasec.com.br
            specific_token = None
            if 'IMAP_sooretama1@megasec.com.br' in config and 'telegram_token' in config['IMAP_sooretama1@megasec.com.br']:
                specific_token = config['IMAP_sooretama1@megasec.com.br']['telegram_token'].strip()
                print(f"Token específico lido do config.ini: {specific_token}")
            
            return global_token, specific_token
    except Exception as e:
        print(f"Erro ao ler tokens do config.ini: {e}")
    
    return None, None

# Configuração do Telegram
# Lê os tokens diretamente do arquivo config.ini
global_token, specific_token = get_tokens_from_config()

# Usamos diretamente os tokens lidos do arquivo, sem permitir substituição
# Se não conseguir ler do arquivo, usa o valor padrão
TELEGRAM_TOKEN = global_token if global_token else '6551651698:AAGOcSuXHkG6Kp9y7pKsWBCZZdmLv7oKmOc'
TELEGRAM_SPECIFIC_TOKEN = specific_token if specific_token else '7645011179:AAFv5DL6T-xvY_gfZgUohn-CsTgHcoPxMME'
TELEGRAM_CHAT_ID = '1395823978'
TELEGRAM_SPECIFIC_CHAT_ID = '8052351981'  # Chat ID específico para sooretama1@megasec.com.br

# Exibir os tokens para depuração
print(f"Token global usado: {TELEGRAM_TOKEN}")
print(f"Token específico usado: {TELEGRAM_SPECIFIC_TOKEN}")

def escape_markdown(text):
    """Escapa caracteres especiais do Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def send_test_message(chat_id=None, token=None):
    """Envia uma mensagem de teste para o Telegram"""
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID
    
    if token is None:
        token = TELEGRAM_TOKEN
        
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
            'parse_mode': 'MarkdownV2'
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

def test_welcome_message(chat_id=None, token=None):
    """Testa o envio da mensagem de boas-vindas (comando /start)"""
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID
    
    if token is None:
        token = TELEGRAM_TOKEN
    
    # Simula uma mensagem de boas-vindas em português que seria enviada pelo novo manipulador de comandos
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    message = (
        "🔔 *Bem-vindo ao WegNots!*\n\n"
        "✅ Seu cadastro foi ativado com sucesso!\n\n"
        "Agora você receberá notificações de e-mails importantes diretamente aqui no Telegram.\n\n"
        "Não é necessário fazer mais nada. O sistema está funcionando automaticamente."
    )
    
    try:
        print(f"Enviando mensagem de boas-vindas para chat_id {chat_id} usando token {token[:8]}...")
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        })
        
        if response.status_code == 200:
            print(f"✅ Mensagem de boas-vindas enviada com sucesso para chat_id {chat_id}!")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem de boas-vindas para chat_id {chat_id}: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de boas-vindas para chat_id {chat_id}: {e}")
        return False

def configure_bot_commands(token=None):
    """Configura os comandos disponíveis no bot"""
    if token is None:
        token = TELEGRAM_TOKEN
        
    url = f"https://api.telegram.org/bot{token}/setMyCommands"
    commands = [
        {"command": "start", "description": "Iniciar o monitoramento de e-mails"},
        {"command": "status", "description": "Verificar status do sistema"},
        {"command": "help", "description": "Exibir ajuda"}
    ]
    
    try:
        print(f"Configurando comandos do bot usando token {token[:8]}...")
        response = requests.post(url, json={"commands": commands})
        
        if response.status_code == 200:
            print("✅ Comandos do bot configurados com sucesso!")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Erro ao configurar comandos do bot: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar comandos do bot: {e}")
        return False

def test_all():
    """Executa todos os testes em sequência"""
    results = {
        "configure_commands_global": configure_bot_commands(TELEGRAM_TOKEN),
        "configure_commands_specific": configure_bot_commands(TELEGRAM_SPECIFIC_TOKEN),
        "global_chat": send_test_message(TELEGRAM_CHAT_ID, TELEGRAM_TOKEN),
        "specific_chat": send_test_message(TELEGRAM_SPECIFIC_CHAT_ID, TELEGRAM_SPECIFIC_TOKEN),
        "welcome_global": test_welcome_message(TELEGRAM_CHAT_ID, TELEGRAM_TOKEN),
        "welcome_specific": test_welcome_message(TELEGRAM_SPECIFIC_CHAT_ID, TELEGRAM_SPECIFIC_TOKEN)
    }
    
    # Exibe um resumo dos resultados
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    success = True
    for test_name, result in results.items():
        status = "✅ SUCESSO" if result else "❌ FALHA"
        print(f"{test_name}: {status}")
        if not result:
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Todos os testes foram bem-sucedidos!")
    else:
        print("⚠️ Alguns testes falharam. Verifique as configurações do Telegram.")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    # Opção para testar um chat_id específico
    if len(sys.argv) > 1:
        if sys.argv[1] == "--welcome":
            # Teste apenas as mensagens de boas-vindas
            if len(sys.argv) > 2:
                test_welcome_message(sys.argv[2])
            else:
                # Teste para ambos os chat_ids
                print("Testando mensagem de boas-vindas para chat_id global...")
                test_welcome_message(TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)
                print("\nTestando mensagem de boas-vindas para chat_id específico...")
                test_welcome_message(TELEGRAM_SPECIFIC_CHAT_ID, TELEGRAM_SPECIFIC_TOKEN)
        elif sys.argv[1] == "--commands":
            # Apenas configura os comandos do bot
            configure_bot_commands()
        elif sys.argv[1] == "--all":
            # Executa todos os testes
            test_all()
        elif sys.argv[1] == "--test-global":
            # Testa apenas o token global
            send_test_message(TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)
        elif sys.argv[1] == "--test-specific":
            # Testa apenas o token específico
            send_test_message(TELEGRAM_SPECIFIC_CHAT_ID, TELEGRAM_SPECIFIC_TOKEN)
        else:
            # Assume que é um chat_id
            chat_id = sys.argv[1]
            send_test_message(chat_id)
    else:
        # Comportamento padrão: teste as mensagens normais para ambos os chat_ids
        print("Testando chat_id global com token global...")
        global_result = send_test_message(TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)
        
        print("\nTestando chat_id específico para sooretama1@megasec.com.br com token específico...")
        specific_result = send_test_message(TELEGRAM_SPECIFIC_CHAT_ID, TELEGRAM_SPECIFIC_TOKEN)
        
        if global_result and specific_result:
            print("\n✅ Todos os testes foram bem-sucedidos!")
        elif global_result:
            print("\n⚠️ Apenas o chat_id global foi bem-sucedido. Verifique a configuração do chat_id específico.")
        elif specific_result:
            print("\n⚠️ Apenas o chat_id específico foi bem-sucedido. Verifique a configuração do chat_id global.")
        else:
            print("\n❌ Ambos os testes falharam. Verifique as configurações do Telegram.")