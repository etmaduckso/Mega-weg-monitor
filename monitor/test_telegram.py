#!/usr/bin/env python3
"""
Script para testar a comunicação com o bot do Telegram.
Este script verifica se o token e chat ID configurados estão funcionando corretamente.
"""

import requests
import configparser
from datetime import datetime

def load_config():
    """Carrega as configurações do arquivo config.ini"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    telegram_config = {
        'token': config['TELEGRAM']['token'],
        'chat_id': config['TELEGRAM']['chat_id']
    }
    
    return telegram_config

def test_send_message(token, chat_id, message):
    """Testa o envio de uma mensagem simples para o Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    print(f"Enviando mensagem para chat_id: {chat_id}")
    print(f"Usando token: {token}")
    
    try:
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False

def test_get_bot_info(token):
    """Obtém informações sobre o bot para verificar se o token é válido"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Informações do bot: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao obter informações do bot: {e}")
        return False

def main():
    # Carrega configurações
    config = load_config()
    token = config['token']
    chat_id = config['chat_id']
    
    print("==== Teste de Comunicação com Bot do Telegram ====")
    print(f"Data e hora: {datetime.now()}")
    
    # Teste 1: Verificar informações do bot
    print("\n1. Verificando informações do bot (token válido)...")
    test_get_bot_info(token)
    
    # Teste 2: Enviar mensagem simples
    print("\n2. Enviando mensagem de teste...")
    test_send_message(token, chat_id, f"*TESTE WEGNOTS*\n\nMensagem de teste enviada em {datetime.now()}")
    
    # Teste 3: Enviar mensagem formatada (similar ao alerta real)
    print("\n3. Enviando mensagem formatada (similar ao alerta real)...")
    message = (
        f"*TESTE DE ALERTA*\n\n"
        f"📧 *De:* teste@exemplo.com\n"
        f"📝 *Assunto:* Teste de Alerta do WegNots\n"
        f"⏰ *Data:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        f"```\nEste é um teste do sistema de alertas do WegNots.\n```"
    )
    test_send_message(token, chat_id, message)

if __name__ == "__main__":
    main()