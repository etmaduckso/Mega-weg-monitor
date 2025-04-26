import requests
import logging
from datetime import datetime

logger = logging.getLogger('wegnots.telegram')

class TelegramClient:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def send_text_message(self, message, parse_mode='Markdown'):
        """Envia mensagem de texto para o Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            response = requests.post(url, json={
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            })
            
            if response.status_code == 200:
                logger.info("Mensagem enviada com sucesso")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem: {e}")
            return False
            
    def send_alert(self, subject, from_addr, body, alert_type="ALERTA"):
        """Envia alerta formatado para o Telegram"""
        message = (
            f"*{alert_type}*\n\n"
            f"📧 *De:* {from_addr}\n"
            f"📝 *Assunto:* {subject}\n"
            f"⏰ *Data:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"```\n{body[:500]}...\n```"  # Limita o corpo a 500 caracteres
        )
        
        return self.send_text_message(message)