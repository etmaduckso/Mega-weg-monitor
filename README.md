# 🌟 **WegNots - Sistema de Monitoramento de E-mails** 📧🚀

[![🐍 Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)  
[![🐳 Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)

🎉 Bem-vindo ao **WegNots**! Um sistema incrível para monitoramento de e-mails IMAP e envio de notificações via Telegram. Desenvolvido com foco em robustez, escalabilidade e boas práticas! 💪✨

---

## ✨ **Características Principais** ✨

- 🔒 **Conexão IMAP Segura**:  
  🔑 SSL/TLS, reconexão automática e tratamento de falhas.  
- 📲 **Notificações via Telegram**:  
  📝 Mensagens formatadas com Markdown e emojis divertidos!  
- 🛠 **Arquitetura Profissional**:  
  🧹 Código limpo, modular e pronto para produção.  
- 🐳 **Compatível com Docker**:  
  🚀 Fácil de implantar em qualquer ambiente.  

---

## 📋 **Pré-requisitos** 🛠

- 🐍 **Python 3.9+**  
- 📧 **Conta de e-mail com IMAP habilitado**  
- 🤖 **Bot do Telegram criado via [@BotFather](https://t.me/BotFather)**  
- 🐳 **Docker (opcional)**  

---

## 🚀 **Como Configurar** ⚙️

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

## 🧪 **Testes** 🧪

- **Teste de conexão IMAP**:  
  ```bash
  python test_imap_connection.py
  ```
- **Teste do Telegram**:  
  ```bash
  python telegram_test.py
  ```

---

## 🏗 **Estrutura do Projeto** 🏗

```
wegnots/
├── app/
│   ├── core/               # Lógica principal 🧠
│   ├── config/             # Configurações ⚙️
├── tests/                  # Testes automatizados ✅
├── docs/                   # Documentação 📚
├── main.py                 # Ponto de entrada 🚀
├── Dockerfile              # Configuração do Docker 🐳
├── README.md               # Este arquivo ✨
```

---

## 🐳 **Executando com Docker** 🐳

1️⃣ **Construa e inicie o container**:  
```bash
docker-compose up --build
```

2️⃣ **Execute em segundo plano**:  
```bash
docker-compose up -d
```

---

## 📈 **Logs e Monitoramento** 📊

- 📂 Os logs são salvos no arquivo wegnots.log.  
- 🔍 Incluem informações detalhadas sobre conexões, notificações e erros.  

---

## 🤝 **Contribuições** 💡

Contribuições são super bem-vindas! 🌟  
Leia nosso guia de contribuição para saber mais.  

---

## 📝 **Licença** 📜

Este projeto é licenciado sob a licença MIT. 🛡️  
Veja o arquivo `LICENSE` para mais detalhes.  

---

Espero que goste desta versão cheia de emojis! 🌟 Se precisar de mais ajustes, é só avisar! 😊
