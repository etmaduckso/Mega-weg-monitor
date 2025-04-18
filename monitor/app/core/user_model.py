import logging
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from datetime import datetime

logger = logging.getLogger('wegnots.user_model')

class UserModel:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client.wegnots
        self.collection = self.db.users
        self._setup_indexes()

    def _setup_indexes(self):
        """Configura índices necessários"""
        # Garante índices únicos para email e chat_id
        self.collection.drop_indexes()
        self.collection.create_index([("email", ASCENDING)], unique=True)
        self.collection.create_index([("chat_id", ASCENDING)], unique=True)
        
        # Índice para busca por remetente nas regras
        self.collection.create_index([("notification_rules.sender", ASCENDING)])

    def create_user(self, name: str, email: str, chat_id: str) -> Dict:
        """
        Cria um novo usuário no sistema.
        
        Args:
            name: Nome completo do usuário
            email: Email do usuário
            chat_id: ID do chat do Telegram
            
        Returns:
            Dict com os dados do usuário criado
        """
        user = {
            "name": name,
            "email": email,
            "chat_id": chat_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "notification_preferences": {
                "receive_criticals": True,
                "receive_moderates": True, 
                "receive_low": True
            }
        }

        try:
            result = self.collection.insert_one(user)
            user['_id'] = result.inserted_id
            logger.info(f"Usuário criado com sucesso: {name} ({email})")
            return user
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise

    def get_user_by_chat_id(self, chat_id: str) -> Optional[Dict]:
        """Busca usuário pelo chat_id do Telegram"""
        return self.collection.find_one({"chat_id": chat_id})

    def get_users_by_email(self, email: str) -> List[Dict]:
        """Busca usuários pelo email cadastrado"""
        return list(self.collection.find({"email": email, "is_active": True}))

    def get_active_chat_ids(self) -> List[str]:
        """Retorna lista de chat_ids de usuários ativos"""
        users = self.collection.find({"is_active": True}, {"chat_id": 1})
        return [user['chat_id'] for user in users]

    def update_user(self, user_id, update_data: Dict) -> bool:
        """
        Atualiza dados do usuário.
        
        Args:
            user_id: ID do usuário no MongoDB
            update_data: Dicionário com campos a atualizar
            
        Returns:
            bool indicando sucesso da operação
        """
        try:
            result = self.collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {user_id}: {e}")
            return False

    def deactivate_user(self, chat_id: str) -> bool:
        """Desativa um usuário pelo chat_id"""
        try:
            result = self.collection.update_one(
                {"chat_id": chat_id},
                {"$set": {"is_active": False}}
            )
            if result.modified_count > 0:
                logger.info(f"Usuário desativado: {chat_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao desativar usuário {chat_id}: {e}")
            return False
