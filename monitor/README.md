# WegNots - Sistema de Monitoramento de E-mails

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)

Sistema profissional para monitoramento de e-mails IMAP e envio de notificações via Telegram, desenvolvido com foco em robustez, escalabilidade e seguindo boas práticas de desenvolvimento.

## 📋 Características Implementadas

- **Conexão IMAP Robusta**: 
  - Conexão segura via SSL/TLS
  - Reconexão automática com backoff exponencial
  - Tratamento refinado de falhas temporárias

- **Múltiplas Contas IMAP**:
  - Suporte para monitorar várias contas simultaneamente
  - Ativação/desativação por configuração
  - Detecção automática de servidores para diferentes provedores

- **Notificações Inteligentes**:
  - Formatação rica de mensagens com Markdown V2
  - Suporte a emojis para melhor visualização
  - Decodificação inteligente de cabeçalhos de email

- **Notificações via Telegram**:
  - Formatação avançada de mensagens com Markdown V2
  - Sistema de tratamento de erro para garantir entrega
  - Suporte a emojis para melhor visualização

- **Gerenciador de Configuração**:
  - Interface interativa de linha de comando
  - Adição/edição/remoção de contas
  - Configuração simplificada do Telegram
  - Validação de conexões e credenciais

## 📋 Pré-requisitos

