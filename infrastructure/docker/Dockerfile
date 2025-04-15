FROM python:3.9-slim

LABEL maintainer="WegNots Team" \
      description="Monitor de E-mails com Notificações Telegram" \
      version="1.0.0"

# Define variáveis de ambiente não interativas
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Cria diretório para logs com as permissões corretas
RUN mkdir -p /app/logs && \
    chown -R 1000:1000 /app/logs

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências em uma camada separada
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY . .

# Define usuário não-root para execução
USER 1000

# Comando para executar ao iniciar o container
CMD ["python", "-u", "/app/main.py"]

# Metadata do container
HEALTHCHECK --interval=1m --timeout=30s --start-period=30s --retries=3 \
  CMD python -c "import requests; requests.get('https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe')" || exit 1
