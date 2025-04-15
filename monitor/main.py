#!/usr/bin/env python3
"""
WegNots - Sistema de Monitoramento de E-mails com Alertas Multicanal

Este módulo orquestra o fluxo principal da aplicação, conectando-se a um servidor
de e-mail via IMAP, verificando novas mensagens e enviando alertas via Telegram
e/ou Rocket.Chat conforme configurado.

Implementa estratégias de reconexão automática, tratamento robusto de erros e 
logging detalhado para garantir a confiabilidade do serviço.
"""

import time
import logging
import sys
import signal
import importlib
from datetime import datetime

from app.core.email_handler import EmailHandler
from app.core.telegram_client import TelegramClient
from app.config.settings import (
    IMAP_CONFIG, 
    TELEGRAM_CONFIG, 
    ROCKETCHAT_CONFIG,
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

def process_email(email_handler, notification_clients, email_id):
    """
    Processa um único e-mail e envia alerta se necessário.
    
    Args:
        email_handler: Instância de EmailHandler
        notification_clients: Lista de clientes de notificação (Telegram, Rocket.Chat)
        email_id: ID do e-mail a ser processado
        
    Returns:
        bool: True se processado com sucesso, False caso contrário
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
        
        # Exemplo de lógica para determinar tipo de alerta com base no assunto
        subject = email_data['subject'].lower()
        alert_type = 3  # Alerta leve por padrão
        
        if "urgente" in subject or "crítico" in subject or "emergência" in subject:
            alert_type = 1  # Alerta crítico
        elif "importante" in subject or "atenção" in subject:
            alert_type = 2  # Alerta moderado
            
        # Prepara detalhes extras
        extra_info = {
            'subject': email_data['subject'],
            'from': email_data['from'],
            'date': email_data['date']
        }
        
        # Envia alertas para todos os clientes configurados
        success = True
        for client in notification_clients:
            try:
                # Prioriza envio via Telegram com retry
                if client.__class__.__name__ == "TelegramClient":
                    for attempt in range(IMAP_CONFIG.get('retry_attempts', 3)):
                        try:
                            result = client.send_alert(
                                equipment_id="WEG-MONITOR-001",
                                alert_type=alert_type,
                                user="Sistema WegNots",
                                extra_info=extra_info
                            )
                            if result:
                                logger.info(f"Alerta enviado com sucesso para e-mail {email_id} via Telegram na tentativa {attempt+1}")
                                break
                            else:
                                logger.warning(f"Falha ao enviar alerta para e-mail {email_id} via Telegram na tentativa {attempt+1}")
                        except Exception as e:
                            logger.error(f"Erro ao enviar alerta via Telegram para e-mail {email_id}: {e}")
                        time.sleep(IMAP_CONFIG.get('retry_delay', 5))
                else:
                    result = client.send_alert(
                        equipment_id="WEG-MONITOR-001",
                        alert_type=alert_type,
                        user="Sistema WegNots",
                        extra_info=extra_info
                    )
                    if result:
                        logger.info(f"Alerta enviado com sucesso para e-mail {email_id} via {client.__class__.__name__}")
                    else:
                        logger.warning(f"Falha ao enviar alerta para e-mail {email_id} via {client.__class__.__name__}")
                        success = False
            except Exception as e:
                logger.error(f"Erro ao enviar alerta via {client.__class__.__name__}: {e}")
                success = False
                
        return success
        
    except Exception as e:
        logger.error(f"Erro ao processar e-mail {email_id}: {e}", exc_info=True)
        return False

def setup_notification_clients():
    """
    Configura clientes de notificação com base nas configurações disponíveis.
    
    Returns:
        list: Lista de clientes de notificação inicializados
    """
    clients = []
    
    # Configura cliente Telegram se habilitado
    if TELEGRAM_CONFIG.get('bot_token') and TELEGRAM_CONFIG.get('chat_id'):
        try:
            telegram_client = TelegramClient()
            clients.append(telegram_client)
            logger.info("Cliente Telegram inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Telegram: {e}")
    
    if not clients:
        logger.warning("Nenhum cliente de notificação configurado! Sistema funcionará sem envio de alertas.")
        
    return clients

def send_system_notification(clients, message):
    """
    Envia uma notificação do sistema para todos os clientes configurados.
    
    Args:
        clients (list): Lista de clientes de notificação
        message (str): Mensagem a ser enviada
        
    Returns:
        bool: True se pelo menos um cliente enviou com sucesso
    """
    if not clients:
        return False
        
    success = False
    for client in clients:
        try:
            result = client.send_text_message(message)
            if result:
                success = True
                logger.debug(f"Notificação enviada via {client.__class__.__name__}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação via {client.__class__.__name__}: {e}")
            
    return success

def main():
    """
    Função principal do monitor de e-mails.
    
    Gerencia o ciclo de vida da aplicação, incluindo:
    - Validação de configurações
    - Conexão com serviços
    - Loop principal de monitoramento
    - Tratamento de erros e reconexões
    - Encerramento gracioso
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
        
        # Notifica início do sistema
        send_system_notification(notification_clients, 
                                "🚀 *Sistema WegNots iniciado*\nMonitoramento de e-mails ativo.")
        
        # Inicializa o manipulador de e-mails com os clientes de notificação
        email_handler = EmailHandler(notification_clients=notification_clients)
        
        # Tenta conectar ao servidor IMAP
        if not email_handler.connect():
            logger.critical("Falha na conexão inicial com servidor de e-mail. Verifique as credenciais.")
            send_system_notification(notification_clients, 
                                   "⚠️ *FALHA* ao conectar com servidor de e-mails")
            return 1
            
        logger.info("Conexões estabelecidas. Monitoramento ativo.")
        
        # Define o intervalo de verificação a partir da configuração
        check_interval = IMAP_CONFIG['check_interval']
        reconnect_delay = IMAP_CONFIG['reconnect_delay']
        
        # Loop principal de monitoramento
        last_check_time = 0
        consecutive_failures = 0
        
        while running:
            current_time = time.time()
            
            # Verifica se já passou o intervalo de verificação
            if current_time - last_check_time >= check_interval:
                try:
                    # Verifica novos e-mails
                    new_emails = email_handler.check_new_emails()
                    
                    # Processa novos e-mails
                    if new_emails:
                        logger.info(f"Novos e-mails detectados: {len(new_emails)}")
                        for email_id in new_emails:
                            process_email(email_handler, notification_clients, email_id)
                            
                    consecutive_failures = 0  # Reset contador de falhas
                    
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"Erro durante monitoramento: {e}", exc_info=True)
                    
                    # Notifica falhas consecutivas
                    if consecutive_failures >= 3:
                        error_msg = f"⚠️ *ATENÇÃO*: {consecutive_failures} falhas consecutivas no monitoramento"
                        send_system_notification(notification_clients, error_msg)
                
                last_check_time = current_time
                
            # Espera um tempo curto antes de verificar novamente
            # Evita uso intensivo de CPU no loop
            time.sleep(1)
                
    except Exception as e:
        logger.critical(f"Erro fatal no sistema: {e}", exc_info=True)
        if notification_clients:
            send_system_notification(notification_clients, 
                                  f"🔥 *ERRO CRÍTICO*: Sistema interrompido\n```{str(e)}```")
        return 1
        
    finally:
        # Encerramento gracioso
        logger.info("Encerrando serviços...")
        
        if email_handler:
            try:
                email_handler.close_connection()
                logger.info("Conexão IMAP encerrada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao encerrar conexão IMAP: {e}")
                
        if notification_clients:
            try:
                send_system_notification(notification_clients, 
                                      "🛑 *Sistema WegNots encerrado*")
                logger.info("Notificações de encerramento enviadas")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagens de encerramento: {e}")
                
    logger.info("Sistema encerrado com sucesso")
    return 0

if __name__ == "__main__":
    sys.exit(main())
