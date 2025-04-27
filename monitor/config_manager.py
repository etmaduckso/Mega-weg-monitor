#!/usr/bin/env python3
import os
import json
import imaplib
import configparser
import re
import logging
from typing import Dict, Optional, List, Tuple

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
    
    email = input("\nE-mail: ").strip()
    if not email or not is_valid_email(email):
        print("E-mail inválido! Forneça um endereço de e-mail válido.")
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
    
    # Determinar qual seção usar
    section_count = sum(1 for s in config.sections() if s.startswith('IMAP_'))
    
    if section_count == 0:
        # Primeira conta = IMAP_PRIMARY
        section = "IMAP_PRIMARY"
    elif section_count == 1 and "IMAP_PRIMARY" in config and "IMAP_SECONDARY" not in config:
        # Segunda conta = IMAP_SECONDARY
        section = "IMAP_SECONDARY"
    else:
        # Demais contas usam formato IMAP_email
        section = f"IMAP_{email}"
    
    if section in config:
        print(f"Uma conta já está configurada como {section}!")
        if input("Deseja sobrescrever? (s/n): ").lower() != 's':
            return
    
    password = input("\nSenha ou Senha de App: ").strip()
    if not password:
        print("Senha inválida!")
        return
    
    is_active = input("Ativar monitoramento para esta conta? (s/n): ").lower() == 's'
    
    # Solicitar chat_id do Telegram específico para esta conta
    print("\nConfiguração de notificação")
    print("-" * 40)
    
    # Verificar se existe configuração global do Telegram
    if 'TELEGRAM' in config and 'chat_id' in config['TELEGRAM']:
        global_chat_id = config['TELEGRAM']['chat_id']
        global_token = config['TELEGRAM'].get('token', '')
        
        print(f"Chat ID global atual: {global_chat_id}")
        print(f"Token global atual: {'••••' + global_token[-4:] if global_token else 'não configurado'}")
        
        use_global_settings = input("Usar as configurações globais do Telegram para esta conta? (s/n): ").lower() == 's'
        
        if use_global_settings:
            chat_id = global_chat_id
            token = global_token
        else:
            chat_id = input("Digite o Chat ID específico para este e-mail: ").strip()
            if not chat_id or not is_valid_chat_id(chat_id):
                print("Chat ID inválido! Deve ser um número inteiro.")
                return
            
            # Perguntar se deseja usar um token diferente para este email específico
            use_custom_token = input("Deseja usar um token de bot diferente para este e-mail? (s/n): ").lower() == 's'
            if use_custom_token:
                token = input("Digite o token do bot para este e-mail: ").strip()
                if not token:
                    print("Token inválido!")
                    return
            else:
                token = global_token
    else:
        chat_id = input("Digite o Chat ID do Telegram para este e-mail: ").strip()
        if not chat_id or not is_valid_chat_id(chat_id):
            print("Chat ID inválido! Deve ser um número inteiro.")
            return
        
        token = input("Digite o token do bot Telegram: ").strip()
        if not token:
            print("Token inválido!")
            return
    
    # Testa a conexão antes de salvar
    print("\nTestando conexão...")
    success, error_message = test_email_connection(
        server_config['server'],
        server_config['port'],
        email,
        password
    )
    
    if success:
        email_config = {
            'server': server_config['server'],
            'port': str(server_config['port']),
            'username': email,
            'password': password,
            'is_active': str(is_active),
            'telegram_chat_id': chat_id  # Adicionando chat_id específico
        }
        
        # Se um token personalizado foi definido, adicione-o à configuração
        if token != global_token or 'TELEGRAM' not in config:
            email_config['telegram_token'] = token
        
        config[section] = email_config
        
        # Se for uma das contas principais e não existir configuração do Telegram, criar
        if 'TELEGRAM' not in config:
            config['TELEGRAM'] = {
                'token': token,
                'chat_id': chat_id
            }
        
        # Verificar se há token do Telegram global configurado
        elif 'token' not in config['TELEGRAM'] or not config['TELEGRAM']['token']:
            config['TELEGRAM']['token'] = token
        
        # Garantir que exista um chat_id global como fallback
        if 'chat_id' not in config['TELEGRAM'] or not config['TELEGRAM']['chat_id']:
            # Usar o chat_id desta conta como global se não existir um global
            config['TELEGRAM']['chat_id'] = chat_id
        
        save_config(config)
        update_env_file(config)
        
        # Exibir resumo da configuração
        print(f"\n✅ E-mail adicionado com sucesso como {section}!")
        if 'telegram_token' in email_config:
            print(f"✅ Este e-mail usará um token personalizado: ••••{token[-4:]}")
            print(f"✅ Alertas serão enviados para o chat ID específico: {chat_id}")
        else:
            print(f"✅ Este e-mail usará o token global: ••••{global_token[-4:]}")
            print(f"✅ Alertas serão enviados para o chat ID: {chat_id}")
    else:
        print(f"❌ Falha ao adicionar e-mail: {error_message}")
        print("Verifique as credenciais e tente novamente.")

