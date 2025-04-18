#!/usr/bin/env python3
"""
Script auxiliar para configurar roteamento do Telegram no WegNots.
Ajuda a obter chat_ids e testar configurações de roteamento.
"""

import os
import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from app.config.settings import TELEGRAM_CONFIG

# Configura logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    """Comando /start - Exibe mensagem inicial e instruções"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    message = (
        f"Olá {user.first_name}! 👋\n\n"
        f"Seu Chat ID é: `{chat_id}`\n\n"
        "Use este ID para configurar o roteamento de alertas no WegNots.\n\n"
        "Comandos disponíveis:\n"
        "/start - Exibe esta mensagem\n"
        "/test - Testa o recebimento de alertas\n"
        "/help - Exibe ajuda sobre configuração"
    )
    update.message.reply_text(message, parse_mode='Markdown')

def test(update, context):
    """Comando /test - Envia mensagem de teste simulando diferentes níveis de alerta"""
    chat_id = update.effective_chat.id
    
    # Simula um alerta de cada nível
    alerts = [
        ("⚠️ ALERTA CRÍTICO", "Teste de alerta crítico"),
        ("🔔 ALERTA MODERADO", "Teste de alerta moderado"),
        ("ℹ️ ALERTA LEVE", "Teste de alerta informativo")
    ]
    
    for alert_type, message in alerts:
        test_message = (
            f"{alert_type}\n"
            f"📌 Equipamento: TESTE-001\n"
            f"👤 Usuário: Sistema de Teste\n"
            f"💬 Mensagem: {message}\n"
            f"🆔 Chat ID: `{chat_id}`"
        )
        update.message.reply_text(test_message, parse_mode='Markdown')

def help_command(update, context):
    """Comando /help - Exibe instruções detalhadas de configuração"""
    help_text = (
        "📝 *Como configurar o roteamento de alertas:*\n\n"
        "1. Anote o Chat ID exibido no comando /start\n\n"
        "2. Configure no arquivo `config.py`:\n"
        "```python\n"
        "TELEGRAM_CONFIG = {\n"
        "    'route_mapping': {\n"
        "        'email@exemplo.com': ['seu_chat_id'],\n"
        "        '*@dominio.com': ['outro_chat_id']\n"
        "    },\n"
        "    'groups': {\n"
        "        'suporte': ['chat_id_1', 'chat_id_2']\n"
        "    }\n"
        "}\n"
        "```\n\n"
        "3. Ou via arquivo .env:\n"
        "```\n"
        "TELEGRAM_ROUTE_MAPPING={'email@exemplo.com':['seu_chat_id']}\n"
        "TELEGRAM_GROUPS={'suporte':['chat_id_1','chat_id_2']}\n"
        "```\n\n"
        "4. Use /test para verificar se está recebendo alertas"
    )
    update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Função principal do script de configuração"""
    try:
        # Cria o Updater com o token do bot
        updater = Updater(TELEGRAM_CONFIG['bot_token'], use_context=True)

        # Obtém o dispatcher para registrar handlers
        dp = updater.dispatcher

        # Registra os handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("test", test))
        dp.add_handler(CommandHandler("help", help_command))

        # Inicia o bot
        updater.start_polling()

        print("🤖 Bot de configuração iniciado!")
        print("1. Abra o Telegram e procure por seu bot")
        print("2. Digite /start para obter seu Chat ID")
        print("3. Use /test para verificar o recebimento de alertas")
        print("4. Use /help para ver instruções de configuração")
        print("\nPressione Ctrl+C para encerrar")

        # Mantém o bot rodando até Ctrl+C
        updater.idle()

    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
        print("\nVerifique se:")
        print("1. O token do bot está correto em config.py ou .env")
        print("2. Você tem conexão com a internet")
        print("3. As dependências estão instaladas (pip install python-telegram-bot==13.7)")

if __name__ == '__main__':
    main()