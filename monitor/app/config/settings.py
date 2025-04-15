from dotenv import load_dotenv
import os
import sys
import logging
import importlib.util

# Carrega variáveis do arquivo .env
load_dotenv()

# Tenta importar o arquivo config.py global se ele existir
try:
    # Verifica se o config.py existe na raiz do projeto
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.py'))
    if os.path.exists(config_path):
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # Importa configurações do arquivo config.py
        if hasattr(config, 'IMAP_CONFIG'):
            root_imap_config = config.IMAP_CONFIG
        else:
            root_imap_config = {}
            
        if hasattr(config, 'TELEGRAM_CONFIG'):
            root_telegram_config = config.TELEGRAM_CONFIG
        else:
            root_telegram_config = {}
            
        if hasattr(config, 'LOG_CONFIG'):
            root_log_config = config.LOG_CONFIG
        else:
            root_log_config = {}
            
        if hasattr(config, 'ROCKETCHAT_CONFIG'):
            root_rocketchat_config = config.ROCKETCHAT_CONFIG
        else:
            root_rocketchat_config = {}
    else:
        root_imap_config = {}
        root_telegram_config = {}
        root_log_config = {}
        root_rocketchat_config = {}
except Exception as e:
    print(f"Erro ao importar configurações do config.py: {e}")
    root_imap_config = {}
    root_telegram_config = {}
    root_log_config = {}
    root_rocketchat_config = {}

# Configurações de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', root_log_config.get('level', 'INFO'))
LOG_FORMAT = os.getenv('LOG_FORMAT', root_log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
LOG_FILE = os.getenv('LOG_FILE', root_log_config.get('filename', 'wegnots.log'))

# Configurações IMAP
IMAP_CONFIG = {
    'server': os.getenv('IMAP_SERVER', root_imap_config.get('server', 'imap.titan.email')),
    'port': int(os.getenv('IMAP_PORT', root_imap_config.get('port', 993))),
    'username': os.getenv('IMAP_USER', root_imap_config.get('username', 'sooretama@megasec.com.br')),
    'password': os.getenv('IMAP_PASSWORD', root_imap_config.get('password', 'Megasec@2025')),
    'check_interval': int(os.getenv('CHECK_INTERVAL', root_imap_config.get('check_interval', 60))),
    'reconnect_attempts': int(os.getenv('RECONNECT_ATTEMPTS', root_imap_config.get('reconnect_attempts', 5))),
    'reconnect_delay': int(os.getenv('RECONNECT_DELAY', root_imap_config.get('reconnect_delay', 30))),
    'reconnect_backoff_factor': float(os.getenv('RECONNECT_BACKOFF_FACTOR', root_imap_config.get('reconnect_backoff_factor', 1.5)))
}

# Configurações Telegram
TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_TOKEN', root_telegram_config.get('bot_token', '8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E')),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID', root_telegram_config.get('chat_id', '1395823978')),
    'retry_attempts': int(os.getenv('TELEGRAM_RETRY_ATTEMPTS', root_telegram_config.get('retry_attempts', 3))),
    'retry_delay': int(os.getenv('TELEGRAM_RETRY_DELAY', root_telegram_config.get('retry_delay', 5)))
}

# Configurações Rocket.Chat
ROCKETCHAT_CONFIG = {
    'url': os.getenv('ROCKETCHAT_URL', root_rocketchat_config.get('url', '')),
    'user_id': os.getenv('ROCKETCHAT_USER_ID', root_rocketchat_config.get('user_id', '')),
    'token': os.getenv('ROCKETCHAT_TOKEN', root_rocketchat_config.get('token', '')),
    'channel': os.getenv('ROCKETCHAT_CHANNEL', root_rocketchat_config.get('channel', 'general')),
    'webhook_url': os.getenv('ROCKETCHAT_WEBHOOK_URL', root_rocketchat_config.get('webhook_url', '')),
    'retry_attempts': int(os.getenv('ROCKETCHAT_RETRY_ATTEMPTS', root_rocketchat_config.get('retry_attempts', 3))),
    'retry_delay': int(os.getenv('ROCKETCHAT_RETRY_DELAY', root_rocketchat_config.get('retry_delay', 5)))
}

# Validação de configurações críticas
def validate_config():
    """Valida configurações essenciais e emite avisos/erros quando necessário."""
    valid = True
    
    # Validar configurações IMAP
    if not IMAP_CONFIG['server'] or not IMAP_CONFIG['username'] or not IMAP_CONFIG['password']:
        logging.error("Configurações IMAP incompletas! Verifique o arquivo .env ou config.py.")
        valid = False
    
    # Validar configurações Telegram
    if not TELEGRAM_CONFIG['bot_token'] or not TELEGRAM_CONFIG['chat_id']:
        logging.error("Configurações do Telegram incompletas! Verifique o arquivo .env ou config.py.")
        valid = False
    
    # Validação opcional do Rocket.Chat
    if (ROCKETCHAT_CONFIG['url'] or ROCKETCHAT_CONFIG['webhook_url']):
        if ROCKETCHAT_CONFIG['webhook_url']:
            logging.info("Usando integração via Webhook para Rocket.Chat.")
        elif not (ROCKETCHAT_CONFIG['user_id'] and ROCKETCHAT_CONFIG['token']):
            logging.warning("Configurações da API REST do Rocket.Chat incompletas.")
            # Não falha a validação, já que Rocket.Chat é opcional
    
    if not valid:
        logging.warning("Aplicação pode não funcionar corretamente devido a configurações ausentes.")
    
    return valid

# Setup do logger principal
def setup_logging(level=None):
    """Configura o logger principal da aplicação."""
    if level is None:
        level = LOG_LEVEL
        
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
        
    handlers = [logging.StreamHandler()]
    
    # Adiciona handler de arquivo se especificado
    if LOG_FILE:
        try:
            handlers.append(logging.FileHandler(LOG_FILE))
        except (IOError, PermissionError) as e:
            print(f"Erro ao criar arquivo de log {LOG_FILE}: {e}")
            print("Logs serão direcionados apenas para o console.")
            
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=handlers
    )
    
    # Reduz verbosidade de logs de bibliotecas externas
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger('wegnots')
