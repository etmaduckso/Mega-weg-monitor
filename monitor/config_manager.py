#!/usr/bin/env python3
import os
import json
import imaplib
import configparser
from typing import Dict, Optional

# Configuração dos servidores IMAP disponíveis
IMAP_SERVERS = {
    'megasec': {
        'name': 'Megasec Email',
        'server': '3.209.234.72',
        'port': 993,
        'domain': 'megasec.com.br',
        'instructions': 'Use seu email @megasec.com.br e senha normal'
    },
    'gmail': {
        'name': 'Gmail',
        'server': 'imap.gmail.com',
        'port': 993,
        'domain': 'gmail.com',
        'instructions': '''Para Gmail, você precisa:
1. Ativar verificação em 2 etapas
2. Criar uma Senha de App em: https://myaccount.google.com/security
3. Usar a Senha de App gerada (não sua senha normal)'''
    }
}

def detect_server_from_email(email: str) -> Optional[Dict]:
    """Detecta o servidor IMAP baseado no domínio do e-mail"""
    domain = email.split('@')[-1].lower()
    for server in IMAP_SERVERS.values():
        if server['domain'] in domain:
            return server
    return None

def load_config() -> configparser.ConfigParser:
    """Carrega a configuração do arquivo config.ini"""
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        # Configuração padrão
        config['TELEGRAM'] = {
            'token': '8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E'
        }
        save_config(config)
    return config

def save_config(config: configparser.ConfigParser):
    """Salva a configuração no arquivo config.ini"""
    with open('config.ini', 'w') as f:
        config.write(f)

def update_env_file(config: configparser.ConfigParser):
    """Atualiza o arquivo .env com as configurações atuais"""
    email_configs = {}
    for section in config.sections():
        if section.startswith('EMAIL_'):
            email = section.replace('EMAIL_', '')
            email_configs[email] = {
                'server': config[section]['server'],
                'port': int(config[section]['port']),
                'password': config[section]['password'],
                'telegram_chat_id': config[section]['telegram_chat_id']
            }
    
    env_content = f"""# Configuracao do Telegram Bot
TELEGRAM_TOKEN={config['TELEGRAM']['token']}

# Configuracoes de monitoramento (formato JSON)
MONITORED_EMAILS={json.dumps(email_configs)}
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

def test_email_connection(server: str, port: int, email: str, password: str) -> bool:
    """Testa a conexão com o servidor IMAP"""
    try:
        print(f"Conectando a {server}:{port}...")
        mail = imaplib.IMAP4_SSL(server, port)
        print("Autenticando...")
        mail.login(email, password)
        print("✅ Conexão estabelecida!")
        mail.logout()
        return True
    except Exception as e:
        print(f"Erro ao testar conexão: {e}")
        return False

def list_monitored_emails(config: configparser.ConfigParser):
    """Lista todos os e-mails monitorados"""
    print("\nE-mails monitorados:")
    print("-" * 60)
    found = False
    for section in config.sections():
        if section.startswith('EMAIL_'):
            found = True
            email = section.replace('EMAIL_', '')
            server = config[section]['server']
            chat_id = config[section]['telegram_chat_id']
            print(f"📧 {email}")
            print(f"   Servidor: {server}")
            print(f"   Chat ID: {chat_id}")
            print("-" * 60)
    
    if not found:
        print("Nenhum e-mail configurado!")

def choose_imap_server() -> Optional[Dict]:
    """Permite ao usuário escolher um servidor IMAP"""
    print("\nServidores IMAP disponíveis:")
    print("-" * 60)
    
    # Lista servidores disponíveis
    for i, (key, server) in enumerate(IMAP_SERVERS.items(), 1):
        print(f"{i}. {server['name']}")
        print(f"   Servidor: {server['server']}:{server['port']}")
    
    try:
        choice = int(input("\nEscolha o servidor (0 para cancelar): "))
        if choice == 0:
            return None
        
        if 1 <= choice <= len(IMAP_SERVERS):
            server_key = list(IMAP_SERVERS.keys())[choice - 1]
            server = IMAP_SERVERS[server_key]
            
            # Mostra instruções específicas
            print("\nInstruções importantes:")
            print("-" * 60)
            print(server['instructions'])
            print("-" * 60)
            
            return server
        else:
            print("Opção inválida!")
            return None
    except ValueError:
        print("Entrada inválida!")
        return None

def add_email(config: configparser.ConfigParser):
    """Adiciona um novo e-mail para monitoramento"""
    print("\nAdicionar novo e-mail para monitoramento")
    print("-" * 60)
    
    email = input("\nE-mail: ").strip()
    if not email:
        print("E-mail inválido!")
        return
    
    # Detecta servidor automaticamente
    server_config = detect_server_from_email(email)
    if not server_config:
        print("Domínio de e-mail não suportado!")
        print("Servidores suportados:")
        for server in IMAP_SERVERS.values():
            print(f"- {server['name']} (@{server['domain']})")
        return
    
    print(f"\nServidor detectado: {server_config['name']}")
    print(server_config['instructions'])
    
    section = f"EMAIL_{email}"
    if section in config:
        print("Este e-mail já está configurado!")
        return
    
    password = input("\nSenha ou Senha de App: ").strip()
    if not password:
        print("Senha inválida!")
        return
    
    chat_id = input("Chat ID do Telegram: ").strip()
    if not chat_id:
        print("Chat ID inválido!")
        return
    
    # Testa a conexão antes de salvar
    print("\nTestando conexão...")
    if test_email_connection(
        server_config['server'],
        server_config['port'],
        email,
        password
    ):
        config[section] = {
            'server': server_config['server'],
            'port': str(server_config['port']),
            'password': password,
            'telegram_chat_id': chat_id
        }
        save_config(config)
        update_env_file(config)
        print("✅ E-mail adicionado com sucesso!")
    else:
        print("❌ Falha ao adicionar e-mail. Verifique as credenciais!")

def remove_email(config: configparser.ConfigParser):
    """Remove um e-mail do monitoramento"""
    print("\nRemover e-mail do monitoramento")
    print("-" * 60)
    
    # Lista e-mails disponíveis
    emails = []
    for section in config.sections():
        if section.startswith('EMAIL_'):
            emails.append(section.replace('EMAIL_', ''))
    
    if not emails:
        print("Nenhum e-mail configurado!")
        return
    
    print("E-mails disponíveis:")
    for i, email in enumerate(emails, 1):
        section = f"EMAIL_{email}"
        server = config[section]['server']
        print(f"{i}. {email} ({server})")
    
    try:
        choice = int(input("\nEscolha o número do e-mail para remover (0 para cancelar): "))
        if choice == 0:
            return
        
        if 1 <= choice <= len(emails):
            email = emails[choice - 1]
            section = f"EMAIL_{email}"
            config.remove_section(section)
            save_config(config)
            update_env_file(config)
            print(f"✅ E-mail {email} removido com sucesso!")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Entrada inválida!")

def main():
    """Função principal do gerenciador de configuração"""
    config = load_config()
    
    while True:
        print("\nGerenciador de Configuração do Monitor")
        print("=" * 60)
        print("1. Listar e-mails monitorados")
        print("2. Adicionar novo e-mail")
        print("3. Remover e-mail")
        print("4. Sair")
        
        try:
            choice = int(input("\nEscolha uma opção: "))
            
            if choice == 1:
                list_monitored_emails(config)
            elif choice == 2:
                add_email(config)
            elif choice == 3:
                remove_email(config)
            elif choice == 4:
                print("\nSaindo...")
                break
            else:
                print("Opção inválida!")
        except ValueError:
            print("Entrada inválida!")
        
        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    main()