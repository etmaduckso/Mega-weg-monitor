import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações Base
BASE_DIR = Path(__file__).resolve().parent.parent

class ConfigurationError(Exception):
    """Exceção para erros de configuração."""
    pass

def get_env_var(var_name: str, default: Any = None, required: bool = True) -> Any:
    """
    Recupera variável de ambiente com validação.
    
    Args:
        var_name: Nome da variável de ambiente
        default: Valor padrão caso não encontrada
        required: Se True, levanta exceção quando não encontrada
    """
    value = os.getenv(var_name, default)
    if value is None and required:
        raise ConfigurationError(f"Variável de ambiente obrigatória não encontrada: {var_name}")
    return value

def parse_json_env(var_name: str, default: Dict = None) -> Dict:
    """
    Parse JSON string from environment variable.
    
    Args:
        var_name: Nome da variável de ambiente
        default: Valor padrão caso parsing falhe
    """
    try:
        value = get_env_var(var_name, required=False)
        return json.loads(value) if value else (default or {})
    except json.JSONDecodeError:
        if default is not None:
            return default
        raise ConfigurationError(f"Erro ao fazer parse do JSON em {var_name}")

# Configurações IMAP
IMAP_CONFIG = {
    'server': get_env_var('IMAP_SERVER'),
    'port': int(get_env_var('IMAP_PORT', 993)),
    'username': get_env_var('IMAP_USER'),
    'password': get_env_var('IMAP_PASSWORD'),
}

# Configurações Telegram
TELEGRAM_CONFIG = {
    'token': get_env_var('TELEGRAM_TOKEN'),
    'chat_id': get_env_var('TELEGRAM_CHAT_ID'),
}

# Configurações de Monitoramento
MONITOR_CONFIG = {
    'check_interval': int(get_env_var('CHECK_INTERVAL', 60)),
    'reconnect_attempts': int(get_env_var('RECONNECT_ATTEMPTS', 5)),
    'reconnect_delay': int(get_env_var('RECONNECT_DELAY', 30)),
    'reconnect_backoff_factor': float(get_env_var('RECONNECT_BACKOFF_FACTOR', 1.5)),
}

# Configurações de Logging
LOG_CONFIG = {
    'level': get_env_var('LOG_LEVEL', 'INFO'),
    'format': get_env_var('LOG_FORMAT', 
                         '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    'max_size': int(get_env_var('MAX_LOG_SIZE', 10485760)),  # 10MB
    'backup_count': int(get_env_var('LOG_BACKUP_COUNT', 3)),
}

# Configurações de Notificação
NOTIFICATION_DESTINATIONS = parse_json_env('NOTIFICATION_DESTINATIONS', {})

def validate_config() -> None:
    """
    Valida todas as configurações necessárias.
    Levanta ConfigurationError se encontrar problemas.
    """
    # Valida configurações IMAP
    if not all([
        IMAP_CONFIG['server'],
        IMAP_CONFIG['username'],
        IMAP_CONFIG['password']
    ]):
        raise ConfigurationError("Configurações IMAP incompletas")

    # Valida configurações Telegram
    if not all([
        TELEGRAM_CONFIG['token'],
        TELEGRAM_CONFIG['chat_id']
    ]):
        raise ConfigurationError("Configurações Telegram incompletas")

    # Valida valores numéricos
    if not all([
        isinstance(MONITOR_CONFIG['check_interval'], int),
        isinstance(MONITOR_CONFIG['reconnect_attempts'], int),
        isinstance(MONITOR_CONFIG['reconnect_delay'], int),
        isinstance(MONITOR_CONFIG['reconnect_backoff_factor'], float)
    ]):
        raise ConfigurationError("Valores inválidos nas configurações de monitoramento")

    # Valida configurações de log
    if not all([
        isinstance(LOG_CONFIG['max_size'], int),
        isinstance(LOG_CONFIG['backup_count'], int)
    ]):
        raise ConfigurationError("Valores inválidos nas configurações de log")

# Executa validação na importação
try:
    validate_config()
except ConfigurationError as e:
    print(f"ERRO DE CONFIGURAÇÃO: {e}")
    raise
