#!/usr/bin/env python3
import os
import json
import time
import imaplib
import email
import logging
import requests
import locale
import asyncio
import configparser
from datetime import datetime, timedelta
from email.header import decode_header
from typing import List, Dict
from dataclasses import dataclass

# Configurar locale para português
os.environ['LANG'] = 'pt_BR.UTF-8'
os.environ['LC_ALL'] = 'pt_BR.UTF-8'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/wegnots.log'), logging.StreamHandler()],
    datefmt='%A, %d de %B de %Y %H:%M'
)

@dataclass
class IMAPConfig:
    server: str
    port: int
    username: str
    password: str
    is_active: bool
    telegram_chat_id: str = ""  # Chat ID específico para esta conta de email

@dataclass
class TelegramConfig:
    token: str
    chat_id: str

def decode_email_header(header):
    """Decodifica cabeçalhos de email corretamente, lidando com diferentes codificações."""
    if not header:
        return ""
    
    decoded_parts = []
    for part, charset in decode_header(header):
        if isinstance(part, bytes):
            try:
                # Tenta decodificar com o charset fornecido
                if charset:
                    decoded_parts.append(part.decode(charset))
                else:
                    # Se não houver charset, tenta UTF-8 primeiro, depois latin1
                    try:
                        decoded_parts.append(part.decode('utf-8'))
                    except UnicodeDecodeError:
                        decoded_parts.append(part.decode('latin1'))
            except (UnicodeDecodeError, LookupError):
                # Se falhar, tenta latin1 como fallback
                decoded_parts.append(part.decode('latin1'))
        else:
            decoded_parts.append(str(part))
    
    return ' '.join(decoded_parts)