def remove_email(config: configparser.ConfigParser):
    """Remove um e-mail do monitoramento"""
    print("\nRemover e-mail do monitoramento")
    print("-" * 60)
    
    # Lista e-mails disponíveis
    emails = []
    sections = []
    
    for section in config.sections():
        if section.startswith('IMAP_'):
            if 'username' in config[section]:
                email = config[section]['username']
                emails.append(email)
                sections.append(section)
            elif section not in ['IMAP_PRIMARY', 'IMAP_SECONDARY']:
                email = section.replace('IMAP_', '')
                emails.append(email)
                sections.append(section)
    
    if not emails:
        print("Nenhum e-mail configurado!")
        return
    
    print("E-mails disponíveis:")
    for i, (email, section) in enumerate(zip(emails, sections), 1):
        server = config[section]['server']
        print(f"{i}. {email} ({section} - {server})")
    
    try:
        choice = int(input("\nEscolha o número do e-mail para remover (0 para cancelar): "))
        if choice == 0:
            return
        
        if 1 <= choice <= len(emails):
            section = sections[choice - 1]
            email = emails[choice - 1]
            
            print(f"\nVocê escolheu remover: {email} ({section})")
            confirm = input("Tem certeza? (s/n): ").lower()
            
            if confirm == 's':
                config.remove_section(section)
                save_config(config)
                update_env_file(config)
                print(f"✅ E-mail {email} removido com sucesso!")
            else:
                print("Operação cancelada.")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Entrada inválida!")

