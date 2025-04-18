"""
Arquivo de configuração principal para o WegNots

Este arquivo contém as configurações essenciais para o funcionamento
do sistema. As configurações aqui definidas têm precedência sobre
as configurações de ambiente (.env).

Para ambientes de produção, recomenda-se usar variáveis de ambiente
ou arquivo .env para evitar commits de credenciais.
"""

# Configurações Telegram
TELEGRAM_CONFIG = {
    'bot_token': '8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E',  # Token obtido do BotFather
    'default_chat_id': '1395823978',                               # Chat ID padrão para notificações gerais
    'retry_attempts': 5,                                           # Número de tentativas aumentado
    'retry_delay': 15,                                            # Delay entre tentativas aumentado
    'route_mapping': {
        'sooretama@megasec.com.br': ['1395823978'],              # Roteamento principal
        '*@megasec.com.br': ['1395823978'],                      # Qualquer email do domínio
    },
    'groups': {
        'suporte_ti': ['1395823978']                             # Grupo de suporte
    }
}

# Configurações IMAP
IMAP_CONFIG = {
    'server': 'imap.titan.email',                               # Servidor IMAP
    'port': 993,                                                    # Porta IMAP SSL padrão
    'username': 'sooretama@megasec.com.br',                     # Usuário IMAP
    'password': 'Megasec@2025',                                # Senha IMAP
    'check_interval': 60,                                           # Intervalo de verificação em segundos
    'reconnect_attempts': 5,                                        # Número máximo de tentativas de reconexão
    'reconnect_delay': 30,                                          # Delay entre tentativas de reconexão em segundos
    'reconnect_backoff_factor': 1.5                                 # Fator de backoff para reconexão exponencial
}

# Configurações de logging
LOG_CONFIG = {
    'level': 'INFO',                                                # Nível de detalhamento dos logs
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Formato dos logs
    'filename': 'wegnots.log'                                       # Arquivo de log
}

# Configurações Rocket.Chat
# As credenciais devem ser obtidas conforme a documentação em docs/ROCKET_CHAT_INTEGRATION.md
ROCKETCHAT_CONFIG = {
    'url': '',                                                      # URL do servidor Rocket.Chat (ex: https://chat.example.com)
    'user_id': '',                                                  # User ID do bot/usuário para API
    'token': '',                                                    # Token de acesso para API
    'channel': 'general',                                           # Canal padrão para enviar mensagens
    'webhook_url': '',                                              # URL do webhook (alternativa à API)
    'retry_attempts': 3,                                            # Número de tentativas para envio
    'retry_delay': 5                                                # Delay entre tentativas em segundos
}
