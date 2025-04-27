#!/usr/bin/env python3
"""
Script de diagnóstico para testar a detecção de emails no WegNots.
Este script verifica se o sistema consegue detectar emails nas contas configuradas.
"""

import configparser
import logging
import sys
from datetime import datetime
from app.core.email_handler import EmailHandler, IMAPConnection

# Configura o logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_diagnosis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('wegnots.diagnosis')

def load_config():
    """Carrega configurações do arquivo config.ini"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Carrega informações globais do Telegram
    telegram_config = {
        'token': config['TELEGRAM']['token'],
        'chat_id': config['TELEGRAM']['chat_id']
    }
    
    # Processa todas as seções de configuração IMAP
    imap_configs = {}
    for section in config.sections():
        if section.startswith('IMAP_'):
            try:
                # Configuração básica do IMAP
                imap_config = {
                    'server': config[section]['server'],
                    'port': config[section]['port'],
                    'username': config[section]['username'],
                    'password': config[section]['password'],
                    'is_active': config[section].get('is_active', 'True')
                }
                
                # Adiciona configuração específica do Telegram se existir
                if 'telegram_chat_id' in config[section]:
                    imap_config['telegram_chat_id'] = config[section]['telegram_chat_id']
                if 'telegram_token' in config[section]:
                    imap_config['telegram_token'] = config[section]['telegram_token']
                    
                # Adiciona à lista de configurações
                imap_configs[section] = imap_config
                logger.info(f"Carregada configuração para {section} ({imap_config['username']})")
            except KeyError as e:
                logger.error(f"Erro ao carregar configuração {section}: {e}")
    
    return imap_configs, telegram_config

def check_email_connection(connection):
    """Testa a conexão com o servidor de email"""
    logger.info(f"Testando conexão com {connection.server} para {connection.username}...")
    
    if connection.connect():
        logger.info(f"✓ Conexão bem-sucedida com {connection.server}")
        
        # Teste diagnóstico para ver se consegue acessar a caixa de entrada
        diagnostics = connection.diagnose_connection()
        
        logger.info(f"Diagnóstico para {connection.username}:")
        logger.info(f"  ✓ Conexão SSL: {diagnostics['ssl_connection']}")
        logger.info(f"  ✓ Autenticação: {diagnostics['authentication']}")
        logger.info(f"  ✓ Acesso à INBOX: {diagnostics['inbox_access']}")
        logger.info(f"  ✓ Listagem de emails: {diagnostics['can_list_emails']}")
        logger.info(f"  ✓ Emails recentes: {diagnostics['recent_emails_count']}")
        
        if diagnostics['latest_email_info']:
            latest = diagnostics['latest_email_info']
            logger.info(f"  ✓ Email mais recente: '{latest['subject']}' de {latest['from']} em {latest['date']}")
        
        # Testa busca de emails não lidos
        try:
            if connection.check_connection():
                status, messages = connection.imap.select('INBOX')
                if status == 'OK':
                    logger.info(f"Inbox contém {messages[0].decode()} mensagens totais")
                    
                    # Testa busca de emails não lidos (UNSEEN)
                    status, messages = connection.imap.search(None, 'UNSEEN')
                    if status == 'OK':
                        unread_count = len(messages[0].split())
                        logger.info(f"  ✓ Emails não lidos: {unread_count}")
                        
                        if unread_count == 0:
                            logger.warning("  ⚠ Não há emails não lidos. O sistema só detecta emails não lidos ou recentes.")
                    else:
                        logger.error(f"  ✗ Erro ao buscar emails não lidos: {status}")
                    
                    # Testa busca de emails recentes (últimas 24h)
                    from datetime import datetime, timedelta
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
                    
                    status, messages = connection.imap.search(None, f'(SINCE "{yesterday}")')
                    if status == 'OK':
                        recent_count = len(messages[0].split())
                        logger.info(f"  ✓ Emails das últimas 24h: {recent_count}")
                        
                        if recent_count == 0:
                            logger.warning("  ⚠ Não há emails das últimas 24h. O sistema não detectará emails antigos.")
                    else:
                        logger.error(f"  ✗ Erro ao buscar emails recentes: {status}")
            
        except Exception as e:
            logger.error(f"  ✗ Erro durante testes adicionais: {e}")
        
        connection.disconnect()
        return True
    else:
        logger.error(f"✗ Falha na conexão com {connection.server}")
        return False

def main():
    """Função principal de diagnóstico"""
    logger.info("=" * 60)
    logger.info(f"Iniciando Diagnóstico de Email WegNots em {datetime.now()}")
    logger.info("=" * 60)
    
    # Carrega configurações
    imap_configs, telegram_config = load_config()
    if not imap_configs:
        logger.error("Nenhuma configuração IMAP válida encontrada em config.ini")
        return 1
    
    # Mostra quais contas serão verificadas
    logger.info(f"Verificando as seguintes contas de email:")
    for section, config in imap_configs.items():
        username = config['username']
        has_custom_telegram = 'telegram_chat_id' in config and 'telegram_token' in config
        logger.info(f"  - {username} (Token Telegram: {'Personalizado' if has_custom_telegram else 'Padrão'})")
    
    # Verifica cada conexão individualmente
    success = False
    
    for section, config in imap_configs.items():
        logger.info(f"\nTestando conexão para {section}...")
        
        connection = IMAPConnection(
            server=config['server'],
            port=int(config['port']),
            username=config['username'],
            password=config['password'],
            is_active=config['is_active'].lower() == 'true',
            telegram_chat_id=config.get('telegram_chat_id'),
            telegram_token=config.get('telegram_token')
        )
        
        if check_email_connection(connection):
            success = True
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("Diagnóstico concluído. Pelo menos uma conexão foi bem-sucedida.")
    else:
        logger.error("Diagnóstico concluído. TODAS as conexões falharam.")
    
    logger.info("Verifique o arquivo email_diagnosis.log para mais detalhes.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()