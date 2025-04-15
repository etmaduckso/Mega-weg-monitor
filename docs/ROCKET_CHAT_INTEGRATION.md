# Integração com RocketChat

Este documento detalha como configurar e utilizar a integração do WegNots com o RocketChat para envio de notificações de e-mails.

## Visão Geral

O WegNots suporta o envio de notificações para o RocketChat, permitindo que alertas de e-mails sejam enviados para canais ou usuários específicos. Esta integração é particularmente útil em ambientes corporativos onde o RocketChat é utilizado como plataforma de comunicação interna.

## Métodos de Integração

Existem duas formas de integrar o WegNots com o RocketChat:

1. **API REST**: Utilizando a API REST do RocketChat com autenticação via token
2. **Webhooks**: Utilizando webhooks do RocketChat para envio de mensagens sem autenticação

## Configuração

### Pré-requisitos

- Instância do RocketChat em execução (local ou remota)
- Usuário com permissões para enviar mensagens
- Canal ou usuário para receber as notificações

### Configuração via API REST

1. **Obtenha as credenciais de API**:
   - Acesse seu perfil no RocketChat (clique no avatar no canto superior direito)
   - Vá para "Minha Conta" > "Segurança" > "Personal Access Tokens"
   - Crie um novo token com escopo "user" (e "admin" se necessário)
   - Anote o User ID e o Token gerado

2. **Configure o WegNots**:
   
   No arquivo `config.py`:
   ```python
   ROCKETCHAT_CONFIG = {
       'url': 'http://seu-servidor-rocketchat:3000',
       'user_id': 'seu-user-id',
       'token': 'seu-token',
       'channel': 'nome-do-canal'  # ou '@username' para mensagem direta
   }
   ```

   Ou usando variáveis de ambiente no arquivo `.env`:
   ```
   ROCKETCHAT_URL=http://seu-servidor-rocketchat:3000
   ROCKETCHAT_USER_ID=seu-user-id
   ROCKETCHAT_TOKEN=seu-token
   ROCKETCHAT_CHANNEL=nome-do-canal
   ```

### Configuração via Webhook

1. **Crie um webhook no RocketChat**:
   - Acesse "Administração" > "Integrações" > "Novo" > "Webhook de Entrada"
   - Configure um nome, canal de destino e ative a integração
   - Personalize o nome de usuário e avatar do bot (opcional)
   - Salve a integração e copie a URL do webhook gerada

2. **Configure o WegNots**:
   
   No arquivo `config.py`:
   ```python
   ROCKETCHAT_CONFIG = {
       'webhook_url': 'http://seu-servidor-rocketchat:3000/hooks/seu-webhook-token'
   }
   ```

   Ou usando variáveis de ambiente no arquivo `.env`:
   ```
   ROCKETCHAT_WEBHOOK_URL=http://seu-servidor-rocketchat:3000/hooks/seu-webhook-token
   ```

## Testando a Integração

Para testar se a integração está funcionando corretamente, execute o script de teste:

```bash
python rocketchat_test.py
```

Este script enviará mensagens de teste para o canal configurado, incluindo:
- Uma mensagem simples de texto
- Uma mensagem formatada com Markdown
- Um alerta simulado de e-mail

## Formato das Mensagens

As mensagens enviadas para o RocketChat são formatadas usando Markdown, permitindo:

- **Títulos** com diferentes níveis
- Texto em **negrito** e *itálico*
- Listas ordenadas e não ordenadas
- Blocos de código
- Emojis para melhor visualização

### Exemplo de Mensagem de Alerta

```
## 🚨 Alerta Crítico: Novo E-mail Urgente

**De:** exemplo@empresa.com
**Assunto:** Problema crítico no servidor de produção
**Data:** 2023-05-15 14:30:45

### Conteúdo:
O servidor de produção está apresentando instabilidade. 
Necessário verificar imediatamente.

---
*Este alerta foi gerado automaticamente pelo WegNots*
```

## Solução de Problemas

### Problemas Comuns

1. **Erro de Autenticação**:
   - Verifique se o User ID e Token estão corretos
   - Confirme se o token não expirou
   - Verifique se o usuário tem permissões suficientes

2. **Mensagens não Aparecem**:
   - Verifique se o canal existe e está escrito corretamente
   - Confirme se o usuário tem permissão para enviar mensagens no canal
   - Para mensagens diretas, certifique-se de usar o formato '@username'

3. **Erro de Conexão**:
   - Verifique se a URL do RocketChat está correta e acessível
   - Confirme se não há bloqueios de firewall ou proxy

### Logs de Depuração

Para habilitar logs detalhados da integração com RocketChat, configure o nível de log para DEBUG:

```python
# No config.py
LOG_LEVEL = 'DEBUG'
```

Ou no arquivo `.env`:
```
LOG_LEVEL=DEBUG
```

## Configuração Avançada

### Personalização de Mensagens

É possível personalizar o formato das mensagens enviadas para o RocketChat modificando o arquivo `app/core/rocketchat_client.py`.

### Configuração de Proxy

Se sua rede utiliza proxy, configure-o nas variáveis de ambiente:

```
HTTP_PROXY=http://seu-proxy:porta
HTTPS_PROXY=http://seu-proxy:porta
```

### Timeout e Retry

É possível configurar o timeout e a política de retry para envio de mensagens:

```python
# No config.py
ROCKETCHAT_CONFIG = {
    # ... outras configurações ...
    'timeout': 10,  # segundos
    'max_retries': 3,
    'retry_delay': 2  # segundos
}
```

## Referências

- [Documentação da API do RocketChat](https://developer.rocket.chat/reference/api)
- [Guia de Webhooks do RocketChat](https://docs.rocket.chat/guides/administration/admin-panel/integrations)
- [Sintaxe Markdown suportada pelo RocketChat](https://docs.rocket.chat/guides/user-guides/messaging)
