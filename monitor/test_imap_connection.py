import imaplib
import logging

# Configurações IMAP
IMAP_SERVER = 'imap.titan.email'
IMAP_PORT = 993
IMAP_USER = 'sooretama@megasec.com.br'
IMAP_PASSWORD = 'Megasec@2025'

# Configura o logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_imap_connection')

def test_imap_connection():
    try:
        logger.debug(f"Tentando conectar ao servidor IMAP {IMAP_SERVER}:{IMAP_PORT}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        logger.debug("Conexão IMAP estabelecida com sucesso.")
        
        # Tentar login
        status, response = mail.login(IMAP_USER, IMAP_PASSWORD)
        if status == 'OK':
            logger.info("Login IMAP bem-sucedido.")
        else:
            logger.error(f"Falha na autenticação IMAP: {response}")
        
        mail.logout()
    except Exception as e:
        logger.error(f"Erro ao conectar ao IMAP: {e}")

if __name__ == "__main__":
    test_imap_connection()
