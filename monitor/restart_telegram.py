#!/usr/bin/env python3
"""
Script para reiniciar o bot do Telegram
"""
import logging
from pymongo import MongoClient
from app.core.user_model import UserModel
from app.core.telegram_client import TelegramClient
from app.config.settings import setup_logging

# Configura o logger
logger = setup_logging()

def main():
    try:
        # Inicializa MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client.wegnots
        
        # Inicializa UserModel e TelegramClient
        user_model = UserModel(db)
        telegram_client = TelegramClient(user_model)
        
        # Reinicia o bot
        telegram_client.restart_bot()
        
        logger.info("Bot do Telegram reiniciado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao reiniciar bot: {e}")
        raise

if __name__ == "__main__":
    main()