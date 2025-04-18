#!/usr/bin/env python3
"""
Script para verificar os dados salvos no MongoDB
"""

from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Conecta ao MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["wegnots"]
        users_collection = db["users"]
        
        # Lista todos os usuários
        print("\n=== Usuários Cadastrados ===")
        users = list(users_collection.find())
        
        if not users:
            print("Nenhum usuário encontrado no banco de dados!")
            return
            
        for user in users:
            print("\nDados do usuário:")
            print(f"Nome: {user.get('name')}")
            print(f"Email: {user.get('email')}")
            print(f"Chat ID: {user.get('chat_id')}")
            print(f"Status: {'Ativo' if user.get('is_active', True) else 'Inativo'}")
            print("-" * 30)
        
        # Estatísticas
        total_users = len(users)
        total_active = sum(1 for user in users if user.get('is_active', True))
        
        print(f"\nTotal de usuários cadastrados: {total_users}")
        print(f"Usuários ativos: {total_active}")
        print(f"Usuários inativos: {total_users - total_active}")
        
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")

if __name__ == "__main__":
    main()