import imaplib
import email
import time
import logging
from email.header import decode_header
from app.config.settings import IMAP_CONFIG, setup_logging
from app.core.telegram_client import TelegramClient  # Import TelegramClient
from .notification_client import NotificationClient

# Configura o logger para este módulo
logger = logging.getLogger('wegnots.email_handler')

class EmailHandler:
    """
    Gerencia a conexão IMAP, verificação de novos e-mails e parsing das mensagens.
    
    Implementa estratégias de reconexão automática e tratamento de erros robusto
    para garantir a continuidade do serviço mesmo em caso de instabilidades na rede
    ou no servidor de e-mail.
    """
    
    def __init__(self, notification_clients: list[NotificationClient]):
        """
        Inicializa o handler de e-mail com as configurações do IMAP.
        Não estabelece conexão no construtor para permitir tratamento de erros
        mais controlado no método connect().
        Adiciona suporte a múltiplos clientes de notificação.
        """
        self.mail = None
        self.username = IMAP_CONFIG['username']
        self.password = IMAP_CONFIG['password']
        self.server = IMAP_CONFIG['server']
        self.port = IMAP_CONFIG['port']
        self.reconnect_attempts = IMAP_CONFIG['reconnect_attempts']
        self.reconnect_delay = IMAP_CONFIG['reconnect_delay']
        self.backoff_factor = IMAP_CONFIG['reconnect_backoff_factor']
        self.connected = False
        self.processed_email_ids = set()  # Set to keep track of processed email IDs
        self.telegram_client = None
        self.notification_clients = notification_clients
        logger.debug(f"EmailHandler inicializado para servidor {self.server}:{self.port}")

    def _create_connection(self):
        """
        Cria uma nova conexão IMAP_SSL. Método interno para encapsular 
        a criação de conexão, facilitando a reconexão quando necessário.
        
        Returns:
            imaplib.IMAP4_SSL: Objeto de conexão IMAP
        """
        try:
            logger.debug(f"Criando conexão IMAP com {self.server}:{self.port}")
            return imaplib.IMAP4_SSL(self.server, self.port)
        except Exception as e:
            logger.error(f"Erro ao criar conexão IMAP: {e}")
            raise

    def connect(self):
        """
        Conecta ao servidor IMAP com estratégia de reconexão automática.
        
        Returns:
            bool: True se a conexão foi estabelecida com sucesso, False caso contrário
        """
        if self.connected and self.mail:
            try:
                # Verify if connection is still alive
                status, _ = self.mail.noop()
                if status == 'OK':
                    return True
            except:
                self.connected = False
                self.mail = None
                
        attempt = 0
        current_delay = self.reconnect_delay
        
        while attempt < self.reconnect_attempts:
            try:
                # Create a new connection if needed
                if not self.mail:
                    self.mail = self._create_connection()
                
                # Try to authenticate
                logger.info(f"Tentativa {attempt+1}/{self.reconnect_attempts} de login no IMAP")
                status, response = self.mail.login(self.username, self.password)
                
                if status != 'OK':
                    logger.warning(f"Falha na autenticação IMAP: {response}")
                    self.connected = False
                    return False
                    
                logger.info("Login IMAP bem-sucedido")
                self.mail.select('INBOX')
                self.connected = True
                return True
                    
            except Exception as e:
                logger.error(f"Erro na conexão IMAP: {e}")
                self.mail = None
                
            attempt += 1
            if attempt < self.reconnect_attempts:
                logger.info(f"Aguardando {current_delay}s antes da próxima tentativa")
                time.sleep(current_delay)
                current_delay *= self.backoff_factor
        
        self.connected = False
        logger.critical(f"Todas as {self.reconnect_attempts} tentativas de conexão IMAP falharam!")
        return False

    def ensure_connection(self):
        """
        Verifica se a conexão está ativa e tenta reconectar se necessário.
        
        Returns:
            bool: True se a conexão está ativa ou foi restaurada, False caso contrário
        """
        if self.connected and self.mail:
            try:
                # Verifica se a conexão está ativa com uma operação simples
                status, _ = self.mail.noop()
                if status == 'OK':
                    return True
            except Exception:
                logger.warning("Conexão IMAP perdida, tentando reconectar...")
                self.connected = False
                self.mail = None
        
        return self.connect()

    def check_new_emails(self):
        """
        Verifica novos e-mails não lidos na caixa de entrada.
        
        Garante que a conexão está ativa antes de tentar a operação.
        
        Returns:
            list: Lista de IDs de e-mails não lidos, vazia se houver erro ou nenhum novo e-mail
        """
        if not self.ensure_connection():
            logger.error("Impossível verificar novos e-mails: sem conexão")
            return []
            
        try:
            logger.debug("Verificando novos e-mails...")
            status, messages = self.mail.search(None, '(UNSEEN)')
            
            if status == 'OK':
                email_ids = messages[0].split()
                new_email_ids = [email_id for email_id in email_ids if email_id.decode() not in self.processed_email_ids]
                
                if new_email_ids:
                    logger.info(f"Encontrados {len(new_email_ids)} novos e-mails")
                    for email_id in new_email_ids:
                        msg = self.parse_email(email_id)
                        if msg:
                            email_data = self.extract_email_data(msg)
                            # Send notification to all clients
                            self.notify_clients(email_data)
                            self.processed_email_ids.add(email_id.decode())
                            logger.debug(f"E-mail {email_id.decode()} marcado como processado")
                return new_email_ids
            else:
                logger.warning(f"Falha ao buscar e-mails: {status}")
        except Exception as e:
            logger.error(f"Erro ao verificar novos e-mails: {e}")
            self.connected = False  # Marca como desconectado para forçar reconexão
        
        return []

    def notify_clients(self, email_data):
        """
        Envia notificações para todos os clientes configurados.
        """
        for client in self.notification_clients:
            try:
                client.send_alert(
                    equipment_id="WEG-MONITOR-001",
                    alert_type=3,  # Exemplo de alerta leve
                    user="Sistema WegNots",
                    extra_info=email_data
                )
            except Exception as e:
                logger.error(f"Erro ao notificar cliente {client.__class__.__name__}: {e}")

    def parse_email(self, email_id):
        """
        Recupera e faz parsing de um e-mail pelo seu ID.
        
        Args:
            email_id: ID do e-mail a ser recuperado
            
        Returns:
            email.message.Message: Objeto de mensagem de e-mail, ou None em caso de erro
        """
        if not self.ensure_connection():
            logger.error(f"Impossível obter e-mail {email_id}: sem conexão")
            return None
            
        try:
            if isinstance(email_id, bytes):
                email_id = email_id.decode()
            logger.debug(f"Buscando conteúdo do e-mail {email_id}")
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            
            if status == 'OK' and msg_data and msg_data[0]:
                logger.debug(f"E-mail {email_id} obtido com sucesso")
                return email.message_from_bytes(msg_data[0][1])
            else:
                logger.warning(f"Falha ao obter dados do e-mail {email_id}")
        except Exception as e:
            logger.error(f"Erro ao fazer parsing do e-mail {email_id}: {e}")
            
        return None

    def extract_email_data(self, msg):
        """
        Extrai informações relevantes de um e-mail.
        
        Args:
            msg: Objeto de mensagem de e-mail
            
        Returns:
            dict: Dicionário com os dados relevantes do e-mail
        """
        if not msg:
            logger.warning("Tentativa de extrair dados de uma mensagem nula")
            return None
            
        try:
            # Extrai cabeçalhos básicos
            subject = decode_header(msg.get('Subject', ''))
            subject = subject[0][0]
            try:
                if isinstance(subject, bytes):
                    subject = subject.decode(errors='replace')
            except Exception as e:
                logger.error(f"Erro ao decodificar o assunto do e-mail: {e}")
                subject = "(Assunto não disponível)"
                
            sender = msg.get('From', '')
            date = msg.get('Date', '')
            
            # Extrai corpo do e-mail (texto simples e HTML)
            body_text = ""
            body_html = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # Pula anexos
                    if "attachment" in content_disposition:
                        continue
                        
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        try:
                            if payload:
                                body_text = payload.decode(errors='replace')
                        except Exception as e:
                            logger.error(f"Erro ao decodificar o corpo do e-mail: {e}")
                            body_text = "(Corpo não disponível)"
                    elif content_type == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_html = payload.decode(errors='replace')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    try:
                        if msg.get_content_type() == "text/html":
                            body_html = payload.decode(errors='replace')
                        else:
                            body_text = payload.decode(errors='replace')
                    except Exception as e:
                        logger.error(f"Erro ao decodificar o corpo do e-mail: {e}")
                        body_text = "(Corpo não disponível)"
            
            return {
                'subject': subject,
                'from': sender,
                'date': date,
                'body_text': body_text,
                'body_html': body_html
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do e-mail: {e}")
            return None

    def close_connection(self):
        """
        Fecha a conexão IMAP de forma segura.
        """
        if not self.mail:
            return
            
        try:
            logger.debug("Fechando conexão IMAP")
            if self.connected:
                try:
                    self.mail.close()
                except Exception as e:
                    logger.warning(f"Erro ao fechar caixa selecionada: {e}")
                    
            try:
                self.mail.logout()
                logger.info("Logout IMAP realizado com sucesso")
            except Exception as e:
                logger.warning(f"Erro durante logout IMAP: {e}")
        finally:
            self.mail = None
            self.connected = False
