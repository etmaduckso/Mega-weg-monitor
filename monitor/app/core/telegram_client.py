import requests
import logging
import json
from datetime import datetime
from .telegram_bot_commands import TelegramCommands

logger = logging.getLogger('wegnots.telegram_client')

class TelegramClient:
    def __init__(self, token, chat_id):
        self.default_token = token
        self.default_chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.commands = TelegramCommands(token)
        
        # Log para debug
        logger.debug("TelegramClient inicializado com suporte a múltiplos destinatários")
        
        # Configura os comandos do bot na inicialização
        self.setup_bot()
        
    def setup_bot(self):
        """Configura os comandos disponíveis no bot"""
        try:
            self.commands.set_bot_commands()
            logger.info("Comandos do bot configurados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao configurar comandos do bot: {e}")
        
    def send_text_message(self, message, parse_mode='Markdown', token=None, chat_id=None):
        """Envia mensagem de texto para o Telegram usando token e chat_id específicos ou os padrões"""
        # Usa os valores padrão se não for fornecido
        token = token or self.default_token
        chat_id = chat_id or self.default_chat_id
        
        # Constrói a URL com o token correto
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        # Faz até 5 tentativas em caso de falha
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"Tentativa {attempt}/{max_retries} de envio para {chat_id}")
                
                response = requests.post(url, json={
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': parse_mode
                }, timeout=10)  # Adicionando timeout de 10 segundos
                
                if response.status_code == 200:
                    logger.info(f"Mensagem enviada com sucesso para chat_id {chat_id}")
                    return True
                else:
                    logger.error(f"Erro ao enviar mensagem para chat_id {chat_id}: {response.status_code} - {response.text}")
                    if attempt < max_retries:
                        # Aguarda um pouco antes de tentar novamente
                        import time
                        time.sleep(2)  
                    else:
                        return False
                    
            except Exception as e:
                logger.error(f"Exceção ao enviar mensagem para chat_id {chat_id}: {e}")
                if attempt < max_retries:
                    # Aguarda um pouco antes de tentar novamente
                    import time
                    time.sleep(2)
                else:
                    return False
        
        return False
            
    def send_alert(self, subject, from_addr, body, alert_type="ALERTA", token=None, chat_id=None):
        """Envia alerta formatado para o Telegram usando token e chat_id específicos"""
        logger.debug("Enviando mensagem de texto simples")
        message = (
            f"*{alert_type}*\n\n"
            f"📧 *De:* {from_addr}\n"
            f"📝 *Assunto:* {subject}\n"
            f"⏰ *Data:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"```\n{body[:500]}...\n```"  # Limita o corpo a 500 caracteres
        )
        
        return self.send_text_message(message, token=token, chat_id=chat_id)
        
    def process_webhook_update(self, update_json):
        """Processa atualizações recebidas via webhook"""
        try:
            update = json.loads(update_json) if isinstance(update_json, str) else update_json
            return self.commands.process_update(update)
        except Exception as e:
            logger.error(f"Erro ao processar webhook update: {e}")
            return False
            
    def check_for_updates(self):
        """Verifica novas mensagens/comandos enviados para o bot"""
        url = f"{self.base_url}/getUpdates"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                updates = response.json().get('result', [])
                
                for update in updates:
                    # Processa cada update
                    self.commands.process_update(update)
                    
                # Confirma processamento dos updates (opcional)
                if updates:
                    last_update_id = updates[-1]['update_id']
                    requests.get(f"{url}?offset={last_update_id + 1}")
                    
                return True
            else:
                logger.error(f"Erro ao verificar atualizações: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao verificar atualizações: {e}")
            return False
            
    def handle_start_command(self, chat_id=None):
        """Responde ao comando /start com uma mensagem amigável em português"""
        if chat_id is None:
            chat_id = self.default_chat_id
            
        return self.commands.handle_start_command(chat_id)