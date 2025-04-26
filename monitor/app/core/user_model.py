import logging
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from datetime import datetime

logger = logging.getLogger('wegnots.user_model')

class UserModel:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client.wegnots
        self.collection: Collection = self.db['users']
        self._setup_indexes()
        self._ensure_central_server()
        self.processed_emails = set()

    def _setup_indexes(self):
        """Configura índices necessários"""
        # Garante índices únicos para email e chat_id
        self.collection.drop_indexes()
        self.collection.create_index([("email", ASCENDING)], unique=True)
        self.collection.create_index([("chat_id", ASCENDING)], unique=True)
        
        # Índice para busca por remetente nas regras
        self.collection.create_index([("notification_rules.sender", ASCENDING)])

    def _ensure_central_server(self):
        """Garante que o servidor central exista"""
        central_server = self.collection.find_one({'email': 'sooretama@megasec.com.br'})
        if not central_server:
            self.collection.insert_one({
                'name': 'WegNots Central',
                'email': 'sooretama@megasec.com.br',
                'chat_id': '1395823978',
                'is_central_server': True,
                'notification_rules': [],
                'is_active': True
            })
            logger.info('Servidor central criado com sucesso')

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
        is_central = email == 'sooretama@megasec.com.br'
        user = {
            "name": name,
            "email": email,
            "chat_id": chat_id,
            "is_central_server": is_central,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "notification_preferences": {
                "receive_criticals": True,
                "receive_moderates": True, 
                "receive_low": True
            },
            "notification_rules": []
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

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário pelo email"""
        return self.collection.find_one({'email': email})

    def get_users_by_email(self, email: str) -> List[Dict]:
        """Busca usuários que devem receber alertas do email informado"""
        # Busca direta pelo email
        users = list(self.collection.find({
            '$or': [
                {'email': email},  # Próprio usuário
                {'notification_rules.sender': email},  # Regras específicas
                {'notification_rules.sender': '*@' + email.split('@')[1]}  # Regras por domínio
            ]
        }))
        
        # Inclui servidor central se não estiver na lista
        central = self.collection.find_one({'is_central_server': True})
        if central and central not in users:
            users.append(central)
            
        return users

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

    def update_user_config(self, user_id: str, config_data: Dict) -> bool:
        """Atualiza as configurações de monitoramento do usuário"""
        try:
            result = self.collection.update_one(
                {"_id": user_id},
                {"$set": {
                    "imap_config": {
                        "check_interval": config_data.get("checkInterval", 60),
                        "server_address": config_data.get("serverAddress"),
                        "server_port": config_data.get("serverPort", 993),
                        "email_user": config_data.get("emailUser")
                    },
                    "notification_config": {
                        "telegram_enabled": config_data.get("telegramEnabled", True),
                        "telegram_chat_id": config_data.get("telegramChatId"),
                        "notifications_enabled": config_data.get("notificationsEnabled", True)
                    }
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações do usuário {user_id}: {e}")
            return False

    def update_notification_rules(self, chat_id: str, rules: List[Dict]) -> bool:
        """Atualiza regras de notificação do usuário"""
        try:
            self.collection.update_one(
                {'chat_id': chat_id},
                {'$set': {'notification_rules': rules}}
            )
            return True
        except Exception as e:
            logger.error(f'Erro ao atualizar regras: {e}')
            return False

    def get_central_server(self) -> Optional[Dict]:
        """Retorna o usuário servidor central"""
        return self.collection.find_one({'is_central_server': True})

    def set_user_active_status(self, chat_id: str, active: bool) -> bool:
        """Atualiza status de ativação do usuário"""
        try:
            self.collection.update_one(
                {'chat_id': chat_id},
                {'$set': {'is_active': active}}
            )
            return True
        except Exception as e:
            logger.error(f'Erro ao atualizar status: {e}')
            return False

    def get_all_users(self) -> List[Dict]:
        """Retorna todos os usuários ativos"""
        try:
            users = list(self.collection.find({'is_active': True}))
            logger.info(f"Encontrados {len(users)} usuários ativos")
            return users
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {e}")
            return []

    def save_processed_emails(self, db):
        """Salva o histórico de e-mails processados no MongoDB"""
        try:
            emails_collection = db['processed_emails']
            
            # Cria índice de expiração se não existir
            try:
                indexes = emails_collection.index_information()
                if 'processed_time_ttl' not in indexes:
                    emails_collection.create_index(
                        [("processed_time", ASCENDING)], 
                        expireAfterSeconds=7*24*60*60,  # 7 dias
                        name="processed_time_ttl"
                    )
                    logger.info("Índice TTL criado para histórico de e-mails")
            except Exception as e:
                logger.error(f"Erro ao criar índice TTL: {e}")
            
            # Converte o conjunto em lista de documentos
            email_docs = [
                {"email_id": email_id, "processed_time": datetime.utcnow()}
                for email_id in self.processed_emails
            ]
            
            if email_docs:
                # Usa bulk insert para maior eficiência
                result = emails_collection.insert_many(
                    email_docs, 
                    ordered=False  # Continua mesmo se alguns falharem (duplicados)
                )
                logger.info(f"Salvos {len(result.inserted_ids)} e-mails processados no MongoDB")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de e-mails: {e}")
            return False
    
    def load_processed_emails(self, db):
        """Carrega o histórico de e-mails processados do MongoDB"""
        try:
            emails_collection = db['processed_emails']
            
            # Busca e-mails processados nos últimos 3 dias
            three_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            three_days_ago = three_days_ago.replace(day=three_days_ago.day - 3)
            
            cursor = emails_collection.find(
                {"processed_time": {"$gte": three_days_ago}},
                {"email_id": 1}
            )
            
            # Adiciona ao conjunto em memória
            email_ids = {doc["email_id"] for doc in cursor}
            self.processed_emails.update(email_ids)
            
            logger.info(f"Carregados {len(email_ids)} e-mails processados do MongoDB")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar histórico de e-mails: {e}")
            return False
