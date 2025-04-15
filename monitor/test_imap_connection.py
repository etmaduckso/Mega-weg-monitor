import imaplib
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')

def test_imap_connection():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USER, IMAP_PASSWORD)
        print("Conexão IMAP bem-sucedida!")
        mail.logout()
    except Exception as e:
        print(f"Erro ao conectar ao IMAP: {e}")

if __name__ == "__main__":
    test_imap_connection()
