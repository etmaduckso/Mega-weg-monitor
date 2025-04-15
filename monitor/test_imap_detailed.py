import imaplib
import ssl

try:
    print("Tentando conexão SSL...")
    mail = imaplib.IMAP4_SSL('191.6.216.100', 993, timeout=10)
    print("Conexão estabelecida. Tentando login...")
    mail.login('sooretama@megasec.com.br', 'Megasec@2025')
    print("Login bem-sucedido!")
except Exception as e:
    print(f"Erro detalhado: {type(e).__name__}: {e}")
finally:
    if 'mail' in locals():
        mail.logout()
