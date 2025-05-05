# 🌟 WegNots - Sistema de Monitoramento de E-mails e Notificações

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-339933.svg)](https://nodejs.org/)
[![Vite](https://img.shields.io/badge/vite-powered-646CFF.svg)](https://vitejs.dev/)
[![Material-UI](https://img.shields.io/badge/mui-styled-007FFF.svg)](https://mui.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-5.0+-47A248.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)

![Última Atualização](https://img.shields.io/badge/última_atualização-Maio_2025-informational)

Sistema profissional para monitoramento de e-mails IMAP e envio de notificações via Telegram, desenvolvido com foco em robustez, escalabilidade e seguindo boas práticas de desenvolvimento.

---

# Guia de Instalação e Configuração

## Pré-requisitos do Sistema

Antes de começar, certifique-se de que seu sistema atende aos seguintes requisitos:

1. **Sistema Operacional**:
   - Windows 10/11, Linux (Ubuntu 20.04+) ou macOS
   - Mínimo de 4GB de RAM
   - 10GB de espaço em disco

2. **Software Necessário**:
   - Git
   - Docker Desktop (Windows/Mac) ou Docker Engine + Docker Compose (Linux)
   - Python 3.9 ou superior

## Passo a Passo para Instalação

### 1. Preparação do Ambiente

```bash
# Windows
# 1. Instale o Docker Desktop: https://www.docker.com/products/docker-desktop
# 2. Instale o Python: https://www.python.org/downloads/
# 3. Instale o Git: https://git-scm.com/download/win

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install -y docker.io docker-compose python3 python3-pip git
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Download do Projeto

```bash
# Clone o repositório
git clone https://github.com/megasec/wegnots.git
cd wegnots

# Em caso de download direto, descompacte o arquivo e navegue até a pasta
```

### 3. Configuração Inicial

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

### 4. Configuração do Telegram

Antes de continuar, você precisará:

1. Criar um bot no Telegram:
   - Abra o Telegram e procure por "@BotFather"
   - Digite /newbot e siga as instruções
   - Guarde o token fornecido

2. Obter seu Chat ID:
   - Procure por "@RawDataBot" no Telegram
   - Inicie uma conversa e guarde o "Chat ID" fornecido

### 5. Configuração do Sistema

```bash
# Windows
python monitor/config_manager.py

# Linux/Mac
python3 monitor/config_manager.py
```

No menu interativo:
1. Escolha a opção 5 (Configurar Telegram)
2. Insira o token do bot e o chat ID obtidos anteriormente
3. Escolha a opção 2 (Adicionar novo e-mail)
4. Siga as instruções para adicionar suas contas de e-mail

### 6. Verificação da Instalação

```bash
# Windows
health_check.bat

# Linux/Mac
./health_check.sh
```

### 7. Acesso ao Sistema

- Abra um navegador e acesse: `http://localhost:5173`
- Faça login com as credenciais padrão:
  - Usuário: admin
  - Senha: admin123
  - **Importante**: Altere a senha no primeiro acesso

## Instalação em Ambiente Cloud (Azure, AWS, GCP)

### Azure VM

1. Crie uma VM:
   - Tamanho recomendado: B2s (2 vCPUs, 4GB RAM)
   - SO: Ubuntu Server 20.04 LTS
   - Abra as portas: 80, 443, 5173, 27017 (se necessário)

2. Conecte-se à VM:
   ```bash
   ssh seu_usuario@ip_da_vm
   ```

3. Instale as dependências:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose python3 python3-pip git
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

4. Siga os passos 2-7 da instalação normal

### Considerações para Ambiente Produtivo

1. **Segurança**:
   - Use HTTPS para o painel admin
   - Configure um firewall
   - Use senhas fortes
   - Mantenha o sistema atualizado

2. **Backup**:
   ```bash
   # Backup do MongoDB
   docker-compose exec mongodb mongodump --out /backup
   
   # Backup das configurações
   cp config.ini config.ini.backup
   cp monitor/config.ini monitor/config.ini.backup
   ```

3. **Monitoramento**:
   - Configure alertas de uso de recursos
   - Monitore os logs regularmente
   - Verifique o status do sistema diariamente

## Componentes do Sistema

- **MongoDB Database**: Armazena dados da aplicação
- **Monitor Service**: Serviço Python que monitora emails
- **Admin Panel**: Interface web para gerenciamento
- **Configuration Manager**: Ferramenta interativa de configuração

## Gerenciamento do Sistema

### Iniciando o Sistema

- Execute `start.bat` (Windows) ou `./start.sh` (Linux/Mac)
- O script verifica se o Docker está rodando
- Status do sistema é exibido após a inicialização

### Configurando o Sistema

- Use o gerenciador de configuração:
  ```bash
  python monitor/config_manager.py
  ```
- Opções disponíveis:
  - Listar emails monitorados
  - Adicionar/remover contas
  - Editar configurações
  - Configurar notificações
  - Testar conexões

### Monitoramento de Saúde

- Execute `health_check.bat` ou `./health_check.sh`
- Verifica:
  - Status dos containers
  - Acessibilidade da API
  - Conectividade do banco
  - Disponibilidade da UI

### Desligando o Sistema

- Execute `stop.bat` ou `./stop.sh`
- Envia notificações de encerramento
- Para todos os containers

## Resolução de Problemas

### Problemas Comuns

1. **Serviços não iniciam**:
   - Verifique o Docker: `docker ps`
   - Veja os logs: `docker-compose logs -f`

2. **Problemas de configuração**:
   - Verifique config.ini
   - Use o gerenciador de configuração
   - Teste as notificações

3. **Monitoramento de email não funciona**:
   - Verifique configurações IMAP
   - Para Gmail, permita apps menos seguros
   - Teste conexão de rede

### Logs

- Logs do monitor: `monitor/logs/`
- Logs de configuração: `logs/config_manager.log`
- Logs dos containers:
  ```bash
  docker-compose logs -f
  docker-compose logs -f monitor
  docker-compose logs -f mongodb
  docker-compose logs -f admin
  ```

## Considerações de Segurança

- Proteja o arquivo config.ini
- Use variáveis de ambiente em produção
- MongoDB acessível apenas na rede Docker
- Configure tokens e chat IDs específicos por email

---

Desenvolvido com ❤️ pela equipe MegaSec.
Para suporte, contate-nos em suporte@megasec.com.br
