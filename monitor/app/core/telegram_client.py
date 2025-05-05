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
        
        # Mapping for specific token -> chat_id relationships
        self.token_chat_map = {
            # Token-specific chat IDs will be discovered and stored here
        }
        
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
        
        # Se chat_id não for fornecido ou estiver vazio, verifica se há um mapeamento por token
        if not chat_id and token in self.token_chat_map:
            chat_id = self.token_chat_map[token]
            logger.info(f"Usando chat_id {chat_id} mapeado para o token {token[:8]}...")
        else:
            chat_id = chat_id or self.default_chat_id
        
        # Constrói a URL com o token correto
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        # Faz até 5 tentativas em caso de falha
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"Tentativa {attempt}/{max_retries} de envio para {chat_id} usando token: {token[:8]}...")
                
                response = requests.post(url, json={
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': parse_mode
                }, timeout=10)  # Adicionando timeout de 10 segundos
                
                if response.status_code == 200:
                    logger.info(f"Mensagem enviada com sucesso para chat_id {chat_id} usando token: {token[:8]}...")
                    
                    # Se a mensagem foi enviada com sucesso para um token específico
                    # e não havia mapeamento anterior, salva o mapeamento
                    if token != self.default_token and token not in self.token_chat_map:
                        self.token_chat_map[token] = chat_id
                        logger.info(f"Mapeamento token->chat_id salvo: {token[:8]}... -> {chat_id}")
                        
                    return True
                else:
                    logger.error(f"Erro ao enviar mensagem para chat_id {chat_id} usando token {token[:8]}: {response.status_code} - {response.text}")
                    if attempt < max_retries:
                        # Aguarda um pouco antes de tentar novamente
                        import time
                        time.sleep(2)  
                    else:
                        return False
                    
            except Exception as e:
                logger.error(f"Exceção ao enviar mensagem para chat_id {chat_id} usando token {token[:8]}: {e}")
                if attempt < max_retries:
                    # Aguarda um pouco antes de tentar novamente
                    import time
                    time.sleep(2)
                else:
                    return False
        
        return False

    def escape_markdown(self, text):
        """Escapa caracteres especiais do Markdown V2"""
        if not text:
            return ""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        escaped_text = text
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        return escaped_text
            
    def send_alert(self, subject, from_addr, body, alert_type="📨 NOVO EMAIL", token=None, chat_id=None):
        """Envia alerta formatado para o Telegram usando token e chat_id específicos"""
        try:
            # Escapa todos os textos para Markdown V2
            safe_subject = self.escape_markdown(subject)
            safe_from = self.escape_markdown(from_addr)
            safe_body = self.escape_markdown(body)

            # Cria mensagem formatada
            message = (
                f"*{alert_type}*\n\n"
                f"📧 *De:* {safe_from}\n"
                f"📝 *Assunto:* {safe_subject}\n"
                f"⏰ *Data:* {self.escape_markdown(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}\n\n"
                f"💬 *Conteúdo:*\n```\n{safe_body[:1000]}```"  # Limita o corpo a 1000 caracteres
            )

            # Envia usando configurações específicas ou padrão
            return self.send_text_message(
                message=message, 
                parse_mode='MarkdownV2',
                token=token, 
                chat_id=chat_id
            )
        except Exception as e:
            logger.error(f"Erro ao formatar/enviar alerta: {e}")
            # Tenta enviar uma versão simplificada em caso de erro
            fallback_message = (
                f"*{alert_type}*\n\n"
                f"📧 De: {subject}\n"
                f"📝 Assunto: {from_addr}\n"
                f"⏰ Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            return self.send_text_message(
                message=fallback_message,
                parse_mode='Markdown',  # Usa Markdown simples como fallback
                token=token,
                chat_id=chat_id
            )
        
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
        
    def initialize_chat_mappings(self, config_sections=None):
        """
        Inicializa mapeamentos de token -> chat_id a partir de seções de configuração 
        e também tenta descobrir automaticamente o chat_id correto para cada token.
        """
        if not config_sections:
            return
            
        # First, create mappings from configuration
        for section_name, config in config_sections.items():
            if not section_name.startswith('IMAP_'):
                continue
                
            # Check for notification_destinations
            try:
                if 'notification_destinations' in config:
                    destinations = json.loads(config['notification_destinations'])
                    for dest_name, dest_info in destinations.items():
                        token = dest_info.get('token')
                        chat_id = dest_info.get('chat_id')
                        
                        # If token exists but chat_id is empty, try to use the global chat_id
                        if token and not chat_id:
                            # Save the mapping using the global chat_id
                            if token not in self.token_chat_map:
                                self.token_chat_map[token] = self.default_chat_id
                                logger.info(f"Usando chat_id global {self.default_chat_id} para token {token[:8]}...")
            except json.JSONDecodeError:
                logger.error(f"Erro ao analisar notification_destinations em {section_name}")
                continue
                
        # Then, try to verify and discover chat IDs for each token
        self.discover_token_chat_ids()
                
    def discover_token_chat_ids(self):
        """
        Tenta descobrir automaticamente os chat IDs corretos para cada token 
        consultando a API do Telegram.
        """
        # Collect unique tokens that we need to verify
        tokens_to_check = set()
        
        # Add tokens from token_chat_map
        for token in self.token_chat_map.keys():
            if token != self.default_token:
                tokens_to_check.add(token)
                
        # For each token, try to get updates to identify chat_id
        for token in tokens_to_check:
            try:
                # Try to get recent updates for this bot
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                logger.info(f"Tentando descobrir chat_id para token {token[:8]}...")
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok') and data.get('result'):
                        # Look for chat_id in recent messages
                        for update in data['result']:
                            if 'message' in update and 'chat' in update['message']:
                                chat_id = str(update['message']['chat']['id'])
                                logger.info(f"Chat ID {chat_id} descoberto para token {token[:8]}...")
                                self.token_chat_map[token] = chat_id
                                break
            except Exception as e:
                logger.error(f"Erro ao tentar descobrir chat_id para token {token[:8]}: {e}")
                
        logger.info(f"Mapeamentos token->chat_id inicializados: {len(self.token_chat_map)} tokens mapeados")
        
    def get_token_info(self, token):
        """
        Obtém informações sobre o bot associado a um token específico.
        """
        if not token:
            return None
            
        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    return data['result']
            return None
        except Exception as e:
            logger.error(f"Erro ao obter informações do bot para token {token[:8]}: {e}")
            return None