#!/usr/bin/env python3
"""
WegNots - Sistema de Monitoramento de E-mails com Alertas Multicanal
"""

import time
import logging
import sys
import signal
from datetime import datetime
from pymongo import MongoClient, errors
from app.core.email_handler import EmailHandler
from app.core.telegram_client import TelegramClient
from app.core.user_model import UserModel
from app.config.settings import (
    IMAP_CONFIG, 
    TELEGRAM_CONFIG,
    setup_logging, 
    validate_config
)

# Configura o logger principal
logger = setup_logging()

# Estado global para controle de execução
running = True

def signal_handler(sig, frame):
    """Manipulador de sinais para encerramento gracioso."""
    global running
    logger.info("Sinal de encerramento recebido. Encerrando monitoramento...")
    running = False

def setup_mongodb():
    """
    Inicializa a conexão com o MongoDB.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        # Testa a conexão
        client.server_info()
        db = client["wegnots"]
        logger.info("Conexão com MongoDB estabelecida com sucesso")
        return db
    except errors.ServerSelectionTimeoutError:
        logger.error("Não foi possível conectar ao MongoDB. Verifique se o servidor está rodando.")
        return None
    except Exception as e:
        logger.error(f"Erro ao conectar ao MongoDB: {e}")
        return None

def setup_notification_clients():
    """
    Configura e inicializa os clientes de notificação.
    """
    clients = []
    
    try:
        # Inicializa MongoDB e UserModel
        db = setup_mongodb()
        if db is None:  # Corrigido: usar 'is None' ao invés de verificação booleana
            raise Exception("Falha ao inicializar MongoDB")
            
        user_model = UserModel(db)
        logger.info("UserModel inicializado com sucesso")
        
        # Configura cliente Telegram
        telegram_client = TelegramClient(user_model)
        clients.append(telegram_client)
        logger.info("Cliente Telegram inicializado com sucesso")
        
        # Envia mensagem de inicialização
        startup_message = (
            "🟢 *WegNots Monitor Iniciado*\n\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "📧 IMAP: Conectando...\n"
            "✅ Sistema ativo e monitorando"
        )
        telegram_client.send_text_message(startup_message)
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {e}")
    
    return clients

def process_email(email_handler, notification_clients, email_id):
    """
    Processa um único e-mail e envia alerta se necessário.
    """
    try:
        # Obtém o e-mail completo
        msg = email_handler.parse_email(email_id)
        if not msg:
            logger.warning(f"Não foi possível obter o e-mail {email_id}")
            return False
            
        # Extrai dados do e-mail
        email_data = email_handler.extract_email_data(msg)
        if not email_data:
            logger.warning(f"Falha ao extrair dados do e-mail {email_id}")
            return False
            
        # Processa dados e determina tipo de alerta
        logger.info(f"Processando e-mail: {email_data['subject']}")
        
        # Determina o tipo de alerta com base no assunto
        subject = email_data['subject'].lower()
        alert_type = 3  # Alerta leve por padrão
        
        if "urgente" in subject or "crítico" in subject or "emergência" in subject:
            alert_type = 1  # Alerta crítico
        elif "importante" in subject or "atenção" in subject:
            alert_type = 2  # Alerta moderado
            
        # Envia alertas para todos os clientes configurados
        success = True
        for client in notification_clients:
            try:
                result = client.send_alert(
                    equipment_id="WEG-MONITOR-001",
                    alert_type=alert_type,
                    user="Sistema WegNots",
                    extra_info=email_data
                )
                if result:
                    logger.info(f"Alerta enviado com sucesso via {client.__class__.__name__}")
                else:
                    logger.warning(f"Falha ao enviar alerta via {client.__class__.__name__}")
                    success = False
            except Exception as e:
                logger.error(f"Erro ao enviar alerta via {client.__class__.__name__}: {e}")
                success = False
                
        return success
        
    except Exception as e:
        logger.error(f"Erro ao processar e-mail {email_id}: {e}", exc_info=True)
        return False

def main():
    """
    Função principal do monitor de e-mails.
    """
    logger.info("=" * 60)
    logger.info(f"Iniciando WegNots Monitor v1.1.0 em {datetime.now()}")
    logger.info("=" * 60)
    
    # Registra handler de sinal para SIGINT (Ctrl+C) e SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Valida configurações
    if not validate_config():
        logger.critical("Configurações inválidas. Encerrando aplicação.")
        return 1
        
    # Inicia serviços
    email_handler = None
    notification_clients = []
    
    try:
        # Inicializa os clientes de notificação
        notification_clients = setup_notification_clients()
        
        # Inicializa o manipulador de e-mails com os clientes de notificação
        email_handler = EmailHandler(notification_clients=notification_clients)
        
        # Tenta conectar ao servidor IMAP
        if not email_handler.connect():
            logger.critical("Falha na conexão inicial com servidor de e-mail. Verifique as credenciais.")
            return 1
            
        logger.info("Conexões estabelecidas. Monitoramento ativo.")
        
        # Define o intervalo de verificação a partir da configuração
        check_interval = IMAP_CONFIG['check_interval']
        
        # Loop principal de monitoramento
        last_check_time = 0
        
        while running:
            current_time = time.time()
            
            # Verifica se já passou o intervalo de verificação
            if current_time - last_check_time >= check_interval:
                try:
                    # Verifica novos e-mails
                    new_emails = email_handler.check_new_emails()
                    
                    if new_emails:
                        logger.info(f"Novos e-mails detectados: {len(new_emails)}")
                        for email_id in new_emails:
                            process_email(email_handler, notification_clients, email_id)
                            
                except Exception as e:
                    logger.error(f"Erro durante monitoramento: {e}", exc_info=True)
                
                last_check_time = current_time
                
            # Espera um tempo curto antes de verificar novamente
            time.sleep(1)
                
    except Exception as e:
        logger.critical(f"Erro fatal no sistema: {e}", exc_info=True)
        return 1
        
    finally:
        # Encerramento gracioso
        logger.info("Encerrando serviços...")
        
        if email_handler:
            try:
                email_handler.close()
                logger.info("Conexão IMAP encerrada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao encerrar conexão IMAP: {e}")
                
        if notification_clients:
            for client in notification_clients:
                if hasattr(client, 'send_shutdown_message'):
                    try:
                        client.send_shutdown_message()
                    except Exception as e:
                        logger.error(f"Erro ao enviar mensagem de encerramento via {client.__class__.__name__}: {e}")
                
    logger.info("Sistema encerrado com sucesso")
    return 0

if __name__ == "__main__":
    sys.exit(main())
