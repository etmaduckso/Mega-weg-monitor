#!/usr/bin/env python3
"""
Módulo para gerenciar os comandos do bot Telegram do WegNots
"""

import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('wegnots.telegram.commands')

class TelegramCommands:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def set_bot_commands(self) -> bool:
        """Configura os comandos disponíveis no bot"""
        url = f"{self.base_url}/setMyCommands"
        commands = [
            {"command": "start", "description": "Iniciar o monitoramento de e-mails"},
            {"command": "status", "description": "Verificar status do sistema"},
            {"command": "help", "description": "Exibir ajuda"}
        ]
        
        try:
            response = requests.post(url, json={"commands": commands})
            if response.status_code == 200:
                logger.info("Comandos do bot configurados com sucesso")
                return True
            else:
                logger.error(f"Erro ao configurar comandos do bot: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao configurar comandos do bot: {e}")
            return False
    
    def set_webhook(self, webhook_url: str) -> bool:
        """Configura um webhook para o bot"""
        url = f"{self.base_url}/setWebhook"
        try:
            response = requests.post(url, json={"url": webhook_url})
            if response.status_code == 200:
                logger.info(f"Webhook configurado com sucesso: {webhook_url}")
                return True
            else:
                logger.error(f"Erro ao configurar webhook: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao configurar webhook: {e}")
            return False
    
    def handle_start_command(self, chat_id: str) -> bool:
        """Lida com o comando /start enviando uma mensagem amigável em português"""
        url = f"{self.base_url}/sendMessage"
        
        # Mensagem de boas-vindas em português, simples e direta
        message = (
            "🔔 *Bem-vindo ao WegNots!*\n\n"
            "✅ Seu cadastro foi ativado com sucesso!\n\n"
            "Agora você receberá notificações de e-mails importantes diretamente aqui no Telegram.\n\n"
            "Não é necessário fazer mais nada. O sistema está funcionando automaticamente."
        )
        
        try:
            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            })
            
            if response.status_code == 200:
                logger.info(f"Mensagem de boas-vindas enviada com sucesso para chat_id {chat_id}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem de boas-vindas: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem de boas-vindas: {e}")
            return False
    
    def handle_status_command(self, chat_id: str, status_info: Dict[str, Any]) -> bool:
        """Lida com o comando /status enviando informações sobre o status do sistema"""
        url = f"{self.base_url}/sendMessage"
        
        message = (
            "📊 *Status do Sistema*\n\n"
            f"🖥️ Servidores ativos: {status_info.get('active_servers', 0)}\n"
            f"📧 E-mails monitorados hoje: {status_info.get('emails_today', 0)}\n"
            f"🔔 Notificações enviadas: {status_info.get('notifications_sent', 0)}\n"
            f"⏰ Em execução há: {status_info.get('uptime', '0')} minutos\n\n"
            "✅ Sistema operando normalmente"
        )
        
        try:
            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })
            
            if response.status_code == 200:
                logger.info(f"Mensagem de status enviada com sucesso para chat_id {chat_id}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem de status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem de status: {e}")
            return False
    
    def handle_help_command(self, chat_id: str) -> bool:
        """Lida com o comando /help enviando informações de ajuda"""
        url = f"{self.base_url}/sendMessage"
        
        message = (
            "ℹ️ *Ajuda do WegNots*\n\n"
            "Este bot notifica você sobre e-mails recebidos nas contas configuradas.\n\n"
            "*Comandos disponíveis:*\n"
            "/start - Iniciar o monitoramento\n"
            "/status - Verificar o status do sistema\n"
            "/help - Exibir esta mensagem de ajuda\n\n"
            "✉️ Para suporte adicional, contate o administrador do sistema."
        )
        
        try:
            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })
            
            if response.status_code == 200:
                logger.info(f"Mensagem de ajuda enviada com sucesso para chat_id {chat_id}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem de ajuda: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem de ajuda: {e}")
            return False
    
    def process_update(self, update: Dict[str, Any]) -> Optional[bool]:
        """Processa uma atualização recebida do Telegram"""
        if 'message' not in update:
            return None
            
        message = update['message']
        if 'text' not in message:
            return None
            
        text = message['text']
        chat_id = str(message['chat']['id'])
        
        # Processa comandos
        if text == '/start':
            return self.handle_start_command(chat_id)
        elif text == '/status':
            # Informações de status simuladas - em uma implementação real, estas informações viriam do sistema
            status_info = {
                'active_servers': 2,
                'emails_today': 24,
                'notifications_sent': 18,
                'uptime': '480'
            }
            return self.handle_status_command(chat_id, status_info)
        elif text == '/help':
            return self.handle_help_command(chat_id)
            
        return None