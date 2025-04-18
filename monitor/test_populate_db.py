#!/usr/bin/env python3
"""
Script para popular o banco de dados com usuários de teste
"""

from pymongo import MongoClient
import logging
from datetime import datetime

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dados de teste
TEST_USERS = [
    {
        "name": "Lake Silva",
        "email": "lake.silva@megasec.com.br",
        "chat_id": "1395823978",
        "is_active": True,
        "created_at": datetime.now(),
        "notification_preferences": {
            "receive_criticals": True,
            "receive_moderates": True,
            "receive_low": True,
            "quiet_hours_start": None,
            "quiet_hours_end": None
        }
    },
    {
        "name": "Test User",
        "email": "test.user@megasec.com.br",
        "chat_id": "987654321",
        "is_active": True,
        "created_at": datetime.now(),
        "notification_preferences": {
            "receive_criticals": True,
            "receive_moderates": True,
            "receive_low": False,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00"
        }
    }
]

def main():
    try:
        # Conecta ao MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["wegnots"]
        users_collection = db["users"]

        # Remove índices existentes
        users_collection.drop_indexes()
        logger.info("Índices removidos com sucesso")

        # Cria novos índices únicos
        users_collection.create_index("email", unique=True)
        users_collection.create_index("chat_id", unique=True)
        logger.info("Novos índices criados com sucesso")
        
        # Limpa a coleção antes de inserir
        users_collection.delete_many({})
        logger.info("Coleção de usuários limpa com sucesso")

        # Insere usuários de teste
        for user in TEST_USERS:
            try:
                result = users_collection.insert_one(user)
                logger.info(f"Usuário {user['name']} inserido com sucesso (ID: {result.inserted_id})")
            except Exception as e:
                logger.error(f"Erro ao inserir usuário {user['name']}: {e}")

        # Verifica os usuários inseridos
        total_users = users_collection.count_documents({})
        logger.info(f"\nTotal de usuários cadastrados: {total_users}")

        print("\n=== Usuários cadastrados ===")
        for user in users_collection.find():
            print(f"\nNome: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Chat ID: {user['chat_id']}")
            print(f"Status: {'Ativo' if user['is_active'] else 'Inativo'}")
            print("Preferências de notificação:")
            prefs = user['notification_preferences']
            print(f"- Alertas críticos: {'Sim' if prefs['receive_criticals'] else 'Não'}")
            print(f"- Alertas moderados: {'Sim' if prefs['receive_moderates'] else 'Não'}")
            print(f"- Alertas leves: {'Sim' if prefs['receive_low'] else 'Não'}")
            if prefs['quiet_hours_start'] and prefs['quiet_hours_end']:
                print(f"- Horário silencioso: {prefs['quiet_hours_start']} - {prefs['quiet_hours_end']}")
            print("-" * 30)

    except Exception as e:
        logger.error(f"Erro ao conectar ao MongoDB: {e}")

if __name__ == "__main__":
    main()