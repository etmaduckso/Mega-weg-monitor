import os
import logging
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the root directory to Python path
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from config import IMAP_CONFIG, TELEGRAM_CONFIG, ROCKETCHAT_CONFIG

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de logging
LOG_CONFIG = {
    'level': 'DEBUG',  # Mantendo DEBUG para facilitar diagnóstico
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'wegnots.log'
}

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format'],
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_CONFIG['filename'])
        ]
    )
    return logging.getLogger('wegnots')

def validate_config():
    """Valida configurações necessárias"""
    required_configs = {
        'IMAP': ['server', 'port', 'username', 'password'],
        'TELEGRAM': ['bot_token', 'default_chat_id']
    }
    
    # Validate IMAP config
    for key in required_configs['IMAP']:
        if key not in IMAP_CONFIG or not IMAP_CONFIG[key]:
            logging.error(f"Configuração IMAP ausente: {key}")
            return False
            
    # Validate Telegram config
    for key in required_configs['TELEGRAM']:
        if key not in TELEGRAM_CONFIG or not TELEGRAM_CONFIG[key]:
            logging.error(f"Configuração Telegram ausente: {key}")
            return False
            
    return True

# Configurações do Banco de Dados
MONGODB_CONFIG = {
    'url': os.getenv('MONGODB_URL', 'mongodb://localhost:27017'),
    'database': os.getenv('MONGODB_DATABASE', 'wegnots')
}
