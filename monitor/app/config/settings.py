import os
import logging
import configparser
from typing import Dict, Tuple

def setup_logging():
    """Configura o logger principal do sistema"""
    logger = logging.getLogger('wegnots')
    logger.setLevel(logging.INFO)
    
    # Handler para console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # Handler para arquivo
    file_handler = logging.FileHandler('logs/wegnots.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def load_config() -> Dict:
    """Carrega configurações do arquivo config.ini"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    config.read(config_path)
    
    # Configurações IMAP primário
    imap_primary = {
        'server': config.get('IMAP_PRIMARY', 'server'),
        'port': config.getint('IMAP_PRIMARY', 'port'),
        'username': config.get('IMAP_PRIMARY', 'username'),
        'password': config.get('IMAP_PRIMARY', 'password'),
        'is_active': config.getboolean('IMAP_PRIMARY', 'is_active'),
        'check_interval': 60,
        'reconnect_attempts': 5,
        'reconnect_delay': 30,
        'reconnect_backoff_factor': 1.5
    }
    
    # Configurações IMAP secundário
    imap_secondary = {
        'server': config.get('IMAP_SECONDARY', 'server'),
        'port': config.getint('IMAP_SECONDARY', 'port'),
        'username': config.get('IMAP_SECONDARY', 'username'),
        'password': config.get('IMAP_SECONDARY', 'password'),
        'is_active': config.getboolean('IMAP_SECONDARY', 'is_active'),
        'check_interval': 60,
        'reconnect_attempts': 5,
        'reconnect_delay': 30,
        'reconnect_backoff_factor': 1.5
    }
    
    # Configurações Telegram
    telegram = {
        'token': config.get('TELEGRAM', 'token'),
        'chat_id': config.get('TELEGRAM', 'chat_id')
    }
    
    return {
        'imap_primary': imap_primary,
        'imap_secondary': imap_secondary,
        'telegram': telegram
    }

def validate_config(config: Dict) -> Tuple[bool, str]:
    """Valida as configurações carregadas"""
    # Verifica se pelo menos um servidor IMAP está ativo
    if not (config['imap_primary']['is_active'] or config['imap_secondary']['is_active']):
        return False, "Nenhum servidor IMAP ativo configurado"
    
    # Valida configurações de cada servidor IMAP ativo
    for imap_config in [config['imap_primary'], config['imap_secondary']]:
        if imap_config['is_active']:
            if not imap_config['server']:
                return False, "Servidor IMAP não configurado"
            if not imap_config['username']:
                return False, "Usuário IMAP não configurado"
            if not imap_config['password']:
                return False, "Senha IMAP não configurada"
    
    # Valida configurações do Telegram
    if not config['telegram']['token']:
        return False, "Token do Telegram não configurado"
    if not config['telegram']['chat_id']:
        return False, "Chat ID do Telegram não configurado"
    
    return True, "Configurações válidas"

# Carrega configurações ao importar o módulo
try:
    CONFIG = load_config()
    IMAP_PRIMARY_CONFIG = CONFIG['imap_primary']
    IMAP_SECONDARY_CONFIG = CONFIG['imap_secondary']
    TELEGRAM_CONFIG = CONFIG['telegram']
except Exception as e:
    logger = setup_logging()
    logger.critical(f"Erro ao carregar configurações: {e}")
    raise