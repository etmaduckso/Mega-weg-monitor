# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Não lançado]

### Adicionado

- Arquivo CHANGELOG.md para rastrear mudanças no projeto
- Arquivo .gitattributes para garantir consistência nos finais de linha
- Arquivo CODE_OF_CONDUCT.md para estabelecer diretrizes de comportamento da comunidade
- Arquivo CONTRIBUTING.md com instruções para contribuidores
- Configuração inicial do GitHub Actions para CI/CD
- Arquivo Dockerfile para containerização do projeto
- Arquivo .pylintrc para configuração do linter

### Modificado

- Atualização do README.md com informações mais detalhadas sobre o projeto e como contribuir
- Refinamento da estrutura do projeto para melhor organização

## [1.1.0] - 2025-04-15

### Adicionado
- Mensagem de inicialização do sistema no Telegram com status dos serviços
- Sistema de retry avançado com backoff exponencial para erros de rede
- Suporte a múltiplos chat IDs no Telegram
- Roteamento inteligente de mensagens baseado em remetentes
- Tratamento específico para erros 502/503/504 (Gateway/Service Unavailable)
- Configurações flexíveis para tentativas e delays
- Grupos de destinatários configuráveis
- Logging detalhado do processo de retry

### Modificado
- Melhorado o sistema de tratamento de erros do Telegram
- Atualizada a lógica de reconexão para usar backoff exponencial
- Aprimorada a formatação das mensagens do Telegram
- Otimizado o gerenciamento de chat IDs

### Corrigido
- Corrigido problema com timeout em conexões lentas
- Resolvido issue com mensagens duplicadas
- Ajustado tratamento de rate limiting do Telegram

## [1.0.0] - AAAA-MM-DD

### Adicionado

- Funcionalidade inicial de monitoramento de e-mails IMAP
- Integração com Telegram para envio de notificações
- Sistema de logging detalhado
- Configuração via arquivo config.py e variáveis de ambiente
- Testes de conexão para IMAP e Telegram

[Não lançado]: https://github.com/seu-usuario/wegnots/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/seu-usuario/wegnots/releases/tag/v1.1.0
[1.0.0]: https://github.com/seu-usuario/wegnots/releases/tag/v1.0.0
