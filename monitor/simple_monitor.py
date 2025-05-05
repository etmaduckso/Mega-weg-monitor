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
import signal
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from typing import List, Dict
from dataclasses import dataclass
from app.core.email_handler import EmailHandler

# Configurar locale para português
os.environ['LANG'] = 'pt_BR.UTF-8'
os.environ['LC_ALL'] = 'pt_BR.UTF-8'

# Verificar que o diretório de logs existe
os.makedirs('logs', exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/wegnots.log'), logging.StreamHandler()],
    datefmt='%A, %d de %B de %Y %H:%M'
)

# Variável global para controlar o encerramento gracioso
running = True

def signal_handler(sig, frame):
    """Manipulador de sinais para encerramento gracioso"""
    global running
    logging.info("Sinal de encerramento recebido. Encerrando monitoramento...")
    running = False

# Registra o handler de sinal para encerramento gracioso (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

@dataclass
class IMAPConfig:
    server: str
    port: int
    username: str
    password: str
    is_active: bool
    telegram_chat_id: str = ""  # Chat ID específico para esta conta de email
    telegram_token: str = ""    # Token específico para esta conta de email

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

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiais do Markdown V2 do Telegram."""
    if not text:
        return ""
    # Escape backslash first
    text = text.replace('\\', '\\\\')
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!', '@']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def send_telegram_notification(config: TelegramConfig, message: str) -> bool:
    """Envia uma notificação via Telegram de forma síncrona"""
    url = f"https://api.telegram.org/bot{config.token}/sendMessage"
    try:
        response = requests.post(url, json={
            'chat_id': config.chat_id,
            'text': message,
            'parse_mode': 'MarkdownV2',
            'disable_web_page_preview': True
        }, timeout=10)
        
        if response.status_code == 200:
            logging.info(f"Notificação enviada com sucesso para chat_id {config.chat_id}")
            return True
        else:
            logging.error(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exceção ao enviar notificação: {e}")
        return False

def send_system_startup_notification(config: TelegramConfig, active_accounts=None) -> bool:
    """
    Envia notificação de inicialização do sistema.
    Para o caso do simple_monitor que usa a classe TelegramConfig diretamente.
    """
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = (
        "🟢 *WegNots Monitor Iniciado*\n\n"
        f"⏰ {escape_markdown(current_time)}\n"
        "✅ Sistema de monitoramento iniciado com sucesso\\.\n"
        "✉️ Monitorando e\\-mails\\.\\.\\."
    )
    
    # Adiciona informação sobre as contas monitoradas
    if active_accounts:
        message += f"\n\n📨 Contas monitoradas: {len(active_accounts)}"
        for i, account in enumerate(active_accounts, 1):
            message += f"\n   {i}\\. {escape_markdown(account)}"
    
    return send_telegram_notification(config, message)

def send_system_shutdown_notification(config: TelegramConfig) -> bool:
    """
    Envia notificação de encerramento do sistema.
    Para o caso do simple_monitor que usa a classe TelegramConfig diretamente.
    """
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = (
        "🔴 *WegNots Monitor Encerrado*\n\n"
        f"⏰ {escape_markdown(current_time)}\n"
        "✅ Sistema encerrado de forma segura\\.\n"
        "🔔 Monitoramento interrompido\\."
    )
    
    return send_telegram_notification(config, message)

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
    
    def disconnect(self):
        """Desconecta do servidor IMAP de forma segura"""
        if self.imap and self.connected:
            try:
                self.imap.close()
                self.imap.logout()
                logging.info(f"Desconectado do servidor {self.config.server}")
                self.connected = False
                return True
            except Exception as e:
                logging.error(f"Erro ao desconectar do servidor {self.config.server}: {str(e)}")
                return False
        return True

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
                    'date': date_str,
                    'username': self.config.username  # Adicionar o campo username para identificar a conta
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
        self.imap_config_map = {}  # Mapa para associar usernames a suas configurações
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
                    imap_config = IMAPConfig(
                        server=config[section]['server'],
                        port=int(config[section]['port']),
                        username=config[section]['username'],
                        password=config[section]['password'],
                        is_active=config[section].getboolean('is_active', True),
                        telegram_chat_id=config[section].get('telegram_chat_id', ''),
                        telegram_token=config[section].get('telegram_token', '')
                    )
                    imap_configs.append(imap_config)
                    # Mapear o username para sua configuração
                    self.imap_config_map[imap_config.username] = imap_config
                    
                    chat_id_info = ""
                    if imap_config.telegram_chat_id:
                        chat_id_info = f" (Chat ID específico: {imap_config.telegram_chat_id})"
                    logging.info(f"Configuração IMAP carregada para: {imap_config.username} em {imap_config.server}{chat_id_info}")
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
        """Inicializa todos os monitores e envia notificação de inicialização"""
        active_accounts = []
        
        # Mapeamento de chat_ids específicos para as contas que eles monitoram
        specific_targets = {}
        
        for imap_config in self.config['imap']:
            if imap_config.is_active:
                monitor = IMAPMonitor(imap_config)
                if await monitor.connect():
                    self.monitors.append(monitor)
                    active_accounts.append(imap_config.username)
                    
                    # Se essa conta tem configuração específica de Telegram, adiciona ao mapeamento
                    if imap_config.telegram_chat_id and imap_config.telegram_token:
                        key = (imap_config.telegram_chat_id, imap_config.telegram_token)
                        if key not in specific_targets:
                            specific_targets[key] = []
                        specific_targets[key].append(imap_config.username)
                    
                    logging.info(f"Monitor para {imap_config.server} ({imap_config.username}) inicializado")
                else:
                    logging.error(f"Falha ao inicializar monitor para {imap_config.server} ({imap_config.username})")
        
        # Envia notificação global
        send_system_startup_notification(self.config['telegram'], active_accounts)
        
        # Envia notificações específicas para cada destinatário com token personalizado
        for (chat_id, token), accounts in specific_targets.items():
            if not accounts:
                continue
                
            config = TelegramConfig(token=token, chat_id=chat_id)
            send_system_startup_notification(config, accounts)
    
    def should_continue(self) -> bool:
        """
        Verifica se o serviço de monitoramento deve continuar executando.
        Esta função pode ser estendida com mais condições como verificar um arquivo
        de status ou indicadores de saúde do sistema.
        """
        return self.active and running and any(monitor.connected for monitor in self.monitors)
    
    async def shutdown(self):
        """Encerra todas as conexões IMAP de forma segura e envia notificação de encerramento"""
        logging.info("Iniciando procedimento de encerramento...")
        
        # Desconecta todos os monitores
        for monitor in self.monitors:
            monitor.disconnect()
        
        # Mapeamento de chat_ids específicos para as contas que eles monitoram
        specific_targets = {}
        
        # Agrupa contas por chat_id/token específico
        for username, imap_config in self.imap_config_map.items():
            if imap_config.telegram_chat_id and imap_config.telegram_token and imap_config.is_active:
                key = (imap_config.telegram_chat_id, imap_config.telegram_token)
                if key not in specific_targets:
                    specific_targets[key] = []
                specific_targets[key].append(username)
        
        # Envia notificação global de encerramento
        send_system_shutdown_notification(self.config['telegram'])
        
        # Envia notificações específicas de encerramento
        for (chat_id, token), accounts in specific_targets.items():
            if not accounts:
                continue
                
            # Cria uma mensagem personalizada para este destinatário
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Mensagem base
            message = (
                "🔴 *WegNots Monitor Encerrado*\n\n"
                f"⏰ {escape_markdown(current_time)}\n"
                "✅ Sistema encerrado de forma segura\\.\n"
                "🔔 Monitoramento interrompido\\."
            )
            
            # Adiciona informação sobre as contas que estavam sendo monitoradas
            if len(accounts) > 1:
                message += f"\n\n📨 O monitoramento das seguintes contas foi encerrado:"
                for i, account in enumerate(accounts, 1):
                    message += f"\n   {i}\\. {escape_markdown(account)}"
            else:
                message += f"\n\n📨 O monitoramento da conta {escape_markdown(accounts[0])} foi encerrado\\."
                
            # Envia a notificação personalizada
            config = TelegramConfig(token=token, chat_id=chat_id)
            send_telegram_notification(config, message)
        
        logging.info("Sistema encerrado com sucesso")
    
    async def monitor_emails(self):
        """Monitora os emails e envia notificações via Telegram"""
        while self.should_continue():
            try:
                # Coleta emails de todos os monitores
                all_emails = []
                for monitor in self.monitors:
                    emails = await monitor.check_emails()
                    all_emails.extend(emails)
                
                # Processa todos os emails coletados
                for email_data in all_emails:
                    # Criar mensagem de notificação
                    message = (
                        f"📨 Novo email de {email_data['sender']}\n"
                        f"📝 Assunto: {email_data['subject']}\n"
                        f"🌐 Servidor: {email_data['server']}\n"
                        f"📅 Data: {email_data['date']}"
                    )
                    
                    # Obter a configuração associada a este email
                    username = email_data.get('username', '')
                    imap_config = self.imap_config_map.get(username)
                    
                    if imap_config and imap_config.telegram_chat_id:  # Fixed syntax error here (changed && to and)
                        # Se esta conta de email tem um chat_id específico, usar ele
                        specific_notifier = TelegramNotifier(TelegramConfig(
                            token=imap_config.telegram_token or self.config['telegram'].token,
                            chat_id=imap_config.telegram_chat_id
                        ))
                        await specific_notifier.send_notification(message)
                        logging.info(f"Notificação enviada para chat_id específico: {imap_config.telegram_chat_id} (email: {username})")
                    else:
                        # Caso contrário, usar o chat_id global
                        await self.notifier.send_notification(message)
                        logging.info(f"Notificação enviada para chat_id global: {self.config['telegram'].chat_id}")
                
                # Aguarda antes de verificar novamente
                await asyncio.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logging.error(f"Erro no loop de monitoramento: {str(e)}")
                # Se houver um erro, espera um pouco antes de tentar novamente
                await asyncio.sleep(10)
        
        logging.info("Loop de monitoramento encerrado")
        # Executa processo de encerramento adequado
        await self.shutdown()

def monitor_unread_emails():
    """Monitora os últimos 5 emails não lidos a cada 30 segundos."""
    telegram_client = TelegramNotifier(config=TelegramConfig(token='SEU_TOKEN', chat_id='SEU_CHAT_ID'))
    email_handler = EmailHandler(telegram_client=telegram_client)

    while True:
        for account in email_handler.accounts:
            try:
                print(f"Verificando emails não lidos para a conta: {account['username']}")
                unread_emails = email_handler.get_unread_emails(account, limit=5)

                if unread_emails:
                    print(f"Últimos 5 emails não lidos para {account['username']}:")
                    for email in unread_emails:
                        print(f"- De: {email['from']}, Assunto: {email['subject']}, Data: {email['date']}")
                else:
                    print(f"Nenhum email não lido encontrado para {account['username']}.")
            except Exception as e:
                print(f"Erro ao verificar emails para {account['username']}: {e}")

        print("Aguardando 30 segundos antes da próxima verificação...")
        time.sleep(30)

async def main():
    try:
        logging.info("=" * 60)
        logging.info(f"Iniciando WegNots Monitor (simple_monitor) em {datetime.now()}")
        logging.info("=" * 60)
        
        service = EmailMonitoringService()
        await service.initialize()
        await service.monitor_emails()
        
        return 0
    except Exception as e:
        logging.exception(f"Erro fatal durante execução: {e}")
        return 1

if __name__ == "__main__":
    try:
        monitor_unread_emails()
    except KeyboardInterrupt:
        logging.info("Programa interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logging.exception(f"Erro não tratado: {e}")
        sys.exit(1)