class IMAPMonitor:
    def __init__(self, config: IMAPConfig):
        self.config = config
        self.imap = None
        self.connected = False
        
    async def connect(self):
        try:
            self.imap = imaplib.IMAP4_SSL(self.config.server, self.config.port)
            self.imap.login(self.config.username, self.config.password)
            self.connected = True
            logging.info(f"Conectado ao servidor {self.config.server}")
            return True
        except Exception as e:
            logging.error(f"Erro ao conectar ao servidor {self.config.server}: {str(e)}")
            self.connected = False
            return False

    async def check_emails(self):
        if not self.connected:
            return []
        
        try:
            self.imap.select('INBOX')
            # Buscar todos os emails e pegar os últimos 30
            _, messages = self.imap.search(None, 'ALL')
            email_ids = messages[0].split()
            
            # Pegar os últimos 30 emails
            last_30_emails = email_ids[-30:] if len(email_ids) > 30 else email_ids
            
            new_emails = []
            for num in last_30_emails:
                _, msg = self.imap.fetch(num, '(RFC822)')
                email_body = msg[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Usar a nova função de decodificação
                subject = decode_email_header(email_message['subject'])
                sender = decode_email_header(email_message['from'])
                
                # Obter a data do email
                date_str = email_message['date']
                
                new_emails.append({
                    'subject': subject,
                    'sender': sender,
                    'server': self.config.server,
                    'date': date_str
                })
            
            return new_emails
        except Exception as e:
            logging.error(f"Erro ao verificar emails em {self.config.server}: {str(e)}")
            return []
            
class TelegramNotifier:
    def __init__(self, config: TelegramConfig):
        self.config = config
        self._last_send_time = 0
        self._min_interval = 1  # seconds between messages
    
    def escape_markdown(self, text: str) -> str:
        """Escapa caracteres especiais do Markdown V2 do Telegram."""
        # Escape backslash first
        text = text.replace('\\', '\\\\')
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!', '@']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
        
    async def send_notification(self, message: str):
        try:
            now = time.time()
            elapsed = now - self._last_send_time
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            url = f"https://api.telegram.org/bot{self.config.token}/sendMessage"
            
            # Preparar a mensagem com os caracteres especiais escapados
            lines = []
            for line in message.split('\n'):
                if line.startswith('📨'):  # Linha do remetente
                    prefix, content = line.split(' de ', 1)
                    lines.append(f"{prefix} de *{self.escape_markdown(content)}*")
                elif line.startswith('📝'):  # Linha do assunto
                    prefix, content = line.split(': ', 1)
                    lines.append(f"{prefix}: _{self.escape_markdown(content)}_")
                else:  # Outras linhas
                    lines.append(self.escape_markdown(line))
            
            formatted_message = '\n'.join(lines)
            
            data = {
                "chat_id": self.config.chat_id,
                "text": formatted_message,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=data)
            response_json = response.json()
            self._last_send_time = time.time()
            if response.status_code != 200 or not response_json.get('ok'):
                logging.error(f"Erro ao enviar mensagem para Telegram: {response_json}")
                return False
            
            logging.info("Mensagem enviada com sucesso para Telegram")
            return True
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem para Telegram: {str(e)}")
            return False

class EmailMonitoringService:
    def __init__(self):
        self.config = self._load_config()
        self.monitors: List[IMAPMonitor] = []
        self.notifier = TelegramNotifier(self.config['telegram'])
        self.active = True
        
    def _load_config(self) -> Dict:
        # Encontrar o caminho absoluto do script para garantir que o caminho do config.ini esteja correto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Tentar diferentes locais possíveis para o config.ini
        possible_paths = [
            os.path.join(script_dir, 'config.ini'),  # Local relativo ao script
            os.path.join(script_dir, '..', 'config.ini'),  # Um nível acima
            '/app/config.ini',  # Caminho comum em ambientes Docker
        ]
        
        config = configparser.ConfigParser()
        config_loaded = False
        
        for config_path in possible_paths:
            if os.path.exists(config_path):
                try:
                    config.read(config_path)
                    logging.info(f"Arquivo de configuração carregado: {config_path}")
                    config_loaded = True
                    break
                except Exception as e:
                    logging.error(f"Erro ao carregar arquivo de configuração {config_path}: {str(e)}")
        
        if not config_loaded:
            error_msg = "Nenhum arquivo de configuração encontrado"
            logging.critical(error_msg)
            raise FileNotFoundError(error_msg)
        
        imap_configs = []
        for section in config.sections():
            if section.startswith('IMAP_'):
                try:
                    imap_configs.append(IMAPConfig(
                        server=config[section]['server'],
                        port=int(config[section]['port']),
                        username=config[section]['username'],
                        password=config[section]['password'],
                        is_active=config[section].getboolean('is_active', True),
                        telegram_chat_id=config[section].get('telegram_chat_id', '')
                    ))
                    chat_id_info = ""
                    if 'telegram_chat_id' in config[section] and config[section]['telegram_chat_id']:
                        chat_id_info = f" (Chat ID específico: {config[section]['telegram_chat_id']})"
                    logging.info(f"Configuração IMAP carregada para: {config[section]['server']}{chat_id_info}")
                except Exception as e:
                    logging.error(f"Erro ao carregar configuração IMAP para {section}: {str(e)}")
        
        # Verificar se há uma seção TELEGRAM
        if 'TELEGRAM' not in config:
            error_msg = "Seção TELEGRAM não encontrada no arquivo de configuração"
            logging.critical(error_msg)
            raise KeyError(error_msg)
        
        telegram_config = TelegramConfig(
            token=config['TELEGRAM']['token'],
            chat_id=config['TELEGRAM']['chat_id']
        )
        
        logging.info(f"Configurações carregadas: {len(imap_configs)} servidores IMAP")
        return {
            'imap': imap_configs,
            'telegram': telegram_config
        }
    
    async def initialize(self):
        for imap_config in self.config['imap']:
            if imap_config.is_active:
                monitor = IMAPMonitor(imap_config)
                if await monitor.connect():
                    self.monitors.append(monitor)
                    logging.info(f"Monitor para {imap_config.server} inicializado")
                else:
                    logging.error(f"Falha ao inicializar monitor para {imap_config.server}")
    
    def should_continue(self) -> bool:
        """
        Checks if the monitoring service should continue running.
        This can be extended with more conditions like checking a status file
        or system health indicators.
        """
        return self.active and any(monitor.connected for monitor in self.monitors)
    
    async def monitor_emails(self):
        """Monitora os emails e envia notificações via Telegram"""
        # Cria um dicionário para associar monitores aos seus respectivos configs
        monitor_configs = {monitor: config for monitor, config in zip(self.monitors, [c for c in self.config['imap'] if c.is_active])}
        
        while self.should_continue():
            try:
                # Coleta emails de todos os monitores
                results = []
                for monitor in self.monitors:
                    emails = await monitor.check_emails()
                    for email_data in emails:
                        # Adiciona o config do monitor a cada email para podermos acessar o chat_id específico
                        email_data['monitor_config'] = monitor_configs[monitor]
                    results.append(emails)
                
                # Processa todos os emails coletados
                for emails in results:
                    for email_data in emails:
                        message = (
                            f"📨 Novo email de {email_data['sender']}\n"
                            f"📝 Assunto: {email_data['subject']}\n"
                            f"🌐 Servidor: {email_data['server']}\n"
                            f"📅 Data: {email_data['date']}"
                        )
                        
                        # Verifica se existe um chat_id específico para esta conta
                        monitor_config = email_data['monitor_config']
                        if monitor_config.telegram_chat_id:
                            # Cria um notificador temporário com o chat_id específico
                            specific_notifier = TelegramNotifier(TelegramConfig(
                                token=self.config['telegram'].token,
                                chat_id=monitor_config.telegram_chat_id
                            ))
                            await specific_notifier.send_notification(message)
                            logging.info(f"Notificação enviada para chat_id específico: {monitor_config.telegram_chat_id}")
                        else:
                            # Usa o notificador padrão (chat_id global)
                            await self.notifier.send_notification(message)
                            logging.info(f"Notificação enviada para chat_id global: {self.config['telegram'].chat_id}")
                
                # Aguarda antes de verificar novamente
                await asyncio.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logging.error(f"Erro no loop de monitoramento: {str(e)}")
                # Se houver um erro, espera um pouco antes de tentar novamente
                await asyncio.sleep(10)
        
        logging.info("Serviço de monitoramento encerrado")

async def main():
    service = EmailMonitoringService()
    await service.initialize()
    await service.monitor_emails()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('wegnots.log'),
            logging.StreamHandler()
        ]
    )
    
    asyncio.run(main())
