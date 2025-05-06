# WegNots - Sistema de Monitoramento de E-mails

[Conteúdo anterior mantido...]

## 🔒 Segurança

### Configuração Segura do Ambiente

1. **Configuração Inicial**
```bash
# Clone o repositório
git clone [url-do-repositorio]

# Entre no diretório
cd monitor

# Copie o arquivo de exemplo de configuração
cp .env.example .env

# Edite o arquivo .env com suas credenciais
nano .env
```

2. **Proteção de Credenciais**
- NUNCA commit o arquivo `.env`
- NUNCA compartilhe tokens ou senhas
- Use o arquivo `.env.example` como template
- Mantenha credenciais apenas no arquivo `.env`

3. **Boas Práticas**
- Consulte o arquivo `SECURITY.md` para diretrizes completas de segurança
- Siga as recomendações de segurança ao configurar o ambiente
- Mantenha logs e backups protegidos
- Atualize regularmente as dependências

[Resto do conteúdo mantido...]
