import imaplib
import email
import logging
from email.header import decode_header
from typing import Dict, List

logger = logging.getLogger('wegnots.email_handler')

class IMAPConnection:
    def __init__(self, server, port, username, password, is_active=True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.is_active = is_active
        self.imap = None
        self.connection_status = 'disconnected'
        
    def connect(self) -> bool:
        """Estabelece conexão com servidor IMAP"""
        if not self.is_active:
            return False
            
        try:
            if self.imap:
                try:
                    self.imap.logout()
                except:
                    pass
                    
            self.imap = imaplib.IMAP4_SSL(self.server, self.port)
            self.imap.login(self.username, self.password)
            self.connection_status = 'connected'
            logger.info(f"Conectado ao servidor IMAP {self.server}")
            return True
            
        except Exception as e:
            self.connection_status = 'error'
            logger.error(f"Erro ao conectar ao servidor {self.server}: {e}")
            return False

    def disconnect(self):
        """Desconecta do servidor IMAP"""
        if self.imap:
            try:
                self.imap.logout()
                logger.info(f"Desconectado do servidor IMAP {self.server}")
            except:
                pass
        self.connection_status = 'disconnected'

    def check_connection(self) -> bool:
        """Verifica se a conexão está ativa e reconecta se necessário"""
        if not self.imap:
            return self.connect()
        try:
            self.imap.noop()
            return True
        except:
            return self.connect()

    def get_recent_emails(self, limit=30) -> List[Dict]:
        """Obtém os emails mais recentes da caixa de entrada"""
        emails = []
        try:
            if not self.check_connection():
                logger.error(f"Falha ao conectar ao servidor {self.server} para buscar emails recentes")
                return emails

            # Seleciona a caixa de entrada
            status, messages = self.imap.select('INBOX')
            if status != 'OK':
                logger.error(f"Falha ao selecionar INBOX no servidor {self.server}: {status}")
                return emails

            # Busca todos os emails
            status, messages = self.imap.search(None, 'ALL')
            if status != 'OK':
                logger.error(f"Falha ao buscar emails no servidor {self.server}: {status}")
                return emails

            # Obtém os IDs dos emails em ordem reversa (mais recentes primeiro)
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            email_ids.reverse()

            for email_id in email_ids:
                try:
                    status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        logger.error(f"Falha ao buscar email ID {email_id} no servidor {self.server}")
                        continue

                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)

                    # Log detalhado do email
                    logger.info(f"Email encontrado - Servidor: {self.server}, ID: {email_id}, "
                              f"Subject: {email_message['subject']}, "
                              f"From: {email_message['from']}, "
                              f"Date: {email_message['date']}")

                    emails.append({
                        'id': email_id.decode(),
                        'subject': email_message['subject'],
                        'from': email_message['from'],
                        'date': email_message['date']
                    })
                except Exception as e:
                    logger.error(f"Erro ao processar email ID {email_id} no servidor {self.server}: {str(e)}")

        except Exception as e:
            logger.error(f"Erro ao buscar emails recentes no servidor {self.server}: {str(e)}")
        
        return emails

    def diagnose_connection(self):
        """Realiza diagnóstico detalhado da conexão IMAP"""
        diagnosis = {
            'server': self.server,
            'ssl_connection': False,
            'authentication': False,
            'inbox_access': False,
            'can_list_emails': False,
            'recent_emails_count': 0,
            'latest_email_info': None,
            'error': None
        }
        
        try:
            # Testa conexão SSL
            self.imap_conn = imaplib.IMAP4_SSL(self.server, self.port)
            diagnosis['ssl_connection'] = True
            
            # Testa autenticação
            self.imap_conn.login(self.username, self.password)
            diagnosis['authentication'] = True
            
            # Testa acesso à INBOX
            status, messages = self.imap_conn.select('INBOX')
            if status == 'OK':
                diagnosis['inbox_access'] = True
                
                # Testa listagem dos últimos 30 emails
                num_messages = min(int(messages[0]), 30)
                status, messages = self.imap_conn.search(None, 'ALL')
                if status == 'OK':
                    diagnosis['can_list_emails'] = True
                    email_ids = messages[0].split()
                    
                    if email_ids:
                        # Conta emails recentes
                        diagnosis['recent_emails_count'] = len(email_ids[-30:])
                        
                        # Obtém informações do email mais recente
                        latest_email_id = email_ids[-1]
                        status, msg_data = self.imap_conn.fetch(latest_email_id, '(RFC822)')
                        if status == 'OK':
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            diagnosis['latest_email_info'] = {
                                'subject': decode_header(email_message['subject'])[0][0],
                                'from': email_message['from'],
                                'date': email_message['date']
                            }
            
        except Exception as e:
            diagnosis['error'] = str(e)
        finally:
            try:
                if hasattr(self, 'imap_conn'):
                    self.imap_conn.close()
                    self.imap_conn.logout()
            except:
                pass
                
        return diagnosis

