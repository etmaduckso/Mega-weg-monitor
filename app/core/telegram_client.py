import requests
import logging
import time
from app.config.settings import TELEGRAM_CONFIG

# Configura o logger para este módulo
logger = logging.getLogger('wegnots.telegram_client')

class TelegramClient:
    """
    Cliente para envio de alertas via Telegram.
    
    Fornece funcionalidades para enviar mensagens formatadas para um chat
    específico, com suporte a tratamento de erros e tentativas automáticas
    de reenvio em caso de falha.
    """
    
    def __init__(self):
        """
        Inicializa o cliente Telegram com as configurações definidas.
        """
        # Utiliza bot_token se disponível, senão tenta token para compatibilidade
        self.bot_token = TELEGRAM_CONFIG.get('bot_token', TELEGRAM_CONFIG.get('token', ''))
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.retry_attempts = TELEGRAM_CONFIG.get('retry_attempts', 3)
        self.retry_delay = TELEGRAM_CONFIG.get('retry_delay', 5)
        logger.debug(f"TelegramClient inicializado para chat_id {self.chat_id}")

    def send_alert(self, equipment_id, alert_type, user, extra_info=None):
        """
        Envia um alerta via Telegram.
        
        Implementa uma estratégia de retry para garantir a entrega mesmo 
        em caso de problemas temporários de conexão.
        
        Args:
            equipment_id (str): Identificador do equipamento
            alert_type (int): Tipo do alerta (1=CRÍTICO, 2=MODERADO, 3=LEVE)
            user (str): Nome do usuário relacionado ao alerta
            extra_info (dict, optional): Informações adicionais para o alerta
            
        Returns:
            bool: True se o envio foi bem-sucedido, False caso contrário
        """
        message = self._format_message(equipment_id, alert_type, user, extra_info)
        logger.debug(f"Mensagem formatada para envio via Telegram:\n{message}")
        url = f"{self.base_url}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        # Implementa lógica de retry
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                logger.debug(f"Tentativa {attempts+1}/{self.retry_attempts} de envio de alerta via Telegram")
                response = requests.post(url, data=params, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        logger.info(f"Alerta enviado com sucesso para {equipment_id}")
                        return True
                    else:
                        error = result.get('description', 'Erro desconhecido')
                        logger.warning(f"API do Telegram retornou erro: {error}")
                logger.warning(f"Falha no envio do alerta. Status: {response.status_code}, Response: {response.text}")
                
            except requests.RequestException as e:
                logger.error(f"Erro de requisição ao Telegram: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao enviar alerta: {e}")
            
            # Prepara próxima tentativa
            attempts += 1
            if attempts < self.retry_attempts:
                logger.info(f"Aguardando {self.retry_delay}s antes de tentar novamente")
                time.sleep(self.retry_delay)
        
        logger.error(f"Falha no envio do alerta após {self.retry_attempts} tentativas")
        return False

    def _format_message(self, equipment_id, alert_type, user, extra_info=None):
        """
        Formata a mensagem de alerta para o Telegram.
        
        Args:
            equipment_id (str): Identificador do equipamento
            alert_type (int): Tipo do alerta (1=CRÍTICO, 2=MODERADO, 3=LEVE)
            user (str): Nome do usuário relacionado ao alerta
            extra_info (dict, optional): Informações adicionais para o alerta
            
        Returns:
            str: Mensagem formatada em Markdown
        """
        alert_types = {
            1: "⚠️ ALERTA CRÍTICO",
            2: "🔔 ALERTA MODERADO",
            3: "ℹ️ ALERTA LEVE"
        }
        
        # Formata a data para o padrão desejado
        formatted_date = time.strftime("%d/%m/%Y %H:%M:%S")
        
        # Constrói a mensagem básica no formato preferido
        message = f"{alert_types.get(alert_type, 'ALERTA DESCONHECIDO')}\n"
        message += f"📌 Equipamento: {equipment_id}\n"
        message += f"👤 Usuário: {user}\n"
        message += f"⏰ Data: {formatted_date}\n\n"
        message += "Detalhes adicionais:\n"
        
        # Adiciona informações extras no formato preferido
        if extra_info and isinstance(extra_info, dict):
            # Mapeia as chaves para os nomes preferidos
            key_map = {
                'subject': 'Assunto',
                'from': 'Remetente',
                'date': 'Data'
            }
            for key in ['subject', 'from', 'date']:
                if key in extra_info:
                    message += f"- {key_map.get(key, key)}: {extra_info[key]}\n"
        return message
    
    def send_text_message(self, text):
        """
        Envia uma mensagem simples de texto.
        
        Útil para notificações do sistema, logs ou mensagens informativas
        que não seguem o formato padrão de alerta.
        
        Args:
            text (str): Texto da mensagem
            
        Returns:
            bool: True se o envio foi bem-sucedido, False caso contrário
        """
        url = f"{self.base_url}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                logger.debug("Enviando mensagem de texto simples")
                response = requests.post(url, data=params, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        return True
                    
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem: {e}")
            
            attempts += 1
            if attempts < self.retry_attempts:
                time.sleep(self.retry_delay)
        
        return False
