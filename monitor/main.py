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
import os
from datetime import datetime
from app.core.telegram_client import TelegramClient
from app.core.email_handler import EmailHandler
from config_manager import send_system_startup_notification, send_system_shutdown_notification

# Configura log directory
os.makedirs('logs', exist_ok=True)

# Configura o logger para nível DEBUG para capturar informações mais detalhadas
logging.basicConfig(
    level=logging.DEBUG,  # Alterado de INFO para DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/wegnots.log'),
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
    if 'TELEGRAM' not in config:
        logger.error("Seção TELEGRAM não encontrada em config.ini")
        config['TELEGRAM'] = {'token': '', 'chat_id': ''}
    
    telegram_config = {
        'token': config['TELEGRAM'].get('token', ''),
        'chat_id': config['TELEGRAM'].get('chat_id', '')
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
    
    return imap_configs, telegram_config, config

def main():
    """Função principal do monitor de e-mails"""
    # Carrega toda a configuração uma única vez
    try:
        logger.info("=" * 60)
        logger.info(f"Iniciando WegNots Monitor em {datetime.now()}")
        logger.info("=" * 60)
        
        # Registra handler de sinal para SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Carrega configurações
        imap_configs, telegram_config, config_parser = load_config()
        if not imap_configs:
            logger.error("Nenhuma configuração IMAP válida encontrada em config.ini")
            return 1
        
        # Envia notificação de inicialização através do novo sistema
        # Esta função tentará recuperar automaticamente todas as contas ativas
        startup_success = send_system_startup_notification(config_parser)
        if not startup_success:
            logger.warning("Falha ao enviar notificação de inicialização. Continuando mesmo assim...")
        
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
            # Envia notificação de erro
            telegram_client.send_text_message(
                "🔶 *Aviso: Falha na Conexão IMAP*\n\n"
                f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                "⚠️ Não foi possível conectar aos servidores IMAP.\n"
                "🔍 Verifique suas credenciais e tente novamente."
            )
            return 1
        
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
        
        logger.info("Loop de monitoramento encerrado, realizando limpeza...")
        
        # Encerramento gracioso
        email_handler.shutdown()
        
        # Envia notificação de encerramento através do novo sistema
        shutdown_success = send_system_shutdown_notification(config_parser)
        if not shutdown_success:
            logger.warning("Falha ao enviar notificação de encerramento. Tentando método alternativo...")
            # Método alternativo usando o cliente Telegram direto
            telegram_client.send_text_message(
                "🔴 *WegNots Monitor Encerrado*\n\n"
                f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                "✅ Sistema encerrado com sucesso."
            )
        
        logger.info("Encerramento concluído com sucesso")
        return 0
        
    except Exception as e:
        logger.exception("Erro fatal durante execução")
        # Tenta enviar uma notificação de erro crítico
        try:
            # Carregamos a configuração novamente em caso de erro
            config = configparser.ConfigParser()
            config.read('config.ini')
            send_message = (
                "❌ *ERRO CRÍTICO - WegNots Monitor*\n\n"
                f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"💢 Erro: {str(e)}\n\n"
                "🔄 O sistema será reiniciado automaticamente."
            )
            if 'TELEGRAM' in config and config['TELEGRAM'].get('token') and config['TELEGRAM'].get('chat_id'):
                TelegramClient(
                    token=config['TELEGRAM'].get('token'),
                    chat_id=config['TELEGRAM'].get('chat_id')
                ).send_text_message(send_message)
        except Exception as notification_error:
            logger.error(f"Não foi possível enviar notificação de erro: {notification_error}")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    logger.info(f"Programa encerrado com código de saída: {exit_code}")
    sys.exit(exit_code)