class EmailHandler:
    def __init__(self, telegram_client):
        self.primary = None
        self.secondary = None
        self.telegram_client = telegram_client
        
    def setup_connections(self, primary_config: Dict, secondary_config: Dict):
        """Configura conexões IMAP primária e secundária"""
        self.primary = IMAPConnection(
            server=primary_config['server'],
            port=primary_config['port'],
            username=primary_config['username'],
            password=primary_config['password'],
            is_active=primary_config.get('is_active', True)
        )
        
        self.secondary = IMAPConnection(
            server=secondary_config['server'],
            port=secondary_config['port'],
            username=secondary_config['username'],
            password=secondary_config['password'],
            is_active=secondary_config.get('is_active', True)
        )
        
    def connect(self) -> bool:
        """Estabelece conexões com servidores IMAP"""
        primary_ok = self.primary.connect() if self.primary else False
        secondary_ok = self.secondary.connect() if self.secondary else False
        return primary_ok or secondary_ok
        
    def check_new_emails(self) -> List[Dict]:
        """Verifica novos e-mails em todos os servidores ativos"""
        new_emails = []
        
        for connection in [self.primary, self.secondary]:
            if not connection or not connection.is_active or not connection.imap:
                continue
                
            try:
                connection.imap.select('INBOX')
                _, messages = connection.imap.search(None, 'UNSEEN')
                email_ids = messages[0].split()
                
                for email_id in email_ids:
                    _, msg_data = connection.imap.fetch(email_id, '(RFC822)')
                    email_body = msg_data[0][1]
                    message = email.message_from_bytes(email_body)
                    
                    subject = decode_email_header(message['subject'])
                    from_addr = decode_email_header(message['from'])
                    body = get_email_body(message)
                    
                    new_emails.append({
                        'id': email_id.decode(),
                        'server': connection.server,
                        'subject': subject,
                        'from': from_addr,
                        'body': body
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao verificar e-mails em {connection.server}: {e}")
                connection.connect()  # Tenta reconectar em caso de erro
                
        return new_emails
        
    def process_emails(self):
        """Processa emails não lidos e envia alertas"""
        new_emails = self.check_new_emails()
        
        for email_data in new_emails:
            try:
                self.telegram_client.send_alert(
                    subject=email_data['subject'],
                    from_addr=email_data['from'],
                    body=email_data['body']
                )
            except Exception as e:
                logger.error(f"Erro ao processar e-mail: {e}")
                
    def shutdown(self):
        """Encerra conexões IMAP"""
        if self.primary:
            self.primary.disconnect()
        if self.secondary:
            self.secondary.disconnect()

    def diagnose_connections(self) -> Dict:
        """Realiza diagnóstico de todas as conexões"""
        return {
            'primary': self.primary.diagnose_connection() if self.primary else None,
            'secondary': self.secondary.diagnose_connection() if self.secondary else None
        }

def decode_email_header(header):
    """Decodifica cabeçalhos de e-mail"""
    if not header:
        return ""
    try:
        decoded_parts = decode_header(header)
        parts = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                try:
                    parts.append(part.decode(charset or 'utf-8', errors='replace'))
                except:
                    parts.append(part.decode('utf-8', errors='replace'))
            else:
                parts.append(str(part))
        return " ".join(parts)
    except:
        return str(header)

def get_email_body(message):
    """Extrai o corpo do e-mail"""
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='replace')
                except:
                    continue
    else:
        try:
            return message.get_payload(decode=True).decode('utf-8', errors='replace')
        except:
            return message.get_payload()
