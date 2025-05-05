import imaplib
import logging

# Configurações da conta Gmail
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
USERNAME = 'getconexoes@gmail.com'
PASSWORD = 'oqnj nlny edye vutq'

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gmail_connection_test')

def test_gmail_connection():
    try:
        logger.info('Iniciando teste de conexão com o Gmail...')
        
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        logger.info('Conexão com o servidor IMAP bem-sucedida.')
        
        # Fazer login
        mail.login(USERNAME, PASSWORD)
        logger.info('Login bem-sucedido.')
        
        # Selecionar a caixa de entrada
        status, messages = mail.select('INBOX')
        if status == 'OK':
            logger.info(f'Acesso à INBOX bem-sucedido. Total de mensagens: {messages[0].decode()}')
        else:
            logger.error('Falha ao acessar a INBOX.')
        
        # Desconectar
        mail.logout()
        logger.info('Logout realizado com sucesso.')
    except imaplib.IMAP4.error as e:
        logger.error(f'Erro de IMAP: {e}')
    except Exception as e:
        logger.error(f'Erro inesperado: {e}')

if __name__ == '__main__':
    test_gmail_connection()