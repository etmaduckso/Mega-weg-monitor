#!/usr/bin/env python3
"""
Script para testar a configuração específica do Leobot para sooretama1@megasec.com.br
"""

import configparser
import requests
import logging
import sys
from datetime import datetime

# Configura o logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leobot_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('wegnots.leobot_test')

def load_config():
    """Carrega configurações específicas para sooretama1@megasec.com.br"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    section_name = 'IMAP_sooretama1@megasec.com.br'
    if section_name not in config:
        logger.error(f"Seção {section_name} não encontrada no config.ini")
        return None
        
    return {
        'username': config[section_name]['username'],
        'telegram_token': config[section_name]['telegram_token'],
        'telegram_chat_id': config[section_name]['telegram_chat_id']
    }

def test_telegram_config(username, token, chat_id):
    """Testa se a configuração do Telegram está correta"""
    logger.info(f"Testando configuração para {username}")
    logger.info(f"Token: {token}")
    logger.info(f"Chat ID: {chat_id}")
    
    # Primeiro, verifica se o token do bot é válido
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            bot_info = response.json()['result']
            logger.info(f"Bot verificado: {bot_info['first_name']} (@{bot_info.get('username', 'sem username')})")
        else:
            logger.error(f"Falha ao verificar bot: Status {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro ao verificar bot: {e}")
        return False
        
    # Agora, envia uma mensagem de teste
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message = (
        f"🔍 *TESTE DE CONFIGURAÇÃO*\n\n"
        f"📧 *Conta:* {username}\n"
        f"⏰ *Data:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        f"Este é um teste para verificar se a configuração do Leobot está correta.\n"
        f"Se você está vendo esta mensagem, significa que sua configuração está funcionando!"
    )
    
    try:
        logger.info(f"Enviando mensagem de teste para chat_id {chat_id}")
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Mensagem enviada com sucesso!")
            return True
        else:
            logger.error(f"❌ Falha ao enviar mensagem: Status {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {e}")
        return False

def main():
    logger.info("=" * 60)
    logger.info(f"Iniciando teste de configuração do Leobot em {datetime.now()}")
    logger.info("=" * 60)
    
    config = load_config()
    if not config:
        logger.error("Falha ao carregar configuração")
        return 1
        
    success = test_telegram_config(
        username=config['username'],
        token=config['telegram_token'],
        chat_id=config['telegram_chat_id']
    )
    
    logger.info("=" * 60)
    if success:
        logger.info("✅ Teste concluído com sucesso!")
    else:
        logger.error("❌ Teste falhou, verifique os erros acima.")
    logger.info("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())