# 🌟 WegNots - Sistema de Monitoramento de E-mails

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)
[![SOLID](https://img.shields.io/badge/principles-SOLID-orange.svg)](https://en.wikipedia.org/wiki/SOLID)
[![DevOps](https://img.shields.io/badge/practices-DevOps-blueviolet.svg)](https://aws.amazon.com/devops/what-is-devops/)

Sistema profissional para monitoramento de e-mails IMAP e envio de notificações via Telegram, desenvolvido com foco em robustez, escalabilidade e seguindo boas práticas de desenvolvimento.

---

## 📋 Características

### 🔒 **Conexão IMAP Robusta**: 
- Conexão segura via SSL/TLS
- Reconexão automática com backoff exponencial
- Tratamento refinado de falhas temporárias

### 📲 **Notificações Multicanal**:
- Formatação rica de mensagens com Markdown
- Suporte a emojis para melhor visualização
- Mecanismo de retry para garantir entrega
- Interface de notificação extensível (NotificationClient)
- Suporte atual para:
  - Telegram
  - RocketChat (para ambientes corporativos)

### 🏗 **Arquitetura SOLID**:
- **Single Responsibility Principle (SRP)**:
  - Separação clara entre manipulação de e-mails e notificações
  - Classes com responsabilidades únicas e bem definidas

- **Open/Closed Principle (OCP)**:
  - Interface `NotificationClient` permite adicionar novos canais sem modificar código existente
  - Estrutura extensível para futuros tipos de alertas

- **Liskov Substitution Principle (LSP)**:
  - Implementações de notificação (Telegram, RocketChat) são intercambiáveis
  - Comportamento consistente através da interface comum

- **Interface Segregation Principle (ISP)**:
  - Interfaces coesas e específicas para cada funcionalidade
  - Clientes não dependem de interfaces que não utilizam

- **Dependency Inversion Principle (DIP)**:
  - Injeção de dependência para clientes de notificação
  - Baixo acoplamento entre componentes

### 🚀 **Práticas DevOps**:
- **Containerização**:
  - Dockerfile otimizado para produção
  - Compose file para desenvolvimento local
  - Volumes persistentes para dados

- **CI/CD**:
  - GitHub Actions para integração contínua
  - Testes automatizados em cada PR
  - Linting e verificação de estilo
  - Builds Docker automatizados

- **Monitoramento**:
  - Logging estruturado com níveis configuráveis
  - Rastreamento detalhado de erros
  - Métricas de performance
  - Notificações de status do sistema

- **Segurança**:
  - Variáveis de ambiente para configurações sensíveis
  - Suporte a secrets no Docker
  - Conexões seguras (SSL/TLS)

---

## 📋 Pré-requisitos

- Python 3.9+
- Conta de e-mail com IMAP habilitado
- Bot do Telegram criado via [@BotFather](https://t.me/BotFather)
- Docker (opcional, para execução em container)

---

## 🚀 Como Configurar

1️⃣ **Edite o arquivo config.py** com suas credenciais:  
```python
TELEGRAM_CONFIG = {
    'token': 'SEU_TOKEN',
    'chat_id': 'SEU_CHAT_ID'
}

IMAP_CONFIG = {
    'server': 'imap.seuservidor.com',
    'port': 993,
    'username': 'seu@email.com',
    'password': 'sua_senha'
}
```

2️⃣ **Ou use um arquivo .env**:  
```
IMAP_SERVER=imap.seuservidor.com
IMAP_PORT=993
IMAP_USER=seu@email.com
IMAP_PASSWORD=sua_senha
TELEGRAM_TOKEN=SEU_TOKEN
TELEGRAM_CHAT_ID=SEU_CHAT_ID
```

---

## 🧪 Testes e Qualidade

### Testes Automatizados

- **Testes Unitários**: Cobrem componentes individuais
- **Testes de Integração**: Verificam interações entre módulos
- **Testes End-to-End**: Simulam fluxos completos do usuário

### Garantia de Qualidade

- Linting com pylint
- Type checking com mypy
- Formatação com black
- Análise de cobertura de código

---

## 🏗 Nova Estrutura do Projeto

```
wegnots/
├── app/
│   ├── core/               # Lógica principal
│   │   ├── email_handler.py    # Gerencia conexão IMAP
│   │   ├── notification_client.py  # Interface base para notificações
│   │   ├── telegram_client.py  # Cliente Telegram
│   │   └── rocketchat_client.py # Cliente RocketChat
│   ├── config/             # Configurações
│   │   └── settings.py         # Configurações centralizadas
├── docs/
│   └── ROCKET_CHAT_INTEGRATION.md # Documentação específica
├── infrastructure/
│   ├── docker/
│   │   └── Dockerfile          # Configuração do container
├── tests/
│   ├── unit/                   # Testes unitários 
│   └── integration/            # Testes de integração
├── .github/
│   └── workflows/
│       └── main.yml            # Pipeline CI/CD
├── main.py                     # Ponto de entrada
└── README.md                   # Este arquivo
```

---

## 📈 Recursos Avançados

### Tipos de Alerta

O sistema categoriza os e-mails em três níveis baseados no assunto:

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

---

## 🐳 Executando com Docker

1️⃣ **Construa e inicie o container**:  
```bash
docker-compose up --build
```

2️⃣ **Execute em segundo plano**:  
```bash
docker-compose up -d
```

---

## 📈 Logs e Monitoramento

- Os logs são salvos no arquivo wegnots.log.  
- Incluem informações detalhadas sobre conexões, notificações e erros.  

---

## 🤝 Contribuições

Contribuições são super bem-vindas!  
Leia nosso guia de contribuição para saber mais.  

---

## 📝 Licença

Este projeto é licenciado sob a licença Apache-2.0 license.  
Veja o arquivo `LICENSE` para mais detalhes.  

---

Espero que goste desta versão de Monitor e alerta para telegram! Se precisar de mais ajustes fique avontade, aproveita e me segue ai e se precisar de ajuda é só avisar! 😊
