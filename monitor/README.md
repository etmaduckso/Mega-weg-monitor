# WegNots - Sistema de Monitoramento de E-mails

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)

Sistema profissional para monitoramento de e-mails IMAP e envio de notificações via Telegram, desenvolvido com foco em robustez, escalabilidade e seguindo boas práticas de desenvolvimento.

## 📋 Características

- **Conexão IMAP Robusta**: 
  - Conexão segura via SSL/TLS
  - Reconexão automática com backoff exponencial
  - Tratamento refinado de falhas temporárias

- **Notificações via Telegram e RocketChat**:
  - Formatação rica de mensagens com Markdown
  - Suporte a emojis para melhor visualização
  - Mecanismo de retry para garantir entrega mesmo com falhas de conectividade
  - Integração com RocketChat para ambientes corporativos

## 📋 Pré-requisitos

- Python 3.9+
- Conta de e-mail com IMAP habilitado
- Bot do Telegram criado via [@BotFather](https://t.me/BotFather)
- Docker (opcional, para execução em container)

## 🛠 Configuração

### Configuração Manual

A configuração do sistema pode ser feita de duas maneiras:

**1. Usando arquivo config.py (recomendado)**

O sistema já vem pré-configurado com valores padrão no arquivo `config.py` na raiz do projeto. Este arquivo contém as configurações principais:

```python
TELEGRAM_CONFIG = {
    'token': '8002419840:AAFL_Wu0aZ_NOGS9LOo9a9HxRbdGMxxv6-E',
    'chat_id': '1395823978'
}

IMAP_CONFIG = {
    'server': 'imap.titan.email',
    'port': 993,
    'username': 'sooretama@megasec.com.br',
    'password': 'Megasec@2025'
}
```

Você pode editar este arquivo diretamente para modificar a configuração.

**2. Usando variáveis de ambiente**

Alternativamente, você pode criar um arquivo `.env` na raiz do projeto:

```
# Configurações IMAP
IMAP_SERVER=imap.titan.email
IMAP_PORT=993
IMAP_USER=seu@email.com
IMAP_PASSWORD=sua_senha

# Configurações Telegram
TELEGRAM_TOKEN=seu_token_bot
TELEGRAM_CHAT_ID=seu_chat_id

# Configurações de monitoramento
CHECK_INTERVAL=60
RECONNECT_ATTEMPTS=5
RECONNECT_DELAY=30
RECONNECT_BACKOFF_FACTOR=1.5

# Configurações de logging
LOG_LEVEL=INFO

# Configurações RocketChat
ROCKETCHAT_URL=http://localhost:3000
ROCKETCHAT_USER_ID=seu-user-id
ROCKETCHAT_TOKEN=seu-token
ROCKETCHAT_CHANNEL=alertas
# OU usando webhook
ROCKETCHAT_WEBHOOK_URL=http://localhost:3000/hooks/seu-webhook-token
```

Para mais detalhes sobre a configuração do RocketChat, consulte a documentação em `docs/ROCKET_CHAT_INTEGRATION.md`.

### Testes de Conexão

Para testar a conexão IMAP:
```bash
python test_imap_connection.py
```

Para testar o Telegram:
```bash
python telegram_test.py
```

Para obter o CHAT_ID do Telegram:
```bash
python test_telegram_chat_id.py
```

Para testar a integração com o RocketChat:
```bash
python rocketchat_test.py
```

Este teste verifica se o sistema consegue se conectar ao RocketChat e enviar mensagens de teste, tanto mensagens simples quanto alertas formatados. Certifique-se de que o RocketChat esteja em execução e configurado corretamente antes de executar este teste.

### Verificando a Integração com o RocketChat

Para verificar se a integração com o RocketChat está funcionando corretamente, siga estes passos:

1. **Inicie o RocketChat e MongoDB**:
   ```bash
   docker-compose up -d rocketchat mongo
   ```

2. **Aguarde a inicialização completa** (pode levar alguns minutos na primeira execução):
   ```bash
   docker-compose logs -f rocketchat
   ```
   Aguarde até ver mensagens indicando que o servidor está pronto.

3. **Acesse o RocketChat** através do navegador em http://localhost:3000

4. **Configure um usuário administrador** na primeira execução:
   - Preencha os dados do administrador (nome, email, senha)
   - Complete o processo de configuração inicial

5. **Obtenha as credenciais de API**:
   - Vá para seu perfil (clique no avatar no canto superior direito)
   - Selecione "Minha Conta" > "Segurança" > "Personal Access Tokens"
   - Crie um novo token com escopo "user" e "admin"
   - Anote o User ID e o Token gerado

6. **Configure as credenciais** no arquivo config.py ou no arquivo .env:
   ```python
   # No config.py
   ROCKETCHAT_CONFIG = {
       'url': 'http://localhost:3000',
       'user_id': 'seu-user-id-aqui',
       'token': 'seu-token-aqui',
       'channel': 'general'  # ou outro canal de sua escolha
   }
   ```

7. **Crie um canal para testes** (opcional):
   - No RocketChat, clique no "+" ao lado de "Canais"
   - Crie um novo canal (ex: "alertas")
   - Certifique-se de que seu usuário tem permissão para enviar mensagens neste canal

8. **Execute o script de teste**:
   ```bash
   python rocketchat_test.py
   ```

9. **Verifique o resultado**:
   - O script deve exibir mensagens de sucesso no terminal
   - Acesse o RocketChat e verifique se as mensagens de teste foram recebidas no canal configurado
   - As mensagens devem incluir formatação Markdown e emojis

10. **Solução de problemas comuns**:
    - Se o script falhar com erro de autenticação, verifique o User ID e Token
    - Se as mensagens não aparecerem, verifique se o canal existe e se o usuário tem permissão para enviar mensagens
    - Se o RocketChat não estiver acessível, verifique se os containers estão em execução com `docker-compose ps`

## 🚀 Execução

### Ambiente local

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o monitoramento
python main.py
```

### Docker

```bash
# Construir e iniciar o container
docker-compose up --build

# Executar em background
docker-compose up -d
```

#### Configuração do RocketChat

O projeto inclui um arquivo `docker-compose.yml` atualizado para executar uma instância local do RocketChat para testes e integração. Esta configuração foi atualizada para usar as versões mais recentes do RocketChat e MongoDB:

```yaml
version: '3'

volumes:
  mongodb_data: { driver: local }

services:
  rocketchat:
    image: registry.rocket.chat/rocketchat/rocket.chat:latest
    restart: unless-stopped
    volumes:
      - ./uploads:/app/uploads
    environment:
      - PORT=3000
      - ROOT_URL=http://localhost:3000
      - MONGO_URL=mongodb://mongo:27017/rocketchat?replicaSet=rs0
      - MONGO_OPLOG_URL=mongodb://mongo:27017/local?replicaSet=rs0
      - DEPLOY_METHOD=docker
    depends_on:
      - mongo
    ports:
      - 3000:3000

  mongo:
    image: docker.io/bitnami/mongodb:6.0
    restart: unless-stopped
    volumes:
      - ./data/db:/bitnami/mongodb
    environment:
      MONGODB_REPLICA_SET_MODE: primary
      MONGODB_REPLICA_SET_NAME: rs0
      MONGODB_PORT_NUMBER: 27017
      MONGODB_INITIAL_PRIMARY_HOST: mongo
      MONGODB_INITIAL_PRIMARY_PORT_NUMBER: 27017
      MONGODB_ADVERTISED_HOSTNAME: mongo
      MONGODB_ENABLE_JOURNAL: true
      ALLOW_EMPTY_PASSWORD: yes
```

Principais melhorias na configuração do RocketChat:

1. **MongoDB Atualizado**: Utiliza MongoDB 6.0 da Bitnami, que oferece melhor desempenho e segurança em comparação com versões anteriores.
2. **Configuração Simplificada**: Configuração automática do conjunto de réplicas do MongoDB, eliminando a necessidade de scripts de inicialização complexos.
3. **Imagem Oficial**: Usa a imagem oficial mais recente do RocketChat do registro oficial.
4. **Volumes Persistentes**: Mantém os dados do MongoDB e os uploads do RocketChat em volumes locais para persistência entre reinicializações.

Para iniciar o RocketChat:

```bash
# Iniciar apenas o RocketChat e MongoDB
docker-compose up -d rocketchat mongo
```

Após a inicialização, o RocketChat estará disponível em: http://localhost:3000

## 🏗 Estrutura do Projeto

```
wegnots/
├── app/
│   ├── core/               # Lógica principal
│   │   ├── email_handler.py    # Gerencia conexão IMAP
│   │   ├── telegram_client.py  # Envia notificações via Telegram
│   │   └── rocketchat_client.py # Envia notificações via RocketChat
│   ├── config/             # Configurações
│   │   └── settings.py         # Carrega e valida configurações
├── docs/
│   └── ROCKET_CHAT_INTEGRATION.md # Documentação da integração com RocketChat
├── infrastructure/
│   ├── docker/
│   │   └── Dockerfile          # Configuração do container
├── tests/
│   ├── unit/                   # Testes unitários 
│   └── integration/            # Testes de integração
├── .github/
│   └── workflows/
│       └── main.yml            # Configuração do GitHub Actions
├── config.py                   # Configuração principal
├── main.py                     # Ponto de entrada
├── docker-compose.yml          # Definição de serviços Docker
├── requirements.txt            # Dependências Python
├── rocketchat_test.py          # Script para testar integração com RocketChat
├── telegram_test.py            # Script para testar integração com Telegram
├── VERSION                     # Arquivo de versão
└── README.md                   # Este arquivo
```

## 📈 Recursos Avançados

### Tipos de Alerta

O sistema categoriza os e-mails em três níveis de alerta baseados no assunto:

- **Alerta Crítico (1)**: Identificado por palavras como "urgente", "crítico", "emergência"
- **Alerta Moderado (2)**: Identificado por palavras como "importante", "atenção"
- **Alerta Leve (3)**: Demais e-mails sem palavras-chave específicas

### Reconexão Inteligente

A reconexão ao servidor IMAP utiliza uma estratégia de backoff exponencial, aumentando progressivamente o tempo entre tentativas para evitar sobrecarga do servidor.

### Logs Detalhados

Os logs são gerados com informações detalhadas sobre o funcionamento do sistema:
- Informações de inicialização e encerramento
- Detalhes de conexão e reconexão
- Eventos de processamento de e-mails
- Alertas e notificações enviadas
- Erros e exceções

Os logs são salvos em:
- Console (stdout)
- Arquivo `wegnots.log` no diretório de execução

## 🔧 Manutenção e Suporte

### Solução de Problemas

**Problemas de Conexão IMAP**
- Verifique suas credenciais no arquivo de configuração
- Confirme se o servidor IMAP está acessível
- Verifique configurações de firewall e proxy

**Problemas com Telegram**
- Confirme se o token do bot está correto
- Verifique se você iniciou uma conversa com o bot
- Execute `test_telegram_chat_id.py` para obter o chat_id correto

**Problemas com RocketChat**
- Verifique se o RocketChat está em execução (`docker-compose ps`)
- Confirme se as credenciais do RocketChat estão corretas
- Verifique se o canal especificado existe no RocketChat
- Execute `rocketchat_test.py` para testar a conexão e envio de mensagens
- Consulte a documentação em `docs/ROCKET_CHAT_INTEGRATION.md` para mais detalhes

### Monitoramento em Produção

Para ambientes de produção, recomenda-se:

- **Systemd**: Para execução como serviço no Linux
  ```bash
  # Exemplo de arquivo de serviço systemd
  [Unit]
  Description=WegNots Email Monitor
  After=network.target

  [Service]
  Type=simple
  User=seu_usuario
  WorkingDirectory=/caminho/para/wegnots
  ExecStart=/usr/bin/python3 /caminho/para/wegnots/main.py
  Restart=always
  RestartSec=10

  [Install]
  WantedBy=multi-user.target
  ```

- **Docker com Restart**: Configuração já presente no arquivo docker-compose.yml
  ```yaml
  services:
    wegnots:
      build: .
      restart: always
  ```

### CI/CD e Versionamento

O projeto utiliza GitHub Actions para Integração Contínua e Entrega Contínua (CI/CD). O pipeline inclui:

- Execução de testes automatizados
- Verificação de estilo de código com pylint
- Construção e teste de imagem Docker

O versionamento do projeto segue o padrão Semântico (SemVer) e é controlado pelo arquivo `VERSION` na raiz do projeto.

Para atualizar a versão:

1. Edite o arquivo `VERSION`
2. Commit a mudança
3. Crie uma tag Git com a nova versão
4. Push a tag para o repositório

Exemplo:
```bash
echo "1.1.0" > VERSION
git add VERSION
git commit -m "Bump version to 1.1.0"
git tag v1.1.0
git push origin v1.1.0
```

## 📝 Licença

Este projeto é licenciado sob a Apache-2.0 license - veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Antes de contribuir, por favor leia nosso [guia de contribuição](CONTRIBUTING.md) para entender nosso processo de desenvolvimento e os padrões que seguimos.

Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

Certifique-se de seguir nossas diretrizes de código, incluindo o uso do pylint para manter a consistência do estilo de código.

## 📜 Código de Conduta

Este projeto e todos os participantes estão sob o regimento do [Código de Conduta WegNots](CODE_OF_CONDUCT.md). Ao participar deste projeto, você concorda em cumprir seus termos.

## 🧪 Testes

Este projeto utiliza unittest para testes unitários e de integração. Para executar os testes, siga estas etapas:

1. Certifique-se de que todas as dependências estão instaladas:
   ```
   pip install -r requirements.txt
   ```

2. Execute os testes unitários:
   ```bash
   python -m unittest discover tests/unit
   ```

3. Execute os testes de integração:
   ```bash
   python -m unittest discover tests/integration
   ```

Os testes cobrem as principais funcionalidades do EmailHandler e do TelegramClient, incluindo:
- Conexão e autenticação IMAP
- Verificação de novos e-mails
- Parsing e extração de dados de e-mails
- Envio de alertas via Telegram
- Formatação de mensagens de alerta
- Integração entre o processamento de e-mails e o envio de alertas

Certifique-se de executar todos os testes antes de fazer um commit ou abrir um pull request.

## 🔄 Integração Contínua

Este projeto utiliza GitHub Actions para integração contínua. A cada push ou pull request, os seguintes passos são executados automaticamente:

1. Instalação das dependências
2. Execução dos testes unitários
3. Verificação de estilo de código com pylint
4. Construção e teste da imagem Docker

Você pode verificar o status dessas verificações na aba "Actions" do repositório GitHub.