def edit_email(config: configparser.ConfigParser):
    """Edita as configurações de um e-mail monitorado"""
    print("\nEditar configurações de e-mail")
    print("-" * 60)
    
    # Lista e-mails disponíveis
    emails = []
    sections = []
    
    for section in config.sections():
        if section.startswith('IMAP_'):
            if 'username' in config[section]:
                email = config[section]['username']
                emails.append(email)
                sections.append(section)
            elif section not in ['IMAP_PRIMARY', 'IMAP_SECONDARY']:
                email = section.replace('IMAP_', '')
                emails.append(email)
                sections.append(section)
    
    if not emails:
        print("Nenhum e-mail configurado para editar!")
        return
    
    print("E-mails disponíveis:")
    for i, (email, section) in enumerate(zip(emails, sections), 1):
        server = config[section]['server']
        print(f"{i}. {email} ({section} - {server})")
    
    try:
        choice = int(input("\nEscolha o número do e-mail para editar (0 para cancelar): "))
        if choice == 0:
            return
        
        if 1 <= choice <= len(emails):
            section = sections[choice - 1]
            email = emails[choice - 1]
            
            print(f"\nEditando: {email} ({section})")
            print("Deixe em branco para manter o valor atual.")
            
            # Mostra valores atuais
            print("\nValores atuais:")
            for key, value in config[section].items():
                if key == 'password':
                    print(f"  {key}: {'*' * len(value)}")
                elif key == 'telegram_token' and value:
                    print(f"  {key}: ••••{value[-4:]}")
                else:
                    print(f"  {key}: {value}")
            
            # Atualiza senha, se necessário
            new_password = input("\nNova senha (deixe em branco para manter): ").strip()
            if new_password:
                config[section]['password'] = new_password
            
            # Atualiza status ativo
            current_active = config[section].getboolean('is_active', True)
            active_input = input(f"Ativo? (s/n) [{current_active and 's' or 'n'}]: ").strip().lower()
            if active_input:
                config[section]['is_active'] = str(active_input == 's')
            
            # Atualiza chat_id específico
            current_chat_id = config[section].get('telegram_chat_id', '')
            new_chat_id = input(f"Chat ID específico [{current_chat_id}]: ").strip()
            if new_chat_id:
                if is_valid_chat_id(new_chat_id):
                    config[section]['telegram_chat_id'] = new_chat_id
                else:
                    print("Chat ID inválido! Deve ser um número inteiro.")
                    return
            
            # Obtém o token global para comparação
            global_token = config['TELEGRAM'].get('token', '') if 'TELEGRAM' in config else ''
            
            # Atualiza token específico
            if 'telegram_token' in config[section]:
                current_token = config[section]['telegram_token']
                masked_token = "••••" + current_token[-4:] if current_token else "não configurado"
                print(f"\nAtualmente usando token personalizado: {masked_token}")
                
                if input("Deseja continuar usando um token personalizado? (s/n): ").lower() == 's':
                    new_token = input(f"Novo token específico (deixe em branco para manter): ").strip()
                    if new_token:
                        config[section]['telegram_token'] = new_token
                else:
                    # Se o usuário não quer mais um token personalizado, remova-o
                    if 'telegram_token' in config[section]:
                        del config[section]['telegram_token']
                    print(f"✓ Agora usando o token global: ••••{global_token[-4:] if global_token else ''}")
            else:
                # Não tem token específico atualmente
                if global_token:
                    masked_global = "••••" + global_token[-4:] if global_token else "não configurado"
                    print(f"\nAtualmente usando token global: {masked_global}")
                    
                    if input("Deseja configurar um token personalizado para este e-mail? (s/n): ").lower() == 's':
                        new_token = input("Token personalizado: ").strip()
                        if new_token:
                            config[section]['telegram_token'] = new_token
                else:
                    # Não há token global, precisamos de um token
                    new_token = input("\nToken do Telegram (obrigatório): ").strip()
                    if new_token:
                        config[section]['telegram_token'] = new_token
                    else:
                        print("Token do Telegram é obrigatório quando não há token global!")
                        return
            
            # Se for uma conta principal, permite editar config do Telegram global
            if section in ["IMAP_PRIMARY", "IMAP_SECONDARY"] and 'TELEGRAM' in config:
                print("\nConfiguração global do Telegram:")
                
                # Token global
                current_global_token = config['TELEGRAM'].get('token', '')
                masked_token = "••••" + current_global_token[-4:] if current_global_token else "não configurado"
                print(f"Token global atual: {masked_token}")
                new_global_token = input(f"Novo token global (deixe em branco para manter): ").strip()
                if new_global_token:
                    if input("\n⚠️ ATENÇÃO: Alterar o token global afetará todos os e-mails que não possuem token específico. Continuar? (s/n): ").lower() == 's':
                        config['TELEGRAM']['token'] = new_global_token
                    else:
                        print("Alteração do token global cancelada.")
                
                # Chat ID global
                current_global_chat_id = config['TELEGRAM'].get('chat_id', '')
                new_global_chat_id = input(f"Chat ID global [{current_global_chat_id}]: ").strip()
                if new_global_chat_id:
                    if is_valid_chat_id(new_global_chat_id):
                        config['TELEGRAM']['chat_id'] = new_global_chat_id
                    else:
                        print("Chat ID inválido! Deve ser um número inteiro.")
                        return
            
            # Testa a conexão se a senha foi alterada
            if new_password:
                print("\nTestando nova conexão...")
                success, error_message = test_email_connection(
                    config[section]['server'],
                    int(config[section]['port']),
                    config[section]['username'],
                    new_password
                )
                
                if not success:
                    print(f"❌ Aviso: {error_message}")
                    if input("Deseja salvar mesmo assim? (s/n): ").lower() != 's':
                        print("Operação cancelada.")
                        return
            
            save_config(config)
            update_env_file(config)
            
            # Exibe resumo das alterações
            print("\n✅ Configurações atualizadas com sucesso!")
            if 'telegram_token' in config[section]:
                token_value = config[section]['telegram_token']
                print(f"✅ Este e-mail usa token personalizado: ••••{token_value[-4:]}")
            else:
                global_token = config['TELEGRAM'].get('token', '') if 'TELEGRAM' in config else ''
                if global_token:
                    print(f"✅ Este e-mail usa o token global: ••••{global_token[-4:]}")
                else:
                    print("⚠️ Nenhum token configurado! Isso pode causar problemas nas notificações.")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Entrada inválida!")

