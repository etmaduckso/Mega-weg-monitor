#!/usr/bin/env python3
"""
WegNots - Sistema de Monitoramento de E-mails com Alertas via Telegram
"""

import time
import logging
import sys
import signal
import threading
import configparser
from datetime import datetime
from app.core.telegram_client import TelegramClient
from app.core.email_handler import EmailHandler

# Configura o logger para nível DEBUG para capturar informações mais detalhadas
logging.basicConfig(
    level=logging.DEBUG,  # Alterado de INFO para DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wegnots.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('wegnots')

# Estado global para controle de execução
running = True

def signal_handler(sig, frame):
    """Manipulador de sinais para encerramento gracioso"""
    global running
    logger.info("Sinal de encerramento recebido. Encerrando monitoramento...")
    running = False

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

def main():
    """Função principal do monitor de e-mails"""
    try:
        logger.info("=" * 60)
        logger.info(f"Iniciando WegNots Monitor em {datetime.now()}")
        logger.info("=" * 60)
        
        # Registra handler de sinal para SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Carrega configurações
        imap_configs, telegram_config = load_config()
        if not imap_configs:
            logger.error("Nenhuma configuração IMAP válida encontrada em config.ini")
            return 1
        
        # Mostra quais contas serão monitoradas
        logger.info(f"Monitorando as seguintes contas de email:")
        for section, config in imap_configs.items():
            username = config['username']
            has_custom_telegram = 'telegram_chat_id' in config and 'telegram_token' in config
            logger.info(f"  - {username} (Token Telegram: {'Personalizado' if has_custom_telegram else 'Padrão'})")
            
        # Inicializa cliente do Telegram com as configurações padrão 
        telegram_client = TelegramClient(
            token=telegram_config['token'],
            chat_id=telegram_config['chat_id']
        )
        
        # Inicializa handler de e-mail e configura todas as conexões
        email_handler = EmailHandler(telegram_client)
        email_handler.setup_connections(imap_configs)
        
        # Tenta conectar aos servidores IMAP
        if not email_handler.connect():
            logger.critical("Falha ao conectar aos servidores IMAP. Verifique as credenciais.")
            return 1
            
        # Envia mensagem de inicialização
        telegram_client.send_text_message(
            "🟢 *WegNots Monitor Iniciado*\n\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"📨 Monitorando {len(imap_configs)} contas de email"
        )
            
        # Loop principal com monitoramento aprimorado
        check_interval = 60  # 1 minuto
        last_check_time = 0
        consecutive_failures = 0
        max_failures = 3
        
        while running:
            current_time = time.time()
            
            if current_time - last_check_time >= check_interval:
                try:
                    logger.info("Verificando novos e-mails...")
                    email_handler.process_emails()
                    consecutive_failures = 0
                except Exception as e:
                    logger.error(f"Erro durante processamento de e-mails: {e}")
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_failures:
                        logger.warning("Realizando novo diagnóstico após falhas consecutivas...")
                        # Reset contador de falhas
                        consecutive_failures = 0
                        
                        # Tenta reconectar automaticamente
                        logger.info("Tentando reconexão aos servidores IMAP...")
                        email_handler.connect()
                
                last_check_time = current_time
            
            time.sleep(1)
            
        # Encerramento gracioso
        email_handler.shutdown()
        telegram_client.send_text_message(
            "🔴 *WegNots Monitor Encerrado*\n\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "Sistema encerrado com sucesso."
        )
        
        return 0
        
    except Exception as e:
        logger.exception("Erro fatal durante execução")
        return 1

if __name__ == "__main__":
    sys.exit(main())
