#!/usr/bin/env python3
import os
import json
import imaplib
import configparser
import re
import logging
import requests
from typing import Dict, Optional, List, Tuple
from datetime import datetime

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/config_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuração dos servidores IMAP disponíveis
IMAP_SERVERS = {
    'megasec': {
        'name': 'Megasec Email',
        'server': 'mail.megasec.com.br',  # Corrigido para o servidor correto conforme documentação
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
    },
    'outlook': {
        'name': 'Outlook/Hotmail',
        'server': 'outlook.office365.com',
        'port': 993,
        'domain': 'outlook.com',
        'instructions': 'Use seu email Outlook/Hotmail e senha normal'
    },
    'yahoo': {
        'name': 'Yahoo Mail',
        'server': 'imap.mail.yahoo.com',
        'port': 993,
        'domain': 'yahoo.com',
        'instructions': '''Para Yahoo Mail, você precisa:
1. Ativar verificação em 2 etapas
2. Gerar uma senha de app
3. Usar a senha de app gerada (não sua senha normal)'''
    }
}

def detect_server_from_email(email: str) -> Optional[Dict]:
    """Detecta o servidor IMAP baseado no domínio do e-mail"""
    domain = email.split('@')[-1].lower()
    for server in IMAP_SERVERS.values():
        if server['domain'] in domain:
            return server
    return None

def is_valid_email(email: str) -> bool:
    """Valida o formato do endereço de email"""
    # Expressão regular para validação básica de email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def is_valid_chat_id(chat_id: str) -> bool:
    """Valida o formato do chat_id do Telegram"""
    # Chat IDs do Telegram podem ser numéricos positivos ou negativos
    try:
        int(chat_id)
        return True
    except ValueError:
        return False

def load_config() -> configparser.ConfigParser:
    """Carrega a configuração do arquivo config.ini"""
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        logger.info("Arquivo de configuração carregado com sucesso.")
    else:
        # Configuração padrão apenas para a seção TELEGRAM
        config['TELEGRAM'] = {}
        logger.info("Arquivo de configuração não encontrado. Criando novo arquivo.")
        save_config(config)
    return config

def save_config(config: configparser.ConfigParser):
    """Salva a configuração no arquivo config.ini"""
    with open('config.ini', 'w') as f:
        config.write(f)
    logger.info("Configuração salva com sucesso.")

