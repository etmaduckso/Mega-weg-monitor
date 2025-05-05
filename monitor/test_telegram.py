#!/usr/bin/env python3
"""
Script de teste para enviar mensagens ao Telegram usando as configurações do WegNots
"""

import configparser
import sys
import os
import logging
from datetime import datetime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('telegram_test')

def load_config():
    """Carrega configurações do arquivo config.ini"""
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    config.read(config_path)
    
    if 'TELEGRAM' not in config:
        logger.error("Seção TELEGRAM não encontrada em config.ini")
        return None
    
    return config

def send_test_message(token, chat_id, message):
    """Envia mensagem de teste para o Telegram usando requests"""
    import requests
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        logger.info(f"Enviando mensagem para chat_id {chat_id} usando token {token[:10]}...")
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Mensagem enviada com sucesso! Status: {response.status_code}")
            logger.info(f"Resposta: {response.json()}")
            return True
        else:
            logger.error(f"Falha ao enviar mensagem. Status: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== Teste de Envio de Mensagens para o Telegram ===")
    
    # Carrega configurações
    config = load_config()
    if not config:
        logger.error("Não foi possível carregar as configurações.")
        return 1
    
    # Teste 1: Configuração global do Telegram
    logger.info("\nTESTE 1: Usando configuração global do Telegram")
    if 'TELEGRAM' in config and config['TELEGRAM'].get('token') and config['TELEGRAM'].get('chat_id'):
        token = config['TELEGRAM'].get('token')
        chat_id = config['TELEGRAM'].get('chat_id')
        message = (
            "🧪 *TESTE DE MENSAGEM - WegNots Monitor*\n\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "✅ Este é um teste da configuração global do Telegram.\n"
            "🔍 Se você está vendo esta mensagem, a configuração global está funcionando!"
        )
        
        success = send_test_message(token, chat_id, message)
        if not success:
            logger.error("Falha no teste da configuração global.")
    else:
        logger.warning("Configuração global do Telegram não encontrada ou incompleta.")
    
    # Teste 2: Configuração da conta sooretama@megasec.com.br
    logger.info("\nTESTE 2: Usando configuração da conta sooretama@megasec.com.br")
    section = "IMAP_sooretama@megasec.com.br"
    if section in config and config[section].get('telegram_token') and config[section].get('telegram_chat_id'):
        token = config[section].get('telegram_token')
        chat_id = config[section].get('telegram_chat_id')
        message = (
            "🧪 *TESTE DE MENSAGEM - WegNots Monitor*\n\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "✅ Este é um teste da configuração de sooretama@megasec.com.br.\n"
            "🔍 Se você está vendo esta mensagem, a configuração está funcionando!"
        )
        
        success = send_test_message(token, chat_id, message)
        if not success:
            logger.error(f"Falha no teste da configuração de {section}.")
    else:
        logger.warning(f"Configuração de {section} não encontrada ou incompleta.")
    
    # Teste 3: Configuração da conta sooretama1@megasec.com.br
    logger.info("\nTESTE 3: Usando configuração da conta sooretama1@megasec.com.br")
    section = "IMAP_sooretama1@megasec.com.br"
    if section in config and config[section].get('telegram_token') and config[section].get('telegram_chat_id'):
        token = config[section].get('telegram_token')
        chat_id = config[section].get('telegram_chat_id')
        message = (
            "🧪 *TESTE DE MENSAGEM - WegNots Monitor*\n\n"
            f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "✅ Este é um teste da configuração de sooretama1@megasec.com.br.\n"
            "🔍 Se você está vendo esta mensagem, a configuração está funcionando!"
        )
        
        success = send_test_message(token, chat_id, message)
        if not success:
            logger.error(f"Falha no teste da configuração de {section}.")
    else:
        logger.warning(f"Configuração de {section} não encontrada ou incompleta.")
    
    logger.info("\n=== Teste concluído ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())