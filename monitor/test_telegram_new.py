from app.core.telegram_client import TelegramClient

def test_telegram_notification():
    try:
        # Inicializa o cliente Telegram
        telegram_client = TelegramClient()
        
        # Envia mensagem de teste
        success = telegram_client.send_startup_message()
        
        if success:
            print("✅ Teste do Telegram concluído com sucesso!")
        else:
            print("❌ Falha no teste do Telegram")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    test_telegram_notification()