def update_env_file(config: configparser.ConfigParser):
    """Atualiza o arquivo .env com as configurações atuais"""
    email_configs = {}
    
    for section in config.sections():
        if section.startswith('IMAP_'):
            # Ignoramos seções especiais como IMAP_PRIMARY e IMAP_SECONDARY
            # para o arquivo .env, pois são tratadas pelo código Python diretamente
            if section in ['IMAP_PRIMARY', 'IMAP_SECONDARY']:
                continue
                
            # Para seções como IMAP_user@example.com
            email = section.replace('IMAP_', '')
            if 'username' in config[section]:
                email_config = {
                    'server': config[section]['server'],
                    'port': int(config[section]['port']),
                    'username': config[section]['username'],
                    'password': config[section]['password'],
                    'is_active': config[section].getboolean('is_active', True),
                    'telegram_chat_id': config[section].get('telegram_chat_id', '')
                }
                
                # Adiciona token específico se existir
                if 'telegram_token' in config[section]:
                    email_config['telegram_token'] = config[section]['telegram_token']
                    
                email_configs[email] = email_config
    
    # Configurações globais do Telegram
    telegram_token = config['TELEGRAM'].get('token', '')
    telegram_chat_id = config['TELEGRAM'].get('chat_id', '')
    
    env_content = f"""# Configuracao do Telegram Bot
TELEGRAM_TOKEN={telegram_token}
TELEGRAM_CHAT_ID={telegram_chat_id}

# Configuracoes de monitoramento (formato JSON)
MONITORED_EMAILS={json.dumps(email_configs)}
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    logger.info("Arquivo .env atualizado com sucesso.")

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiais do Markdown para formatação correta no Telegram"""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def send_telegram_notification(config: configparser.ConfigParser, message: str, chat_id: str = None, token: str = None) -> bool:
    """Envia notificação via Telegram usando as configurações fornecidas ou as padrões do arquivo config.ini"""
    if 'TELEGRAM' not in config:
        logger.error("Configuração do Telegram não encontrada!")
        return False
    
    # Usa os parâmetros fornecidos ou os valores padrão do config
    if not token:
        token = config['TELEGRAM'].get('token', '')
    if not chat_id:
        chat_id = config['TELEGRAM'].get('chat_id', '')
    
    if not token or not chat_id:
        logger.error("Token ou Chat ID do Telegram ausentes!")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'MarkdownV2',
            'disable_web_page_preview': True
        }, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Notificação enviada com sucesso para chat_id {chat_id}")
            return True
        else:
            logger.error(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exceção ao enviar notificação: {e}")
        return False

def send_system_startup_notification(config: configparser.ConfigParser) -> bool:
    """
    Envia notificação de inicialização do sistema para todos os destinatários configurados.
    Para o chat ID global, mostra todas as contas monitoradas.
    Para chat IDs específicos (com tokens personalizados), mostra apenas as contas associadas a eles.
    """
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    base_message = (
        "🟢 *WegNots Monitor Iniciado*\n\n"
        f"⏰ {escape_markdown(current_time)}\n"
        "✅ Sistema de monitoramento iniciado com sucesso\\.\n"
        "✉️ Monitorando e\\-mails\\.\\.\\."
    )
    
    # Configurações globais
    global_token = config['TELEGRAM'].get('token', '')
    global_chat_id = config['TELEGRAM'].get('chat_id', '')
    
    # Encontra todas as contas de email ativas
    active_accounts = []
    for section in config.sections():
        if section.startswith('IMAP_') and config[section].getboolean('is_active', True):
            if 'username' in config[section]:
                active_accounts.append(config[section]['username'])
    
    # 1. Enviar notificação para o chat ID global com todas as contas
    global_message = base_message
    if active_accounts:
        global_message += f"\n\n📨 Contas monitoradas: {len(active_accounts)}"
        for i, account in enumerate(active_accounts, 1):
            global_message += f"\n   {i}\\. {escape_markdown(account)}"
    
    global_success = False
    if global_token and global_chat_id:
        global_success = send_telegram_notification(config, global_message)
    
    # 2. Enviar notificações personalizadas para cada email com configurações específicas
    accounts_with_specific_settings = {}
    
    # Agrupar por destinos específicos (combinações únicas de chat_id e token)
    for section in config.sections():
        if not section.startswith('IMAP_') or not config[section].getboolean('is_active', True):
            continue
            
        if 'username' not in config[section]:
            continue
            
        username = config[section]['username']
        
        # Obter chat_id e token (específico ou global)
        specific_chat_id = config[section].get('telegram_chat_id', '')
        specific_token = config[section].get('telegram_token', '')
        
        # Se não tiver chat_id específico, use o global
        chat_id_to_use = specific_chat_id or global_chat_id
        # Se não tiver token específico, use o global
        token_to_use = specific_token or global_token
        
        # Apenas prossegue se ambos estiverem disponíveis (seja específico ou global)
        if not chat_id_to_use or not token_to_use:
            continue
        
        # Cria uma chave única para este destino
        destination_key = (chat_id_to_use, token_to_use)
        
        # Adiciona o email à lista deste destino específico
        if destination_key not in accounts_with_specific_settings:
            accounts_with_specific_settings[destination_key] = []
            
        accounts_with_specific_settings[destination_key].append(username)
    
    # Envia notificações personalizadas
    specific_success = True
    for (chat_id, token), accounts in accounts_with_specific_settings.items():
        if not accounts:
            continue
            
        specific_message = base_message
        specific_message += f"\n\n📨 Contas monitoradas: {len(accounts)}"
        for i, account in enumerate(accounts, 1):
            specific_message += f"\n   {i}\\. {escape_markdown(account)}"
            
        # Não enviamos para o chat_id global se já foi enviado
        if chat_id == global_chat_id and token == global_token and global_success:
            continue
            
        success = send_telegram_notification(config, specific_message, chat_id, token)
        specific_success = specific_success and success
        
    # Retorna True se pelo menos uma notificação foi enviada com sucesso
    return global_success or specific_success

def send_system_shutdown_notification(config: configparser.ConfigParser) -> bool:
    """
    Envia notificação de encerramento do sistema para todos os destinatários configurados.
    Para o chat ID global, mostra uma mensagem padrão de encerramento.
    Para chat IDs específicos (com tokens personalizados), mostra uma mensagem personalizada 
    indicando quais contas específicas estão sendo encerradas.
    """
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    base_message = (
        "🔴 *WegNots Monitor Encerrado*\n\n"
        f"⏰ {escape_markdown(current_time)}\n"
        "✅ Sistema encerrado de forma segura\\.\n"
        "🔔 Monitoramento interrompido\\."
    )
    
    # Configurações globais
    global_token = config['TELEGRAM'].get('token', '')
    global_chat_id = config['TELEGRAM'].get('chat_id', '')
    
    # 1. Enviar notificação para o chat ID global
    global_success = False
    if global_token and global_chat_id:
        global_success = send_telegram_notification(config, base_message)
    
    # 2. Enviar notificações personalizadas para cada email com configurações específicas
    accounts_with_specific_settings = {}
    
    # Agrupar por destinos específicos (combinações únicas de chat_id e token)
    for section in config.sections():
        if not section.startswith('IMAP_') or not config[section].getboolean('is_active', True):
            continue
            
        if 'username' not in config[section]:
            continue
            
        username = config[section]['username']
        
        # Obter chat_id e token (específico ou global)
        specific_chat_id = config[section].get('telegram_chat_id', '')
        specific_token = config[section].get('telegram_token', '')
        
        # Se não tiver chat_id específico, use o global
        chat_id_to_use = specific_chat_id or global_chat_id
        # Se não tiver token específico, use o global
        token_to_use = specific_token or global_token
        
        # Apenas prossegue se ambos estiverem disponíveis (seja específico ou global)
        if not chat_id_to_use or not token_to_use:
            continue
        
        # Cria uma chave única para este destino
        destination_key = (chat_id_to_use, token_to_use)
        
        # Adiciona o email à lista deste destino específico
        if destination_key not in accounts_with_specific_settings:
            accounts_with_specific_settings[destination_key] = []
            
        accounts_with_specific_settings[destination_key].append(username)
    
    # Envia notificações personalizadas
    specific_success = True
    for (chat_id, token), accounts in accounts_with_specific_settings.items():
        if not accounts:
            continue
            
        specific_message = base_message
        
        # Adiciona informação sobre as contas que estavam sendo monitoradas
        if len(accounts) > 1:
            specific_message += f"\n\n📨 O monitoramento das seguintes contas foi encerrado:"
            for i, account in enumerate(accounts, 1):
                specific_message += f"\n   {i}\\. {escape_markdown(account)}"
        else:
            specific_message += f"\n\n📨 O monitoramento da conta {escape_markdown(accounts[0])} foi encerrado\\."
        
        # Não enviamos para o chat_id global se já foi enviado
        if chat_id == global_chat_id and token == global_token and global_success:
            continue
            
        success = send_telegram_notification(config, specific_message, chat_id, token)
        specific_success = specific_success and success
        
    # Retorna True se pelo menos uma notificação foi enviada com sucesso
    return global_success or specific_success

def test_email_connection(server: str, port: int, username: str, password: str) -> Tuple[bool, str]:
    """Testa a conexão com o servidor IMAP, retornando sucesso e mensagem de erro detalhada"""
    try:
        print(f"Conectando a {server}:{port}...")
        mail = imaplib.IMAP4_SSL(server, port)
        print("Autenticando...")
        mail.login(username, password)
        print("✅ Conexão estabelecida!")
        mail.logout()
        return True, "Conexão estabelecida com sucesso."
    except imaplib.IMAP4.error as e:
        error_msg = f"Erro de autenticação IMAP: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return False, error_msg
    except ConnectionRefusedError:
        error_msg = f"Conexão recusada pelo servidor {server}:{port}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return False, error_msg
    except TimeoutError:
        error_msg = f"Tempo limite excedido ao conectar a {server}:{port}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Erro ao testar conexão: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return False, error_msg

def list_monitored_emails(config: configparser.ConfigParser):
    """Lista todos os e-mails monitorados"""
    print("\nE-mails monitorados:")
    print("-" * 60)
    found = False
    
    # Primeiro, tente encontrar as contas no formato IMAP_PRIMARY
    special_accounts = []
    for section in config.sections():
        if section in ['IMAP_PRIMARY', 'IMAP_SECONDARY'] and 'username' in config[section]:
            found = True
            email = config[section]['username']
            server = config[section]['server']
            special_accounts.append(section)
            print(f"📧 {email} ({section})")
            print(f"   Servidor: {server}")
            print(f"   Porta: {config[section]['port']}")
            print(f"   Ativo: {config[section].getboolean('is_active', True)}")
            print(f"   Chat ID: {config[section].get('telegram_chat_id', 'não configurado')}")
            
            # Verifica se há token específico
            if 'telegram_token' in config[section]:
                token = config[section]['telegram_token']
                masked_token = "••••" + token[-4:] if token else "não configurado"
                print(f"   Token específico: {masked_token}")
            else:
                print(f"   Token: Global")
                
            print("-" * 60)
    
    # Depois, procure outras contas no formato IMAP_email@example.com
    for section in config.sections():
        if section.startswith('IMAP_') and section not in special_accounts:
            found = True
            email = section.replace('IMAP_', '')
            if 'username' in config[section]:
                email = config[section]['username']
            server = config[section]['server']
            print(f"📧 {email}")
            print(f"   Servidor: {server}")
            print(f"   Porta: {config[section]['port']}")
            print(f"   Ativo: {config[section].getboolean('is_active', True)}")
            print(f"   Chat ID: {config[section].get('telegram_chat_id', 'não configurado')}")
            
            # Verifica se há token específico
            if 'telegram_token' in config[section]:
                token = config[section]['telegram_token']
                masked_token = "••••" + token[-4:] if token else "não configurado"
                print(f"   Token específico: {masked_token}")
            else:
                print(f"   Token: Global")
                
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
    
    # Solicitar informações básicas do email
    email = input("Digite o endereço de e-mail: ").strip()
    
    if not email:
        print("Operação cancelada.")
        return
        
    if not is_valid_email(email):
        print("❌ Formato de e-mail inválido!")
        return
    
    # Detectar servidor automaticamente ou pedir para escolher
    server_info = detect_server_from_email(email)
    if not server_info:
        print("\nNão foi possível detectar o servidor automaticamente.")
        server_info = choose_imap_server()
        if not server_info:
            print("Operação cancelada.")
            return
    else:
        print(f"\nDetectado servidor: {server_info['name']} ({server_info['server']}:{server_info['port']})")
        print(server_info['instructions'])
        
        # Confirmar se quer usar o servidor detectado
        confirm = input("\nUsar este servidor? (s/n): ").lower()
        if confirm != 's':
            server_info = choose_imap_server()
            if not server_info:
                print("Operação cancelada.")
                return
    
    # Solicitar senha
    password = input(f"\nSenha para {email}: ")
    if not password:
        print("Operação cancelada.")
        return
    
    # Testar conexão
    print(f"\nTestando conexão para {email}...")
    success, msg = test_email_connection(
        server_info['server'], 
        server_info['port'], 
        email, 
        password
    )
    
    if not success:
        retry = input("\nO teste de conexão falhou. Deseja salvar mesmo assim? (s/n): ").lower()
        if retry != 's':
            print("Operação cancelada.")
            return
    
    # Opções avançadas
    use_custom_telegram = input("\nDeseja configurar notificações personalizadas do Telegram? (s/n): ").lower()
    custom_chat_id = ""
    custom_token = ""
    
    if use_custom_telegram == 's':
        custom_chat_id = input("Chat ID específico para este e-mail (deixe vazio para usar o global): ").strip()
        if custom_chat_id and not is_valid_chat_id(custom_chat_id):
            print("❌ Chat ID inválido! Deve ser um número inteiro.")
            custom_chat_id = ""
        
        custom_token = input("Token específico para este e-mail (deixe vazio para usar o global): ").strip()
    
    # Determinar qual seção usar
    section_name = f"IMAP_{email}"
    
    # Verificar se já existe
    if section_name in config:
        overwrite = input(f"\nO e-mail {email} já existe na configuração. Deseja sobrescrever? (s/n): ").lower()
        if overwrite != 's':
            print("Operação cancelada.")
            return
    
    # Criar seção
    config[section_name] = {
        'server': server_info['server'],
        'port': str(server_info['port']),
        'username': email,
        'password': password,
        'is_active': 'True'
    }
    
    # Adicionar configurações personalizadas do Telegram, se fornecidas
    if custom_chat_id:
        config[section_name]['telegram_chat_id'] = custom_chat_id
    if custom_token:
        config[section_name]['telegram_token'] = custom_token
    
    # Salvar configuração
    save_config(config)
    update_env_file(config)
    
    print(f"\n✅ E-mail {email} adicionado com sucesso ao monitoramento!")
    return True

def remove_email(config: configparser.ConfigParser):
    """Remove um e-mail do monitoramento"""
    print("\nRemover e-mail do monitoramento")
    print("-" * 60)
    
    # Lista todos os e-mails disponíveis
    email_sections = []
    for section in config.sections():
        if section.startswith('IMAP_') and 'username' in config[section]:
            email_sections.append((section, config[section]['username']))
    
    if not email_sections:
        print("Nenhum e-mail configurado para remoção!")
        return
    
    print("E-mails disponíveis para remoção:")
    for i, (section, email) in enumerate(email_sections, 1):
        print(f"{i}. {email} ({section})")
    
    try:
        choice = int(input("\nEscolha o e-mail a ser removido (0 para cancelar): "))
        if choice == 0:
            print("Operação cancelada.")
            return
        
        if 1 <= choice <= len(email_sections):
            section_to_remove = email_sections[choice - 1][0]
            email_to_remove = email_sections[choice - 1][1]
            
            # Confirmar remoção
            confirm = input(f"Tem certeza que deseja remover {email_to_remove}? (s/n): ").lower()
            if confirm == 's':
                config.remove_section(section_to_remove)
                save_config(config)
                update_env_file(config)
                print(f"✅ E-mail {email_to_remove} removido com sucesso!")
            else:
                print("Operação cancelada.")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Entrada inválida!")
    except Exception as e:
        logger.error(f"Erro ao remover e-mail: {str(e)}")
        print(f"Ocorreu um erro: {str(e)}")

def edit_email(config: configparser.ConfigParser):
    """Edita as configurações de um e-mail monitorado"""
    print("\nEditar configurações de e-mail")
    print("-" * 60)
    
    # Lista todos os e-mails disponíveis
    email_sections = []
    for section in config.sections():
        if section.startswith('IMAP_') and 'username' in config[section]:
            email_sections.append((section, config[section]['username']))
    
    if not email_sections:
        print("Nenhum e-mail configurado para edição!")
        return
    
    print("E-mails disponíveis para edição:")
    for i, (section, email) in enumerate(email_sections, 1):
        print(f"{i}. {email} ({section})")
    
    try:
        choice = int(input("\nEscolha o e-mail a ser editado (0 para cancelar): "))
        if choice == 0:
            print("Operação cancelada.")
            return
        
        if 1 <= choice <= len(email_sections):
            section = email_sections[choice - 1][0]
            email = email_sections[choice - 1][1]
            
            print(f"\nEditando configurações para: {email}")
            print("-" * 60)
            
            # Mostrar opções de edição
            print("Opções de edição:")
            print("1. Mudar servidor/porta")
            print("2. Mudar senha")
            print("3. Ativar/desativar monitoramento")
            print("4. Configurar notificações personalizadas")
            print("5. Voltar")
            
            edit_choice = int(input("\nEscolha uma opção: "))
            
            if edit_choice == 1:
                # Editar servidor e porta
                print("\nMudando servidor/porta:")
                new_server = input(f"Novo servidor [{config[section]['server']}]: ") or config[section]['server']
                try:
                    new_port = int(input(f"Nova porta [{config[section]['port']}]: ") or config[section]['port'])
                    config[section]['server'] = new_server
                    config[section]['port'] = str(new_port)
                    save_config(config)
                    update_env_file(config)
                    print("✅ Servidor/porta atualizados com sucesso!")
                except ValueError:
                    print("❌ Porta inválida! Operação cancelada.")
            
            elif edit_choice == 2:
                # Editar senha
                print("\nMudando senha:")
                new_password = input("Nova senha: ")
                if new_password:
                    # Testar conexão com a nova senha
                    print("\nTestando nova senha...")
                    success, msg = test_email_connection(
                        config[section]['server'],
                        int(config[section]['port']),
                        config[section]['username'],
                        new_password
                    )
                    
                    if success:
                        config[section]['password'] = new_password
                        save_config(config)
                        update_env_file(config)
                        print("✅ Senha atualizada com sucesso!")
                    else:
                        print(f"❌ Falha no teste de conexão: {msg}")
                        retry = input("Deseja salvar a senha mesmo assim? (s/n): ").lower()
                        if retry == 's':
                            config[section]['password'] = new_password
                            save_config(config)
                            update_env_file(config)
                            print("✅ Senha atualizada (mas o teste de conexão falhou)!")
                else:
                    print("Operação cancelada.")
            
            elif edit_choice == 3:
                # Ativar/desativar
                is_active = config[section].getboolean('is_active', True)
                print(f"\nStatus atual: {'Ativo' if is_active else 'Inativo'}")
                
                new_status = input("Deseja ativar ou desativar? (a/d): ").lower()
                if new_status == 'a':
                    config[section]['is_active'] = 'True'
                    save_config(config)
                    update_env_file(config)
                    print("✅ E-mail ativado com sucesso!")
                elif new_status == 'd':
                    config[section]['is_active'] = 'False'
                    save_config(config)
                    update_env_file(config)
                    print("✅ E-mail desativado com sucesso!")
                else:
                    print("Opção inválida. Operação cancelada.")
            
            elif edit_choice == 4:
                # Configurar notificações personalizadas
                print("\nConfigurando notificações personalizadas:")
                
                current_chat_id = config[section].get('telegram_chat_id', '')
                current_token = config[section].get('telegram_token', '')
                
                print(f"Chat ID atual: {current_chat_id or 'Usando configuração global'}")
                print(f"Token atual: {'Personalizado' if current_token else 'Usando configuração global'}")
                
                new_chat_id = input("Novo Chat ID (deixe vazio para usar global): ")
                if new_chat_id:
                    if is_valid_chat_id(new_chat_id):
                        config[section]['telegram_chat_id'] = new_chat_id
                    else:
                        print("❌ Chat ID inválido! Deve ser um número inteiro.")
                        new_chat_id = ""
                
                new_token = input("Novo Token (deixe vazio para usar global): ")
                if new_token:
                    config[section]['telegram_token'] = new_token
                
                if new_chat_id or new_token:
                    save_config(config)
                    update_env_file(config)
                    print("✅ Configurações de notificação atualizadas!")
                else:
                    print("Nenhuma alteração realizada.")
            
            elif edit_choice == 5:
                print("Voltando ao menu principal...")
                return
            else:
                print("Opção inválida.")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Entrada inválida!")
    except Exception as e:
        logger.error(f"Erro ao editar e-mail: {str(e)}")
        print(f"Ocorreu um erro: {str(e)}")

def setup_telegram(config: configparser.ConfigParser):
    """Configura ou atualiza as configurações do Telegram"""
    print("\nConfiguração do Telegram")
    print("-" * 60)
    
    # Verifica se a seção TELEGRAM existe
    if 'TELEGRAM' not in config:
        config['TELEGRAM'] = {}
        
    # Mostrar configuração atual
    current_token = config['TELEGRAM'].get('token', '')
    current_chat_id = config['TELEGRAM'].get('chat_id', '')
    
    masked_token = "••••" + current_token[-4:] if current_token and len(current_token) > 4 else "não configurado"
    print(f"Token atual: {masked_token}")
    print(f"Chat ID atual: {current_chat_id or 'não configurado'}")
    
    print("\nEscolha o que deseja configurar:")
    print("1. Token do Bot")
    print("2. Chat ID")
    print("3. Ambos")
    print("4. Verificar configuração atual")
    print("5. Voltar")
    
    try:
        choice = int(input("\nEscolha uma opção: "))
        
        if choice == 1:
            # Configurar apenas o token
            new_token = input("\nDigite o novo token do bot (gerado pelo BotFather): ")
            if new_token:
                config['TELEGRAM']['token'] = new_token.strip()
                save_config(config)
                update_env_file(config)
                print("✅ Token atualizado com sucesso!")
            else:
                print("Operação cancelada.")
                
        elif choice == 2:
            # Configurar apenas o Chat ID
            new_chat_id = input("\nDigite o novo Chat ID: ")
            if new_chat_id and is_valid_chat_id(new_chat_id):
                config['TELEGRAM']['chat_id'] = new_chat_id.strip()
                save_config(config)
                update_env_file(config)
                print("✅ Chat ID atualizado com sucesso!")
            elif new_chat_id:
                print("❌ Chat ID inválido! Deve ser um número inteiro.")
            else:
                print("Operação cancelada.")
                
        elif choice == 3:
            # Configurar ambos
            new_token = input("\nDigite o novo token do bot (gerado pelo BotFather): ")
            new_chat_id = input("Digite o novo Chat ID: ")
            
            if new_token and new_chat_id:
                if is_valid_chat_id(new_chat_id):
                    config['TELEGRAM']['token'] = new_token.strip()
                    config['TELEGRAM']['chat_id'] = new_chat_id.strip()
                    save_config(config)
                    update_env_file(config)
                    print("✅ Configurações atualizadas com sucesso!")
                    
                    # Oferecer teste imediato
                    test_now = input("\nDeseja testar as novas configurações agora? (s/n): ").lower()
                    if test_now == 's':
                        test_telegram_notifications(config)
                else:
                    print("❌ Chat ID inválido! Deve ser um número inteiro.")
            else:
                print("Operação cancelada.")
                
        elif choice == 4:
            # Apenas verificar a configuração atual
            if current_token and current_chat_id:
                print("\n✅ Configuração do Telegram está completa.")
                
                # Oferecer teste
                test_now = input("\nDeseja testar a configuração atual? (s/n): ").lower()
                if test_now == 's':
                    test_telegram_notifications(config)
            else:
                print("\n❌ Configuração do Telegram está incompleta!")
                missing = []
                if not current_token:
                    missing.append("Token")
                if not current_chat_id:
                    missing.append("Chat ID")
                print(f"Itens faltantes: {', '.join(missing)}")
                
        elif choice == 5:
            # Voltar ao menu principal
            print("Voltando ao menu principal...")
            return
        
        else:
            print("Opção inválida!")
            
    except ValueError:
        print("Entrada inválida!")
    except Exception as e:
        logger.error(f"Erro ao configurar Telegram: {str(e)}")
        print(f"Ocorreu um erro: {str(e)}")

def migrate_old_format(config: configparser.ConfigParser) -> bool:
    """Migra formatos antigos de configuração para o novo formato IMAP_*"""
    migrated = False
    
    # Verificar se existem seções antigas com formatos não padronizados
    old_email_sections = []
    for section in config.sections():
        # Procura por seções que não começam com IMAP_ mas têm parâmetros de email
        if not section.startswith('IMAP_') and section not in ['TELEGRAM'] and 'server' in config[section] and 'username' in config[section]:
            old_email_sections.append(section)
    
    # Migrar cada seção antiga para o novo formato
    for old_section in old_email_sections:
        email = config[old_section]['username']
        new_section = f"IMAP_{email}"
        
        # Criar nova seção
        if new_section not in config:
            config[new_section] = {}
            
            # Copiar todos os parâmetros
            for key in config[old_section]:
                config[new_section][key] = config[old_section][key]
            
            # Remover seção antiga
            config.remove_section(old_section)
            migrated = True
            logger.info(f"Migrada configuração de email {email} para o novo formato")
    
    # Verificar se já existem as seções IMAP_PRIMARY e IMAP_SECONDARY
    # Se não, criar a partir de emails existentes
    if 'IMAP_PRIMARY' not in config:
        # Procurar o primeiro email disponível para usar como primário
        for section in config.sections():
            if section.startswith('IMAP_') and 'username' in config[section] and section not in ['IMAP_PRIMARY', 'IMAP_SECONDARY']:
                # Criar IMAP_PRIMARY
                config['IMAP_PRIMARY'] = {}
                for key in config[section]:
                    config['IMAP_PRIMARY'][key] = config[section][key]
                
                # Não remove a seção original, apenas copia para IMAP_PRIMARY
                migrated = True
                logger.info(f"Criada seção IMAP_PRIMARY a partir de {section}")
                break
    
    # Se houver migração, salvar as alterações
    if migrated:
        save_config(config)
    
    return migrated

def test_telegram_notifications(config: configparser.ConfigParser):
    """Testa o envio de notificações via Telegram"""
    print("\nTeste de Notificações do Telegram")
    print("-" * 60)
    
    if 'TELEGRAM' not in config or not config['TELEGRAM'].get('token') or not config['TELEGRAM'].get('chat_id'):
        print("❌ Configuração do Telegram incompleta! Verifique as configurações.")
        return False
    
    token = config['TELEGRAM'].get('token')
    chat_id = config['TELEGRAM'].get('chat_id')
    
    print(f"Token: {'••••' + token[-4:] if token else 'não configurado'}")
    print(f"Chat ID: {chat_id}")
    
    # Teste 1: Mensagem simples
    print("\nEnviando mensagem de teste...")
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = (
        "🧪 *Teste do WegNots*\n\n"
        f"Este é um teste de notificação do sistema\\.\n"
        f"⏰ {escape_markdown(current_time)}"
    )
    
    if send_telegram_notification(config, message):
        print("✅ Mensagem de teste enviada com sucesso!")
    else:
        print("❌ Falha ao enviar mensagem de teste!")
        return False
    
    # Teste 2: Notificação de inicialização
    print("\nSimulando notificação de inicialização...")
    if send_system_startup_notification(config):
        print("✅ Notificação de inicialização enviada com sucesso!")
    else:
        print("❌ Falha ao enviar notificação de inicialização!")
        return False
    
    # Teste 3: Notificação de encerramento
    print("\nSimulando notificação de encerramento...")
    if send_system_shutdown_notification(config):
        print("✅ Notificação de encerramento enviada com sucesso!")
    else:
        print("❌ Falha ao enviar notificação de encerramento!")
        return False
    
    print("\n✅ Todos os testes de notificação foram bem-sucedidos!")
    return True

def main():
    """Função principal do gerenciador de configuração"""
    config = load_config()
    
    # Verifica e migra formatos antigos
    migrated = migrate_old_format(config)
    if migrated:
        print("\nAs configurações foram migradas para o novo formato!")
        input("Pressione ENTER para continuar...")
    
    send_system_startup_notification(config)
    
    try:
        while True:
            print("\nGerenciador de Configuração do Monitor")
            print("=" * 60)
            print("1. Listar e-mails monitorados")
            print("2. Adicionar novo e-mail")
            print("3. Remover e-mail")
            print("4. Editar configurações de e-mail")
            print("5. Configurar Telegram")
            print("6. Testar notificações do Telegram")
            print("7. Sair")
            
            try:
                choice = int(input("\nEscolha uma opção: "))
                
                if choice == 1:
                    list_monitored_emails(config)
                elif choice == 2:
                    add_email(config)
                elif choice == 3:
                    remove_email(config)
                elif choice == 4:
                    edit_email(config)
                elif choice == 5:
                    setup_telegram(config)
                elif choice == 6:
                    test_telegram_notifications(config)
                elif choice == 7:
                    print("\nSaindo...")
                    break
                else:
                    print("Opção inválida!")
            except ValueError:
                print("Entrada inválida!")
            except Exception as e:
                logger.error(f"Erro não tratado: {str(e)}")
                print(f"Ocorreu um erro: {str(e)}")
            
            input("\nPressione ENTER para continuar...")
    finally:
        send_system_shutdown_notification(config)

if __name__ == "__main__":
    main()