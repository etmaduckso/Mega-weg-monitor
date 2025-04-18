# 🌟 WegNots - Sistema de Monitoramento de E-mails e Notificações

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/mongodb-5.0+-47A248.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)
[![SOLID](https://img.shields.io/badge/principles-SOLID-orange.svg)](https://en.wikipedia.org/wiki/SOLID)
[![DevOps](https://img.shields.io/badge/practices-DevOps-blueviolet.svg)](https://aws.amazon.com/devops/what-is-devops/)

![Última Atualização](https://img.shields.io/badge/última_atualização-Abril_2025-informational)

Sistema eficiente para monitoramento de e-mails IMAP e envio de notificações via Telegram, desenvolvido com foco em robustez, escalabilidade e seguindo boas práticas de desenvolvimento.

---

## 🚀 Novidades na Versão Atual (Abril 2025)

### ✨ Interface Administrativa (Front-end)
- **Dashboard Completo**: Visualize todos os usuários, status dos serviços e estatísticas em tempo real
- **Login Seguro**: Sistema de autenticação com usuário admin padrão para primeiro acesso
- **Menu Lateral**: Navegação intuitiva entre diferentes seções do sistema
- **Responsividade**: Interface adaptada para dispositivos móveis e desktop
- **Gestão de Usuários**: Visualize e gerencie usuários cadastrados para receber notificações

### 🔐 Sistema de Autenticação
- **Login Padrão**: Acesse com usuário `admin` e senha `admin` para primeiro uso
- **Logout Funcional**: Encerre sua sessão com segurança
- **Proteção de Rotas**: Acesso restrito a usuários autenticados
- **Token JWT**: Autenticação moderna baseada em tokens

### 🌐 Arquitetura Full-Stack
- **Backend Python**: Monitoramento robusto com Python e MongoDB
- **Frontend React**: Interface moderna com React, Vite e Material UI
- **Comunicação API**: Integração backend-frontend via API RESTful
- **Docker Compose**: Facilidade para executar todo o ambiente com um único comando

---

## 📋 Características Principais

### 🔒 **Conexão IMAP Robusta**: 
- Conexão segura via SSL/TLS
- Reconexão automática com backoff exponencial
- Tratamento refinado de falhas temporárias

### 📲 **Notificações Multicanal**:
- Formatação rica de mensagens com Markdown
- Suporte a emojis para melhor visualização
- Sistema de retry avançado com backoff exponencial
- Tratamento robusto de erros de rede (incluindo 502 Bad Gateway)
- Mensagens de status do sistema (inicialização/encerramento)
- Roteamento inteligente de mensagens baseado em remetentes
- Interface de notificação extensível (NotificationClient)
- Suporte atual para:
  - Telegram (com suporte a múltiplos chat IDs)
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

---

## 📋 Pré-requisitos

- Python 3.9+ (para o backend)
- Node.js 16+ (para o frontend)
- MongoDB 5.0+
- Git
- Conta de e-mail com IMAP habilitado
- Bot do Telegram criado via [@BotFather](https://t.me/BotFather)
- Docker e Docker Compose (recomendado para facilitar a instalação)

---

## 🚀 Guia Passo a Passo para Iniciantes

### 1️⃣ Preparando o Ambiente

#### Instalação Manual (sem Docker)

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/wegnots.git
cd wegnots
```

**2. Configure o Backend (Python)**
```bash
# Crie e ative um ambiente virtual
python -m venv .venv

# No Windows
.venv\Scripts\activate

# No macOS/Linux
source .venv/bin/activate

# Instale as dependências
cd monitor
pip install -r requirements.txt
```

**3. Configure o Frontend (React)**
```bash
# Instale as dependências do frontend
cd ../wegnots-admin
npm install
```

**4. Configure o MongoDB**
- Instale o MongoDB seguindo a [documentação oficial](https://www.mongodb.com/docs/manual/installation/)
- Inicie o serviço do MongoDB

#### Instalação com Docker (Recomendado)

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/wegnots.git
cd wegnots
```

**2. Inicie com Docker Compose**
```bash
docker-compose up -d
```
Isso iniciará automaticamente o backend, frontend e MongoDB em containers separados.

### 2️⃣ Configuração do Sistema

**1. Configuração do Bot Telegram**
- Crie um bot usando o [@BotFather](https://t.me/BotFather) no Telegram
- Anote o token gerado

**2. Configuração do E-mail IMAP**
- Certifique-se de que sua conta de e-mail tem IMAP habilitado
- Para Gmail, você precisa ativar o "Acesso a app menos seguro" ou usar senhas de app

**3. Configure as Variáveis de Ambiente**
- Crie um arquivo `.env` na pasta `monitor` com as seguintes variáveis:

```
IMAP_SERVER=imap.seuservidor.com
IMAP_PORT=993
IMAP_USER=seu@email.com
IMAP_PASSWORD=sua_senha
TELEGRAM_TOKEN=SEU_TOKEN_DO_BOT
TELEGRAM_CHAT_ID=SEU_CHAT_ID_DO_TELEGRAM
MONGODB_URI=mongodb://localhost:27017/wegnots
```

### 3️⃣ Executando a Aplicação

#### Executando Manualmente

**1. Inicie o Backend**
```bash
cd monitor
python main.py
```

**2. Inicie o Frontend em outro terminal**
```bash
cd wegnots-admin
npm run dev
```

#### Obtendo seu Chat ID do Telegram

1. Inicie uma conversa com seu bot
2. Envie o comando `/start`
3. Acesse `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Localize o valor `chat_id` na resposta JSON

### 4️⃣ Acessando o Sistema

1. Abra o navegador e acesse: `http://localhost:5173`
2. Faça login com as credenciais padrão:
   - Usuário: `admin`
   - Senha: `admin`
3. Você será direcionado para o Dashboard principal

### 5️⃣ Testando o Sistema

1. **Para testar o monitoramento de e-mails**:
   - Envie um e-mail para a conta configurada com palavras como "urgente" ou "crítico" no assunto
   - Observe o bot do Telegram enviar uma notificação

2. **Para testar o encerramento gracioso**:
   - Pressione `Ctrl+C` no terminal onde o backend está rodando
   - Observe a mensagem de encerramento no Telegram

---

## 🔧 Resolução de Problemas Comuns

### Problema: Não recebo notificações no Telegram
- Verifique se o token do bot está correto
- Confirme se o chat_id está configurado corretamente
- Verifique os logs em `wegnots.log` para detalhes específicos

### Problema: Não consigo me conectar ao servidor IMAP
- Confirme que as credenciais estão corretas
- Verifique se o IMAP está habilitado na sua conta de e-mail
- Para Gmail, verifique as configurações de segurança

### Problema: O frontend não inicia
- Verifique se Node.js está instalado corretamente
- Confirme que as dependências foram instaladas com `npm install`
- Verifique os logs do terminal para erros específicos

### Problema: O MongoDB não conecta
- Verifique se o serviço do MongoDB está em execução
- Confirme a URL de conexão no arquivo `.env`
- Tente se conectar manualmente com um cliente MongoDB

---

## 📈 Estrutura de Pastas do Projeto

```
wegnots/
├── monitor/                # Backend Python
│   ├── app/
│   │   ├── core/           # Lógica principal
│   │   ├── config/         # Configurações
│   ├── main.py             # Ponto de entrada do backend
│   └── docker-compose.yml  # Configuração Docker
├── wegnots-admin/          # Frontend React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── context/        # Context API (autenticação, etc.)
│   │   ├── layouts/        # Layouts da aplicação
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── services/       # Serviços e API
│   ├── package.json        # Dependências do frontend
```

---

## 📈 Recursos Avançados

### 🚨 Tipos de Alerta

O sistema categoriza os e-mails em três níveis baseados no assunto:

- **Alerta Crítico (1)**: Identificado por palavras como "urgente", "crítico", "emergência"
- **Alerta Moderado (2)**: Identificado por palavras como "importante", "atenção"
- **Alerta Leve (3)**: Demais e-mails sem palavras-chave específicas

### 📊 Dashboard Administrativo

A interface administrativa oferece:

- **Visão Geral**: Status dos serviços e estatísticas
- **Usuários**: Lista de usuários cadastrados para receber notificações
- **Logs**: Visualização de eventos e alertas recentes
- **Configurações**: Ajustes do sistema e preferências

---

## 🤝 Contribuições

Contribuições são super bem-vindas! Se quiser contribuir:

1. Faça um Fork do projeto
2. Crie uma Branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Faça commit das suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Faça Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é licenciado sob a licença Apache-2.0.  
Veja o arquivo `LICENSE` para mais detalhes.  

---

Desenvolvido com ❤️ pela equipe MegaSec.
Para suporte, contate-nos em suporte@megasec.com.br
