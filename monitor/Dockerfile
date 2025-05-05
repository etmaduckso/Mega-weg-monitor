# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and locales
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales \
    wget \
    curl \
    iputils-ping \
    procps \
    && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && locale-gen pt_BR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Set locale environment variables
ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV TZ=America/Sao_Paulo
ENV PYTHONUNBUFFERED=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p logs uploads

# Verifica se o MongoDB está online antes de iniciar
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Adiciona health check interno
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Define o entrypoint para iniciar o serviço
ENTRYPOINT ["/entrypoint.sh"]

# Para modo de desenvolvimento/debug, use:
CMD ["python", "main.py"]
