import requests
import logging
import time
import re
from typing import Dict, List, Optional
from app.config.settings import TELEGRAM_CONFIG
from .notification_client import NotificationClient
from ..core.user_model import UserModel

logger = logging.getLogger('wegnots.telegram_client')

class TelegramClient(NotificationClient):
    def __init__(self, user_model: UserModel):
        """
        Inicializa o cliente Telegram com as configurações definidas.
        """
        self.bot_token = TELEGRAM_CONFIG.get('bot_token', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.retry_attempts = TELEGRAM_CONFIG.get('retry_attempts', 5)
        self.retry_delay = TELEGRAM_CONFIG.get('retry_delay', 15)
        self.user_model = user_model
        self.default_chat_id = TELEGRAM_CONFIG.get('default_chat_id')
        
        # Estado do registro de usuários
        self.registration_states = {}
        
        logger.debug("TelegramClient inicializado")
        self.start_bot()

    def start_bot(self):
        """Inicia o bot e configura os handlers de comando"""
        self.last_update_id = 0
        self.process_pending_messages()

    def restart_bot(self):
        """Reinicia o bot, limpando estados e reiniciando o processamento de mensagens"""
        logger.info("Reiniciando bot do Telegram...")
        # Limpa estados
        self.registration_states = {}
        self.last_update_id = 0
        # Reinicia processamento
        self.process_pending_messages()
        logger.info("Bot do Telegram reiniciado com sucesso")

    def process_pending_messages(self):
        """Processa mensagens pendentes do bot"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                updates = response.json()
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        self.handle_update(update)
                        self.last_update_id = update['update_id']
        except Exception as e:
            logger.error(f"Erro ao processar mensagens: {e}")

    def handle_update(self, update: Dict):
        """Processa uma atualização do Telegram"""
        try:
            message = update.get('message', {})
            if not message:
                return

            chat_id = str(message.get('chat', {}).get('id'))
            text = message.get('text', '')

            if not chat_id or not text:
                return

            if text.startswith('/start'):
                self.start_registration(chat_id, message)
            elif text.startswith('/cancel'):
                self.cancel_registration(chat_id)
            elif chat_id in self.registration_states:
                self.handle_registration_step(chat_id, text, self.registration_states[chat_id])

        except Exception as e:
            logger.error(f"Erro ao processar update: {e}")

    def start_registration(self, chat_id: str, message: Dict):
        """Inicia o processo de registro do usuário"""
        try:
            # Verifica se já está cadastrado
            existing_user = self.user_model.get_user_by_chat_id(chat_id)
            if existing_user:
                message = (
                    f"✅ Você já está cadastrado e receberá alertas automaticamente!\n\n"
                    f"👤 Nome: {existing_user['name']}\n"
                    f"📧 Email: {existing_user['email']}"
                )
                self._send_message(chat_id, message)
                return

            # Inicia registro
            user_name = message.get('from', {}).get('first_name', 'Usuário')
            self.registration_states[chat_id] = {
                'step': 'name',
                'chat_id': chat_id
            }
            
            # Show system status before starting registration prompt
            self._send_message(chat_id, "✅ Sistema ativo e monitorando")
            response = (
                f"Olá! Para receber alertas automáticos, preciso registrar seus dados:\n\n"
                "👤 Por favor, digite seu *nome completo*:"
            )
            self._send_message(chat_id, response)

        except Exception as e:
            logger.error(f"Erro ao iniciar registro: {e}")
            self._send_message(chat_id, "Desculpe, ocorreu um erro. Por favor, tente novamente com /start")

    def cancel_registration(self, chat_id: str):
        """Cancela o processo de registro"""
        if chat_id in self.registration_states:
            del self.registration_states[chat_id]
        self._send_message(chat_id, "Registro cancelado. Use /start para tentar novamente.")

    def handle_registration_step(self, chat_id: str, text: str, user_data: Dict):
        """Processa cada etapa do registro"""
        if not user_data or chat_id not in self.registration_states:
            return

        current_step = user_data.get('step')

        if current_step == 'name':
            # Valida nome completo (nome + sobrenome)
            parts = [part for part in text.strip().split() if part]
            if len(parts) < 2:
                self._send_message(chat_id, "❌ Por favor, digite seu nome *completo* (nome e sobrenome).")
                return
                
            self.registration_states[chat_id]['name'] = " ".join(parts)
            self.registration_states[chat_id]['step'] = 'email'
            self._send_message(chat_id, "📧 Agora digite seu *e-mail*:")

        elif current_step == 'email':
            if not self._validate_email(text):
                self._send_message(chat_id, "❌ E-mail inválido. Por favor, digite um e-mail válido.")
                return

            try:
                # Salva usuário no banco
                user_data = self.registration_states[chat_id]
                self.user_model.create_user(
                    name=user_data['name'],
                    email=text,
                    chat_id=chat_id
                )

                # Confirma registro
                success_message = (
                    "✅ *Registro concluído com sucesso!*\n\n"
                    f"👤 Nome: {user_data['name']}\n"
                    f"📧 E-mail: {text}\n\n"
                    "Você receberá alertas automáticos quando:\n"
                    "1. Seu e-mail estiver no remetente\n"
                    "2. Houver alertas para sua área\n\n"
                    "Para cancelar o registro use /cancel"
                )
                self._send_message(chat_id, success_message)
                
                # Limpa estado
                del self.registration_states[chat_id]

            except Exception as e:
                logger.error(f"Erro ao finalizar registro: {e}")
                self._send_message(chat_id, "❌ Erro ao salvar registro. Por favor, tente novamente.")
                del self.registration_states[chat_id]

    def _validate_email(self, email: str) -> bool:
        """Valida formato do e-mail"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def _send_message(self, chat_id: str, message: str) -> bool:
        """Envia mensagem com retry automático"""
        url = f"{self.base_url}/sendMessage"
        
        # Divide mensagens grandes
        if len(message) > 4000:
            parts = self._split_message(message)
            success = True
            for part in parts:
                if not self._send_message_with_retry(url, chat_id, part):
                    success = False
            return success
        
        return self._send_message_with_retry(url, chat_id, message)

    def _send_message_with_retry(self, url: str, chat_id: str, message: str) -> bool:
        """Envia mensagem com retry e backoff exponencial"""
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(url, json=params, timeout=60)
                
                if response.status_code == 200 and response.json().get('ok'):
                    return True

                if response.status_code in [408, 502, 503, 504]:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                
                logger.warning(f"Erro ao enviar mensagem: {response.status_code}")
                
            except Exception as e:
                logger.error(f"Erro na requisição: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                
        return False

    def _split_message(self, message: str) -> List[str]:
        """Divide mensagem grande em partes menores"""
        max_length = 3800
        if len(message) <= max_length:
            return [message]
            
        parts = []
        current_part = ""
        
        for line in message.split('\n'):
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = line + '\n'
                
        if current_part:
            parts.append(current_part.strip())
            
        return parts

    def send_alert(self, equipment_id: str, alert_type: int, user: str, extra_info: Optional[Dict] = None):
        """Envia alerta para usuários baseado nos dados do email"""
        message = self._format_alert_message(equipment_id, alert_type, user, extra_info)
        
        # Determina destinatários baseado no remetente e assunto
        recipients = []
        
        if extra_info:
            sender = extra_info.get('from', '')
            subject = extra_info.get('subject', '')
            
            # Busca usuários pelo email do remetente
            if sender:
                users = self.user_model.get_users_by_email(sender)
                recipients.extend(user['chat_id'] for user in users)
            
            # Adiciona usuários baseado no assunto
            if subject:
                # Implementar lógica de roteamento por assunto aqui
                pass
        
        # Usa chat_id padrão se não encontrar destinatários
        if not recipients:
            recipients = [self.default_chat_id]
        
        # Envia para cada destinatário
        success = False
        for chat_id in recipients:
            if self._send_message(chat_id, message):
                success = True
                logger.info(f"Alerta enviado para chat_id: {chat_id}")
            else:
                logger.warning(f"Falha ao enviar alerta para chat_id: {chat_id}")
        
        return success

    def _format_alert_message(self, equipment_id: str, alert_type: int, user: str, extra_info: Optional[Dict] = None) -> str:
        """Formata mensagem de alerta"""
        alert_icons = {
            1: "🚨",  # Crítico
            2: "⚠️",  # Moderado
            3: "ℹ️",  # Informativo
        }
        
        message = (
            f"{alert_icons.get(alert_type, '❗')} *ALERTA*\n\n"
            f"🔧 Equipamento: {equipment_id}\n"
            f"👤 Usuário: {user}\n"
            f"⏰ Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        )
        
        if extra_info:
            message += "\n*Detalhes:*\n"
            if 'subject' in extra_info:
                message += f"📝 Assunto: {extra_info['subject']}\n"
            if 'from' in extra_info:
                message += f"📤 Remetente: {extra_info['from']}\n"
            if 'date' in extra_info:
                message += f"📅 Data Email: {extra_info['date']}\n"
            
        return message

    def send_text_message(self, text: str, recipients: Optional[List[str]] = None) -> bool:
        """Implementação do método abstrato da classe NotificationClient"""
        if not recipients:
            recipients = [self.default_chat_id]
            
        success = True
        for chat_id in recipients:
            if not self._send_message(chat_id, text):
                success = False
                
        return success
