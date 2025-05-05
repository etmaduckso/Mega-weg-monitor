import imaplib
import email
import logging
from email.header import decode_header
from typing import Dict, List, Optional

logger = logging.getLogger('wegnots.email_handler')

class IMAPConnection:
    def __init__(self, server, port, username, password, is_active=True, telegram_chat_id=None, telegram_token=None):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.is_active = is_active
        self.imap = None
        self.connection_status = 'disconnected'
        # Informações do Telegram específicas para esta conexão
        self.telegram_chat_id = telegram_chat_id
        self.telegram_token = telegram_token
        
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

    def get_recent_emails(self, limit=10) -> List[Dict]:
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
        self.connections = {}
        self.telegram_client = telegram_client
        self.processed_emails = {}  # Dictionary to store processed email IDs per account
        
    def _get_email_key(self, server, username, email_id):
        """Generate a unique key for an email"""
        return f"{server}:{username}:{email_id}"
        
    def setup_connections(self, config_sections):
        """Configura múltiplas conexões IMAP a partir de seções do arquivo de configuração"""
        for section_name, config in config_sections.items():
            if section_name.startswith('IMAP_') and config.get('is_active', 'false').lower() == 'true':
                connection = IMAPConnection(
                    server=config['server'],
                    port=int(config['port']),
                    username=config['username'],
                    password=config['password'],
                    is_active=True,
                    telegram_chat_id=config.get('telegram_chat_id'),
                    telegram_token=config.get('telegram_token')
                )
                
                # Adiciona a conexão ao dicionário, usando o username como chave
                self.connections[config['username']] = connection
                logger.info(f"Configurada conexão IMAP para {config['username']}")
        
    def connect(self) -> bool:
        """Estabelece conexões com todos os servidores IMAP"""
        success = False
        
        for username, connection in self.connections.items():
            if connection.connect():
                success = True
                
        return success
        
    def check_new_emails(self) -> List[Dict]:
        """Verifica novos e-mails em todos os servidores ativos"""
        new_emails = []
        
        for username, connection in self.connections.items():
            if not connection or not connection.is_active or not connection.imap:
                logger.warning(f"Conexão inativa ou com problemas para {username}")
                continue
                
            try:
                logger.debug(f"Verificando emails para {username} em {connection.server}")
                status, selected = connection.imap.select('INBOX')
                if status != 'OK':
                    logger.error(f"Falha ao selecionar INBOX para {username}: {status}")
                    continue
                    
                # Initialize processed emails set for this account if it doesn't exist
                if username not in self.processed_emails:
                    self.processed_emails[username] = set()
                
                # Estratégia 1: Busca emails não lidos (UNSEEN)
                status, messages = connection.imap.search(None, 'UNSEEN')
                email_ids = messages[0].split() if status == 'OK' else []
                
                # Se não houver emails não lidos, não procuramos mais
                # Removida a busca por emails das últimas 24h e emails recentes
                # para evitar processamento duplicado
                
                for email_id in email_ids:
                    try:
                        email_key = self._get_email_key(connection.server, username, email_id.decode())
                        
                        # Skip if already processed
                        if email_key in self.processed_emails[username]:
                            logger.debug(f"Email {email_id} já processado para {username}")
                            continue
                            
                        status, msg_data = connection.imap.fetch(email_id, '(RFC822)')
                        if status != 'OK' or not msg_data or not msg_data[0]:
                            logger.error(f"Falha ao buscar email ID {email_id} para {username}")
                            continue
                            
                        email_body = msg_data[0][1]
                        message = email.message_from_bytes(email_body)
                        
                        subject = decode_email_header(message['subject'])
                        from_addr = decode_email_header(message['from'])
                        body = get_email_body(message)
                        
                        logger.info(f"Novo email encontrado para {username}: Subject='{subject}', De='{from_addr}'")
                        
                        new_emails.append({
                            'id': email_id.decode(),
                            'server': connection.server,
                            'username': username,
                            'subject': subject,
                            'from': from_addr,
                            'body': body,
                            'telegram_chat_id': connection.telegram_chat_id,
                            'telegram_token': connection.telegram_token,
                            'email_key': email_key
                        })
                        
                        # Mark as read immediately after processing
                        connection.imap.store(email_id, '+FLAGS', '\\Seen')
                        # Add to processed set
                        self.processed_emails[username].add(email_key)
                        
                        # Limit the size of processed emails set (keep last 1000 per account)
                        if len(self.processed_emails[username]) > 1000:
                            self.processed_emails[username] = set(list(self.processed_emails[username])[-1000:])
                            
                    except Exception as e:
                        logger.error(f"Erro ao processar email ID {email_id} para {username}: {e}")
                    
            except Exception as e:
                logger.error(f"Erro ao verificar e-mails em {connection.server} para {username}: {e}")
                logger.info(f"Tentando reconectar para {username}")
                connection.connect()
                
        if new_emails:
            logger.info(f"Total de novos emails encontrados: {len(new_emails)}")
        
        return new_emails
        
    def process_emails(self):
        """Processa emails não lidos e envia alertas"""
        new_emails = self.check_new_emails()
        
        if not new_emails:
            return
            
        for email_data in new_emails:
            try:
                # Usa telegram_token e chat_id específicos da conta, se disponíveis
                token = email_data.get('telegram_token')
                chat_id = email_data.get('telegram_chat_id')
                
                logger.info(f"Enviando alerta para {email_data['username']} usando token: {'personalizado' if token else 'padrão'}, chat_id: {chat_id or 'padrão'}")
                
                # Log detalhado dos detalhes do alerta a ser enviado
                logger.debug(f"Detalhes do alerta: Subject='{email_data['subject']}', From='{email_data['from']}', Body Length={len(email_data['body']) if email_data['body'] else 0}")
                
                result = self.telegram_client.send_alert(
                    subject=email_data['subject'],
                    from_addr=email_data['from'],
                    body=email_data['body'],
                    token=token,
                    chat_id=chat_id
                )
                
                if result:
                    logger.info(f"Alerta enviado com sucesso para {email_data['username']}")
                else:
                    logger.error(f"Falha ao enviar alerta para {email_data['username']}")
                    
            except Exception as e:
                logger.error(f"Erro ao processar e-mail para {email_data.get('username', 'desconhecido')}: {e}")
                
    def shutdown(self):
        """Encerra todas as conexões IMAP"""
        for username, connection in self.connections.items():
            connection.disconnect()

    def diagnose_connections(self) -> Dict:
        """Realiza diagnóstico de todas as conexões"""
        return {username: connection.diagnose_connection() for username, connection in self.connections.items()}

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
    body = ""
    if message.is_multipart():
        # Primeiro tenta encontrar texto plano
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # Pula anexos
            if 'attachment' in cdispo:
                continue

            if ctype == 'text/plain':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break
                except:
                    continue

        # Se não encontrou texto plano, tenta HTML
        if not body:
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                # Pula anexos
                if 'attachment' in cdispo:
                    continue

                if ctype == 'text/html':
                    try:
                        html = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        # Remove tags HTML de forma simples
                        body = html.replace('<br>', '\n').replace('<br/>', '\n').replace('<p>', '\n').replace('</p>', '\n')
                        import re
                        body = re.sub('<[^<]+?>', '', body)
                        body = body.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
                        break
                    except:
                        continue
    else:
        # Mensagem não é multipart
        try:
            body = message.get_payload(decode=True).decode('utf-8', errors='replace')
        except:
            body = str(message.get_payload())

    # Limpa o texto
    body = '\n'.join(line.strip() for line in body.splitlines() if line.strip())
    return body