- Python 3.9+
- Conta de e-mail com IMAP habilitado
- Bot do Telegram criado via [@BotFather](https://t.me/BotFather)
- Docker (opcional, para execução em container)

## 🛠 Configuração

### Usando o Gerenciador de Configuração

A maneira mais fácil de configurar o sistema é usando o gerenciador de configuração interativo:

```bash
python config_manager.py
```

Este utilitário oferece um menu interativo para:
- Listar todos os e-mails monitorados
- Adicionar novo e-mail para monitoramento
- Remover e-mail do monitoramento
- Editar configurações de e-mail existente
- Configurar o Telegram (token e chat_id)

### Configuração Manual

A configuração do sistema também pode ser feita manualmente através do arquivo `config.ini`:

```ini
[IMAP_PRIMARY]
server = mail.megasec.com.br
port = 993
username = seu@megasec.com.br
password = sua_senha
is_active = true

[IMAP_SECONDARY]
server = imap.gmail.com
port = 993
username = outro@gmail.com
password = senha_do_app
is_active = true

[TELEGRAM]
token = seu_token_do_bot
chat_id = seu_chat_id
```

### Servidores IMAP Suportados

O sistema detecta automaticamente o servidor IMAP com base no domínio do e-mail. Servidores suportados incluem:

- **mail.megasec.com.br** - Para contas @megasec.com.br
- **imap.gmail.com** - Para contas @gmail.com
- **outlook.office365.com** - Para contas @outlook.com ou @hotmail.com
- **imap.mail.yahoo.com** - Para contas @yahoo.com

### Múltiplas Contas

O sistema suporta monitoramento de múltiplas contas simultaneamente:
- Use seções `IMAP_PRIMARY` e `IMAP_SECONDARY` para as duas contas principais
- Para contas adicionais, use o formato `IMAP_email@domain.com`
- Configure `is_active = true/false` para habilitar/desabilitar contas
- Cada conta é monitorada independentemente

### Processamento de E-mails

O sistema implementa um robusto mecanismo de processamento:
- Decodificação inteligente de cabeçalhos (UTF-8, latin1, etc.)
- Tratamento adequado de caracteres especiais
- Suporte a diferentes codificações de e-mail

### Notificações Telegram

As mensagens são formatadas usando Markdown V2:
- Remetente em **negrito**
- Assunto em _itálico_
- Escape automático de caracteres especiais
- Suporte a emojis e formatação rica

### Configuração do Bot do Telegram

1. Crie um bot no Telegram através do [@BotFather](https://t.me/BotFather)
2. Anote o token do bot fornecido
3. Inicie uma conversa com seu bot
4. Obtenha seu chat_id com o seguinte método:
   - Envie uma mensagem para o seu bot
   - Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   - Procure o valor do campo "chat_id" na resposta JSON
5. Configure o token e chat_id no arquivo config.ini ou use o `config_manager.py`

### Testando a Configuração do Telegram

Para testar a conexão com o Telegram:
```bash
python test_telegram_new.py
```

Este teste verifica se o sistema consegue se conectar ao Telegram e enviar mensagens de teste. Certifique-se de que o token e chat_id estejam configurados corretamente antes de executar este teste.

## 🚀 Execução

### Ambiente local

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o monitoramento
python simple_monitor.py
```

### Docker

```bash
# Construir e iniciar o container
docker-compose up --build

# Executar em background
docker-compose up -d
```

## 🏗 Estrutura Atual do Projeto

```
monitor/
├── simple_monitor.py      # Script principal de monitoramento
├── config_manager.py      # Gerenciador de configuração interativo
├── config.ini             # Arquivo de configuração
├── docker-compose.yml     # Configuração Docker
├── Dockerfile             # Definição da imagem Docker
├── requirements.txt       # Dependências Python
├── test_telegram_new.py   # Script para testar integração com Telegram
├── app/                   # Módulos auxiliares (em desenvolvimento)
│   ├── core/              # Componentes principais
├── logs/                  # Diretório para arquivos de log
```

## 📈 Recursos Implementados

### Sistema de Notificação

O sistema implementa os seguintes recursos para notificações:

1. **Formatação de Mensagens**:
   - Formatação rica com Markdown V2
   - Suporte a emojis para melhor visualização
   - Escape automático de caracteres especiais

2. **Garantia de Entrega**:
   - Tratamento de erros de API
   - Sistema de intervalo entre mensagens
   - Logs detalhados para diagnóstico

### Monitoramento de E-mails

O sistema implementa os seguintes recursos para monitoramento de e-mails:

1. **Conexão IMAP**:
   - Conexão segura via SSL
   - Tratamento de erros de conexão
   - Suporte a múltiplos servidores

2. **Processamento de E-mails**:
   - Decodificação de cabeçalhos (assunto, remetente, etc.)
   - Suporte a diferentes codificações
   - Extração de informações relevantes

### Logs Detalhados

Os logs são gerados com informações detalhadas sobre o funcionamento do sistema:
- Informações de inicialização e encerramento
- Detalhes de conexão e reconexão
- Eventos de processamento de e-mails
- Alertas e notificações enviadas
- Erros e exceções

Os logs são salvos em:
- Console (stdout)
- Arquivo `logs/wegnots.log` no diretório monitor

## 🔧 Manutenção e Suporte

### Solução de Problemas

**Problemas de Conexão IMAP**
- Verifique suas credenciais no arquivo de configuração
- Confirme se o servidor IMAP está acessível e correto
  - Para Megasec: `mail.megasec.com.br` (não use endereços IP)
  - Para Gmail: `imap.gmail.com`
- Verifique se o IMAP está habilitado na sua conta
- Verifique configurações de firewall e proxy

**Problemas com Telegram**
- Confirme se o token do bot está correto
- Verifique se você iniciou uma conversa com o bot
- Execute `test_telegram_new.py` para testar a conexão

### Monitoramento em Produção

Para ambientes de produção, recomenda-se:

- **Docker com Restart**: Configuração já presente no arquivo docker-compose.yml
  ```yaml
  services:
    monitor:
      build: .
      restart: always
  ```

## 📝 Licença

Este projeto é licenciado sob a Apache-2.0 license - veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 🧪 Recursos Futuros em Desenvolvimento

Os seguintes recursos estão planejados para implementação futura:

1. **Sistema de Múltiplos Usuários**:
   - Suporte para múltiplos destinatários de notificações
   - Gerenciamento individual de preferências de notificação
   - Regras personalizadas por remetente

2. **Integração com RocketChat**:
   - Suporte para envio de notificações via RocketChat
   - Formatação avançada de mensagens
   - Integração via API REST

3. **Categorização de Alertas**:
   - Classificação automática por prioridade
   - Regras personalizáveis para categorização
   - Tratamento diferenciado por categoria

4. **Interface de Administração Completa**:
   - Dashboard de monitoramento
   - Configuração via interface web
   - Visualização de logs e estatísticas
