#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente para integração com o RocketChat.
Este módulo fornece funcionalidades para enviar mensagens para o RocketChat,
tanto via API REST quanto via webhooks.
"""

import os
import json
import logging
import requests
import time
from typing import Dict, Any, Optional, Union

# Tenta importar as configurações do arquivo config.py
try:
    from config import ROCKETCHAT_CONFIG
except ImportError:
    # Se não encontrar, usa um dicionário vazio
    ROCKETCHAT_CONFIG = {}

class RocketChatClient:
    """Cliente para envio de mensagens para o RocketChat."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o cliente RocketChat.
        
        Args:
            config: Configuração opcional. Se não fornecida, tentará carregar do config.py
                   ou variáveis de ambiente.
        """
        self.logger = logging.getLogger("rocketchat_client")
        
        # Carrega configuração
        self.config = config or self._load_config()
        
        # Inicializa atributos
        self.url = self.config.get('url')
        self.user_id = self.config.get('user_id')
        self.token = self.config.get('token')
        self.channel = self.config.get('channel')
        self.webhook_url = self.config.get('webhook_url')
        
        # Configurações de timeout e retry
        self.timeout = self.config.get('timeout', 10)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
        
        # Verifica se está configurado
        if self.is_configured():
            self.logger.info("Cliente RocketChat inicializado com sucesso.")
        else:
            self.logger.warning("Cliente RocketChat não configurado corretamente.")

    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração do RocketChat de várias fontes.
        
        Ordem de prioridade:
        1. Arquivo config.py (ROCKETCHAT_CONFIG)
        2. Variáveis de ambiente
        
        Returns:
            Dict com a configuração carregada.
        """
        config = {}
        
        # Carrega do ROCKETCHAT_CONFIG (já importado)
        if ROCKETCHAT_CONFIG:
            config.update(ROCKETCHAT_CONFIG)
        
        # Carrega das variáveis de ambiente
        if os.environ.get('ROCKETCHAT_URL'):
            config['url'] = os.environ.get('ROCKETCHAT_URL')
        
        if os.environ.get('ROCKETCHAT_USER_ID'):
            config['user_id'] = os.environ.get('ROCKETCHAT_USER_ID')
        
        if os.environ.get('ROCKETCHAT_TOKEN'):
            config['token'] = os.environ.get('ROCKETCHAT_TOKEN')
        
        if os.environ.get('ROCKETCHAT_CHANNEL'):
            config['channel'] = os.environ.get('ROCKETCHAT_CHANNEL')
        
        if os.environ.get('ROCKETCHAT_WEBHOOK_URL'):
            config['webhook_url'] = os.environ.get('ROCKETCHAT_WEBHOOK_URL')
        
        return config

    def is_configured(self) -> bool:
        """
        Verifica se o cliente está configurado corretamente.
        
        Returns:
            bool: True se configurado, False caso contrário.
        """
        # Verifica se tem webhook_url OU (url E user_id E token E channel)
        if self.webhook_url:
            return True
        
        return all([self.url, self.user_id, self.token, self.channel])

    def send_message(self, text: str, channel: Optional[str] = None) -> bool:
        """
        Envia uma mensagem para o RocketChat.
        
        Args:
            text: Texto da mensagem (suporta Markdown)
            channel: Canal ou usuário para enviar a mensagem (opcional)
                    Se não fornecido, usa o canal padrão da configuração
        
        Returns:
            bool: True se a mensagem foi enviada com sucesso, False caso contrário
        """
        if not self.is_configured():
            self.logger.error("Cliente RocketChat não configurado corretamente.")
            return False
        
        # Define o canal a ser usado
        target_channel = channel or self.channel
        
        # Tenta enviar a mensagem com retry
        for attempt in range(1, self.max_retries + 1):
            try:
                if self.webhook_url:
                    return self._send_via_webhook(text, target_channel)
                else:
                    return self._send_via_api(text, target_channel)
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt}/{self.max_retries} falhou: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Falha ao enviar mensagem após {self.max_retries} tentativas: {str(e)}")
                    return False
        
        return False

    def _send_via_api(self, text: str, channel: str) -> bool:
        """
        Envia mensagem usando a API REST do RocketChat.
        
        Args:
            text: Texto da mensagem
            channel: Canal ou usuário para enviar
        
        Returns:
            bool: True se enviado com sucesso
        
        Raises:
            Exception: Se ocorrer erro na requisição
        """
        headers = {
            'X-User-Id': self.user_id,
            'X-Auth-Token': self.token,
            'Content-Type': 'application/json'
        }
        
        data = {
            'channel': channel,
            'text': text,
            'alias': 'WegNots',
            'emoji': ':email:'
        }
        
        url = f"{self.url}/api/v1/chat.postMessage"
        
        self.logger.debug(f"Enviando mensagem via API para {channel}")
        response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        
        if response.status_code == 200:
            self.logger.info(f"Mensagem enviada com sucesso para {channel}")
            return True
        else:
            error_msg = f"Erro ao enviar mensagem: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def _send_via_webhook(self, text: str, channel: Optional[str] = None) -> bool:
        """
        Envia mensagem usando webhook do RocketChat.
        
        Args:
            text: Texto da mensagem
            channel: Canal opcional (pode ser ignorado se o webhook já tiver um canal definido)
        
        Returns:
            bool: True se enviado com sucesso
        
        Raises:
            Exception: Se ocorrer erro na requisição
        """
        data = {
            'text': text,
            'alias': 'WegNots',
            'emoji': ':email:'
        }
        
        # Adiciona o canal apenas se fornecido
        if channel:
            data['channel'] = channel
        
        self.logger.debug("Enviando mensagem via webhook")
        response = requests.post(self.webhook_url, json=data, timeout=self.timeout)
        
        if response.status_code in [200, 201, 204]:
            self.logger.info("Mensagem enviada com sucesso via webhook")
            return True
        else:
            error_msg = f"Erro ao enviar mensagem via webhook: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def send_alert(self, 
                  subject: str, 
                  sender: str, 
                  body: str, 
                  alert_level: int = 3,
                  received_date: Optional[str] = None,
                  channel: Optional[str] = None) -> bool:
        """
        Envia um alerta formatado de e-mail para o RocketChat.
        
        Args:
            subject: Assunto do e-mail
            sender: Remetente do e-mail
            body: Corpo do e-mail
            alert_level: Nível de alerta (1=Crítico, 2=Moderado, 3=Leve)
            received_date: Data de recebimento formatada (opcional)
            channel: Canal para enviar (opcional)
        
        Returns:
            bool: True se enviado com sucesso
        """
        # Define emojis e títulos baseados no nível de alerta
        alert_info = {
            1: {"emoji": "🚨", "title": "Alerta Crítico"},
            2: {"emoji": "⚠️", "title": "Alerta Importante"},
            3: {"emoji": "📬", "title": "Novo E-mail"}
        }
        
        # Usa o nível 3 como padrão se o nível fornecido for inválido
        if alert_level not in alert_info:
            alert_level = 3
        
        emoji = alert_info[alert_level]["emoji"]
        title = alert_info[alert_level]["title"]
        
        # Formata a mensagem
        message = f"""
## {emoji} {title}: {subject}

**De:** {sender}
**Assunto:** {subject}
"""
        
        # Adiciona a data se fornecida
        if received_date:
            message += f"**Data:** {received_date}\n"
        
        # Adiciona o corpo do e-mail
        message += f"""
### Conteúdo:
{body}

---
*Este alerta foi gerado automaticamente pelo WegNots*
"""
        
        # Envia a mensagem formatada
        return self.send_message(message, channel)
