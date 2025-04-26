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

# Configura o logger
logging.basicConfig(
    level=logging.INFO,
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
    
    primary_config = {
        'server': config['IMAP_PRIMARY']['server'],
        'port': int(config['IMAP_PRIMARY']['port']),
        'username': config['IMAP_PRIMARY']['username'],
        'password': config['IMAP_PRIMARY']['password'],
        'is_active': config['IMAP_PRIMARY'].getboolean('is_active', True)
    }
    
    secondary_config = {
        'server': config['IMAP_SECONDARY']['server'],
        'port': int(config['IMAP_SECONDARY']['port']),
        'username': config['IMAP_SECONDARY']['username'],
        'password': config['IMAP_SECONDARY']['password'],
        'is_active': config['IMAP_SECONDARY'].getboolean('is_active', True)
    }
    
    telegram_config = {
        'token': config['TELEGRAM']['token'],
        'chat_id': config['TELEGRAM']['chat_id']
    }
    
    return primary_config, secondary_config, telegram_config

def diagnose_primary_server(config):
    """Realiza diagnóstico específico do servidor primário"""
    logger.info("Iniciando diagnóstico do servidor primário")
    
    primary_server = {
        'server': config['server'],
        'port': config['port'],
        'username': config['username'],
        'password': config['password'],
        'is_active': config['is_active']
    }
    
    if not all([primary_server['server'], primary_server['username'], primary_server['password']]):
        logger.error("Configurações do servidor primário estão incompletas")
        return
    
    connection = EmailHandler(None)
    connection.setup_connections(primary_server, None)
    diagnosis = connection.diagnose_connections()['primary']
    
    logger.info("=== Resultado do Diagnóstico do Servidor Primário ===")
    logger.info(f"Servidor: {diagnosis['server']}")
    logger.info(f"Conexão SSL: {'OK' if diagnosis['ssl_connection'] else 'Falha'}")
    logger.info(f"Autenticação: {'OK' if diagnosis['authentication'] else 'Falha'}")
    logger.info(f"Acesso INBOX: {'OK' if diagnosis['inbox_access'] else 'Falha'}")
    logger.info(f"Listagem de Emails: {'OK' if diagnosis['can_list_emails'] else 'Falha'}")
    logger.info(f"Qtd Emails Recentes: {diagnosis['recent_emails_count']}")
    
    if diagnosis['error']:
        logger.error(f"Erro encontrado: {diagnosis['error']}")
    
    return diagnosis

def main():
    """Função principal do monitor de e-mails"""
    try:
        logger.info("=" * 60)
        logger.info(f"Iniciando WegNots Monitor em {datetime.now()}")
        logger.info("=" * 60)
        
        # Registra handler de sinal para SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Carrega configurações
        primary_config, secondary_config, telegram_config = load_config()
        
        # Diagnóstico do servidor primário
        diagnose_primary_server(primary_config)
        
        # Inicializa clientes
        telegram_client = TelegramClient(
            token=telegram_config['token'],
            chat_id=telegram_config['chat_id']
        )
        
        # Inicializa handler de e-mail
        email_handler = EmailHandler(telegram_client)
        email_handler.setup_connections(primary_config, secondary_config)
        
        # Realiza diagnóstico detalhado
        logger.info("Realizando diagnóstico dos servidores IMAP...")
        diagnosis = email_handler.diagnose_connections()
        
        if diagnosis['primary']:
            primary_status = diagnosis['primary']
            logger.info(f"Diagnóstico do servidor primário ({primary_status['server']}):")
            logger.info(f"- SSL/TLS: {'✓' if primary_status['ssl_connection'] else '✗'}")
            logger.info(f"- Autenticação: {'✓' if primary_status['authentication'] else '✗'}")
            logger.info(f"- Acesso à Caixa: {'✓' if primary_status['inbox_access'] else '✗'}")
            logger.info(f"- Listagem de Emails: {'✓' if primary_status['can_list_emails'] else '✗'}")
            logger.info(f"- Emails Recentes: {primary_status['recent_emails_count']}")
            if primary_status['error']:
                logger.error(f"- Erro: {primary_status['error']}")
                
            # Envia diagnóstico para o Telegram
            diagnostic_message = (
                "📊 *Diagnóstico do Servidor Primário*\n\n"
                f"🔒 SSL/TLS: {'✓' if primary_status['ssl_connection'] else '✗'}\n"
                f"🔑 Autenticação: {'✓' if primary_status['authentication'] else '✗'}\n"
                f"📫 Acesso à Caixa: {'✓' if primary_status['inbox_access'] else '✗'}\n"
                f"📧 Listagem de Emails: {'✓' if primary_status['can_list_emails'] else '✗'}\n"
                f"📨 Emails Recentes: {primary_status['recent_emails_count']}\n"
            )
            if primary_status['error']:
                diagnostic_message += f"❌ Erro: {primary_status['error']}\n"
            telegram_client.send_text_message(diagnostic_message)
        
        # Tenta conectar aos servidores IMAP
        if not email_handler.connect():
            logger.critical("Falha ao conectar aos servidores IMAP. Verifique as credenciais.")
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
                        diagnosis = email_handler.diagnose_connections()
                        if diagnosis['primary'] and diagnosis['primary']['error']:
                            logger.error(f"Diagnóstico detectou erro: {diagnosis['primary']['error']}")
                            telegram_client.send_text_message(
                                "⚠️ *Alerta de Monitoramento*\n\n"
                                f"Servidor: {primary_config['server']}\n"
                                f"Erro: {diagnosis['primary']['error']}\n"
                                "Tentando reconexão..."
                            )
                            email_handler.connect()
                        consecutive_failures = 0
                
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
