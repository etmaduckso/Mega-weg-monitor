import imaplib
import email
import logging
import time
from email.header import decode_header
from typing import List, Dict, Optional

from app.config.settings import IMAP_CONFIG
from .notification_client import NotificationClient
from .telegram_client import TelegramClient

logger = logging.getLogger('wegnots.email_handler')

class EmailHandler:
    def __init__(self, notification_clients: List[NotificationClient]):
        # Configurações IMAP
        self.server = IMAP_CONFIG.get('server', '')
        self.port = IMAP_CONFIG.get('port', 993)
        self.username = IMAP_CONFIG.get('username', '')
        self.password = IMAP_CONFIG.get('password', '')
        self.check_interval = IMAP_CONFIG.get('check_interval', 60)
        self.reconnect_attempts = IMAP_CONFIG.get('reconnect_attempts', 5)
        self.reconnect_delay = IMAP_CONFIG.get('reconnect_delay', 30)
        self.reconnect_backoff = IMAP_CONFIG.get('reconnect_backoff_factor', 1.5)
        
        # Clientes de notificação
        self.notification_clients = notification_clients
        self.telegram_client = next(
            (client for client in notification_clients if isinstance(client, TelegramClient)),
            None
        )
        
        logger.debug(f"EmailHandler inicializado para servidor {self.server}:{self.port}")
        
        # Estabelece conexão inicial
        self.connect_and_login()

    def connect_and_login(self) -> bool:
        """Estabelece conexão e faz login no servidor IMAP"""
        try:
            # Tenta conectar
            if not self.connect():
                return False
                
            # Se conectou, tenta login
            if not self.login():
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar e fazer login: {e}")
            return False

    def connect(self) -> bool:
        """Estabelece conexão com servidor IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.server, self.port)
            logger.debug("Conexão IMAP estabelecida")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao servidor IMAP: {e}")
            return False
            
    def login(self) -> bool:
        """Realiza login no servidor IMAP"""
        for attempt in range(self.reconnect_attempts):
            try:
                logger.info(f"Tentativa {attempt + 1}/{self.reconnect_attempts} de login no IMAP com usuário {self.username}")
                self.imap.login(self.username, self.password)
                logger.info("Login IMAP bem-sucedido")
                return True
            except Exception as e:
                logger.error(f"Erro no login IMAP (tentativa {attempt + 1}): {e}")
                if attempt < self.reconnect_attempts - 1:
                    delay = self.reconnect_delay * (self.reconnect_backoff ** attempt)
                    time.sleep(delay)
        return False

    def check_new_emails(self) -> List[str]:
        """Verifica se há novos emails não lidos"""
        logger.debug("Verificando novos e-mails...")
        try:
            # Tenta selecionar INBOX
            status, _ = self.imap.select('INBOX')
            if status != 'OK':
                # Se falhou, tenta reconectar
                logger.warning("Seleção da INBOX falhou. Tentando reconectar...")
                if not self.connect_and_login():
                    return []
                    
                # Tenta selecionar INBOX novamente
                status, _ = self.imap.select('INBOX')
                if status != 'OK':
                    logger.error("Falha ao selecionar INBOX mesmo após reconexão")
                    return []
                    
            # Busca emails não lidos
            _, messages = self.imap.search(None, 'UNSEEN')
            return messages[0].split()
            
        except Exception as e:
            logger.error(f"Erro ao verificar novos emails: {e}")
            return []

    def parse_email(self, email_id: str) -> Optional[Dict]:
        """
        Processa um email e extrai informações relevantes.
        Retorna um dicionário com os dados do email ou None em caso de erro.
        """
        try:
            _, msg_data = self.imap.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)
            
            subject = self._decode_header(msg['subject'])
            sender = msg['from']
            date = msg['date']

            # Extrai informações do assunto
            alert_info = self._parse_alert_subject(subject)
            if alert_info:
                return {
                    'equipment_id': alert_info['equipment_id'],
                    'alert_type': alert_info['alert_type'],
                    'subject': subject,
                    'from': sender,
                    'date': date
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar email {email_id}: {e}")
            return None

    def _decode_header(self, header: Optional[str]) -> str:
        """Decodifica cabeçalho do email"""
        if not header:
            return ''
            
        try:
            decoded = decode_header(header)
            parts = []
            for text, charset in decoded:
                if isinstance(text, bytes):
                    text = text.decode(charset or 'utf-8', errors='ignore')
                parts.append(str(text))
            return ' '.join(parts)
        except Exception as e:
            logger.error(f"Erro ao decodificar cabeçalho: {e}")
            return header

    def _parse_alert_subject(self, subject: str) -> Optional[Dict]:
        """
        Analisa o assunto do email para extrair informações do alerta.
        Formato esperado: equipamento-nivel 
        Exemplo: "servidor01-1" para alerta crítico do servidor01
        """
        try:
            if not subject or '-' not in subject:
                return None
                
            parts = subject.strip().split('-')
            if len(parts) != 2:
                return None
                
            equipment_id = parts[0].strip()
            try:
                alert_type = int(parts[1])
                if alert_type not in [1, 2, 3]:  # 1=Crítico, 2=Moderado, 3=Informativo
                    alert_type = 3  # Default para informativo
            except ValueError:
                alert_type = 3
                
            return {
                'equipment_id': equipment_id,
                'alert_type': alert_type
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar assunto do email: {e}")
            return None

    def process_emails(self):
        """Processa emails não lidos e envia alertas"""
        new_emails = self.check_new_emails()
        
        for email_id in new_emails:
            email_data = self.parse_email(email_id)
            if email_data:
                # Envia alerta via Telegram se configurado
                if self.telegram_client:
                    extra_info = {
                        'subject': email_data.get('subject', ''),
                        'from': email_data.get('from', ''),
                        'date': email_data.get('date', '')
                    }
                    
                    self.telegram_client.send_alert(
                        equipment_id=email_data['equipment_id'],
                        alert_type=email_data['alert_type'],
                        user=self.username,  # Usa conta IMAP como usuário
                        extra_info=extra_info
                    )
                    
                # Envia para outros clientes de notificação configurados
                for client in self.notification_clients:
                    if not isinstance(client, TelegramClient):
                        client.send_alert(
                            equipment_id=email_data['equipment_id'],
                            alert_type=email_data['alert_type'],
                            user=self.username
                        )

    def close(self):
        """Fecha conexão com servidor IMAP"""
        try:
            if hasattr(self, 'imap'):
                self.imap.close()
                self.imap.logout()
                logger.info("Logout IMAP realizado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão IMAP: {e}")
