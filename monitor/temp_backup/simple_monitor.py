#!/usr/bin/env python3
import imaplib
import email
import os
import time
import requests
import socket
from datetime import datetime
from email.header import decode_header
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
IMAP_CONFIG = {
    'server': os.getenv('IMAP_SERVER', '3.209.234.72'),  # IP direto do servidor
    'port': int(os.getenv('IMAP_PORT', '993')),
    'username': os.getenv('IMAP_USER', 'sooretama@megasec.com.br'),
    'password': os.getenv('IMAP_PASSWORD', 'Megasec@2025')
}

TELEGRAM_CONFIG = {
    'token': os.getenv('TELEGRAM_TOKEN', '8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID', '1395823978')
}

print("Iniciando monitor com as seguintes configurações:")
print(f"Servidor IMAP: {IMAP_CONFIG['server']}:{IMAP_CONFIG['port']}")
print(f"Usuário: {IMAP_CONFIG['username']}")
print("Verificando resolução DNS...")

try:
    ip = socket.gethostbyname(IMAP_CONFIG['server'])
    print(f"IP resolvido: {ip}")
except Exception as e:
    print(f"Erro na resolução DNS: {e}")

def send_telegram_message(message: str) -> bool:
    """Envia mensagem via Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['token']}/sendMessage"
    try:
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CONFIG['chat_id'],
            'text': message,
            'parse_mode': 'MarkdownV2'  # Usando MarkdownV2 que é mais confiável
        })
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiais do Markdown"""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def decode_header_str(header: Optional[str]) -> str:
    """Decodifica cabeçalhos de e-mail"""
    if not header:
        return ''
    try:
        decoded_parts = []
        for part, charset in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(charset or 'utf-8', errors='replace'))
            else:
                decoded_parts.append(str(part))
        return ''.join(decoded_parts)
    except:
        return str(header)

def get_email_body(message: email.message.Message) -> str:
    """Extrai o corpo do e-mail"""
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(errors='replace')
                except:
                    continue
    try:
        return message.get_payload(decode=True).decode(errors='replace')
    except:
        return "Não foi possível extrair o conteúdo do e-mail"

def monitor_emails():
    """Monitora e-mails e envia alertas"""
    try:
        # Conecta ao servidor IMAP
        mail = imaplib.IMAP4_SSL(IMAP_CONFIG['server'], IMAP_CONFIG['port'])
        mail.login(IMAP_CONFIG['username'], IMAP_CONFIG['password'])
        print("✅ Conectado ao servidor IMAP")
        
        # Envia mensagem de início
        start_message = (
            "🟢 *Monitor Iniciado*\n\n"
            f"⏰ {escape_markdown(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}\n"
            "✉️ Monitorando novos e\\-mails\\.\\.\\."
        )
        send_telegram_message(start_message)
        
        # Loop principal
        while True:
            try:
                # Seleciona a caixa de entrada
                mail.select('INBOX')
                
                # Busca e-mails não lidos
                _, messages = mail.search(None, 'UNSEEN')
                
                # Processa cada e-mail não lido
                for num in messages[0].split():
                    try:
                        # Obtém o e-mail
                        _, msg_data = mail.fetch(num, '(RFC822)')
                        email_body = msg_data[0][1]
                        message = email.message_from_bytes(email_body)
                        
                        # Extrai informações
                        subject = decode_header_str(message['subject'])
                        sender = decode_header_str(message['from'])
                        date = message['date']
                        body = get_email_body(message)
                        
                        # Prepara mensagem para o Telegram
                        alert = (
                            "📨 *Novo E\\-mail*\n\n"
                            f"*De:* {escape_markdown(sender)}\n"
                            f"*Assunto:* {escape_markdown(subject)}\n"
                            f"*Data:* {escape_markdown(date)}\n\n"
                            f"*Conteúdo:*\n{escape_markdown(body[:500])}\\.\\.\\."  # Limita o tamanho
                        )
                        
                        # Envia alerta
                        if send_telegram_message(alert):
                            print(f"✅ Alerta enviado: {subject}")
                        else:
                            print(f"❌ Falha ao enviar alerta: {subject}")
                            
                    except Exception as e:
                        print(f"Erro ao processar e-mail: {e}")
                        continue
                
                # Aguarda 30 segundos antes da próxima verificação
                time.sleep(30)
                
            except Exception as e:
                print(f"Erro no loop principal: {e}")
                time.sleep(60)  # Aguarda 1 minuto em caso de erro
                
    except Exception as e:
        error_msg = f"Erro fatal: {e}"
        print(error_msg)
        send_telegram_message(
            "🔴 *Erro Fatal*\n\n"
            f"⚠️ {escape_markdown(str(e))}\n"
            f"⏰ {escape_markdown(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}"
        )

if __name__ == "__main__":
    monitor_emails()