def setup_telegram(config: configparser.ConfigParser):
    """Configura ou atualiza as configurações do Telegram"""
    print("\nConfiguração do Telegram")
    print("-" * 60)
    
    if 'TELEGRAM' not in config:
        config['TELEGRAM'] = {}
    
    # Configuração atual
    current_token = config['TELEGRAM'].get('token', '')
    masked_token = "••••" + current_token[-4:] if current_token else "não configurado"
    
    current_chat_id = config['TELEGRAM'].get('chat_id', '')
    
    print(f"Token atual: {masked_token}")
    print(f"Chat ID global atual: {current_chat_id}")
    
    # Nova configuração
    print("\nPara manter o valor atual, deixe em branco.")
    
    new_token = input("Novo token do bot Telegram: ").strip()
    if new_token:
        config['TELEGRAM']['token'] = new_token
    
    new_chat_id = input("Novo Chat ID global: ").strip()
    if new_chat_id:
        if is_valid_chat_id(new_chat_id):
            config['TELEGRAM']['chat_id'] = new_chat_id
        else:
            print("Chat ID inválido! Deve ser um número inteiro.")
            return
    
    save_config(config)
    update_env_file(config)
    print("✅ Configuração do Telegram atualizada com sucesso!")

def migrate_old_format(config: configparser.ConfigParser):
    """Migra formatos antigos de configuração para o novo formato IMAP_*"""
    changed = False
    
    # Migra formato EMAIL_* para IMAP_*
    email_sections = [s for s in config.sections() if s.startswith('EMAIL_')]
    for old_section in email_sections:
        email = old_section.replace('EMAIL_', '')
        
        # Determina nova seção
        if len(email_sections) == 1 and "IMAP_PRIMARY" not in config:
            # Se só tem um email, torna-se o primário
            new_section = "IMAP_PRIMARY"
        elif len(email_sections) > 1 and old_section == email_sections[1] and "IMAP_SECONDARY" not in config:
            # Segundo email torna-se o secundário
            new_section = "IMAP_SECONDARY"
        else:
            # Outros emails mantêm o formato, mas com prefixo IMAP_
            new_section = f"IMAP_{email}"
        
        # Cria nova seção
        config[new_section] = {
            'server': config[old_section]['server'],
            'port': config[old_section]['port'],
            'username': email,
            'password': config[old_section]['password'],
            'is_active': 'true'
        }
        
        # Remove seção antiga
        config.remove_section(old_section)
        changed = True
        
        print(f"Migrado: {old_section} -> {new_section}")
    
    if changed:
        save_config(config)
        update_env_file(config)
        print("✅ Migração de formato concluída com sucesso!")
    
    return changed

def main():
    """Função principal do gerenciador de configuração"""
    config = load_config()
    
    # Verifica e migra formatos antigos
    migrated = migrate_old_format(config)
    if migrated:
        print("\nAs configurações foram migradas para o novo formato!")
        input("Pressione ENTER para continuar...")
    
    while True:
        print("\nGerenciador de Configuração do Monitor")
        print("=" * 60)
        print("1. Listar e-mails monitorados")
        print("2. Adicionar novo e-mail")
        print("3. Remover e-mail")
        print("4. Editar configurações de e-mail")
        print("5. Configurar Telegram")
        print("6. Sair")
        
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

if __name__ == "__main__":
    main()