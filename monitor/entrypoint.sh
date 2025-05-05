#!/bin/bash
set -e

echo "======================================================="
echo "             INICIANDO SERVIÇO MONITOR"
echo "======================================================="

# Cria os diretórios necessários
echo "Criando diretórios de logs e uploads..."
mkdir -p logs uploads
touch logs/wegnots.log
chmod -R 777 logs uploads

# Espera o MongoDB inicializar
echo "Aguardando 10 segundos para garantir que o MongoDB tenha tempo de inicializar..."
sleep 10

# Exibe o URI original para debug
echo "URI original do MongoDB: $MONGODB_URI"

# Verifica e corrige o URI do MongoDB se necessário
if [[ "$MONGODB_URI" != *"@mongodb-new:"* && "$MONGODB_URI" == *"@mongodb:"* ]]; then
    echo "Corrigindo o URI do MongoDB para apontar para o host correto..."
    export MONGODB_URI=$(echo "$MONGODB_URI" | sed 's/@mongodb:/@mongodb-new:/g')
    echo "URI corrigido: $MONGODB_URI"
elif [[ "$MONGODB_URI" != *"@mongodb-new:"* && "$MONGODB_URI" != *"@mongodb:"* ]]; then
    echo "AVISO: URI do MongoDB não contém o padrão esperado. URI atual: $MONGODB_URI"
    echo "Tentando prosseguir com o URI fornecido..."
fi

# Função para verificar a conexão com o MongoDB
check_mongodb() {
    echo "Verificando conexão com MongoDB em: $MONGODB_URI"
    
    # Tenta usar o pymongo para verificar a conexão
    python -c "
import sys, pymongo, time
try:
    print('Iniciando tentativa de conexão via pymongo...')
    client = pymongo.MongoClient('$MONGODB_URI', serverSelectionTimeoutMS=5000)
    info = client.server_info()
    db_version = info.get('version', 'desconhecida')
    print(f'Conexão com MongoDB bem-sucedida! Versão: {db_version}')
    dbs = client.list_database_names()
    print(f'Bancos de dados disponíveis: {dbs}')
    sys.exit(0)
except Exception as e:
    print(f'Erro ao conectar ao MongoDB: {e}')
    sys.exit(1)
"
    return $?
}

# Tenta conectar ao MongoDB com várias tentativas
max_retries=30  # Aumentado para 30 tentativas
current_attempt=1
success=0
connection_timeout=3  # Tempo entre tentativas em segundos

echo "Iniciando tentativas de conexão com o MongoDB..."
while [ $current_attempt -le $max_retries ] && [ $success -eq 0 ]; do
    echo "Tentativa $current_attempt de $max_retries..."
    
    if check_mongodb; then
        echo "MongoDB está disponível e respondendo!"
        success=1
    else
        echo "MongoDB ainda não está pronto. Tentando novamente em $connection_timeout segundos..."
        sleep $connection_timeout
        current_attempt=$((current_attempt + 1))
    fi
done

# Verifica status da rede
echo "Verificando conectividade de rede..."
ping -c 2 mongodb-new || echo "Não foi possível pingar o host mongodb-new"
ping -c 2 8.8.8.8 || echo "Não foi possível acessar a internet"

# Mesmo se falhar na conexão com MongoDB, continua tentando iniciar o serviço
if [ $success -eq 0 ]; then
    echo "AVISO: Não foi possível conectar ao MongoDB após $max_retries tentativas."
    echo "Verificando informações da rede Docker:"
    hostname -i
    cat /etc/hosts
    
    echo "Tentando inicializar o serviço mesmo sem conexão confirmada com o MongoDB..."
    echo "O serviço tentará reconectar-se ao MongoDB automaticamente."
    
    # Criamos um arquivo flag para indicar problema na inicialização
    echo "$(date) - Falha na conexão inicial com MongoDB" > logs/startup_issue.log
else
    echo "Conexão com MongoDB estabelecida com sucesso!"
    # Removemos o arquivo flag se existir
    rm -f logs/startup_issue.log
fi

echo "Iniciando aplicação principal..."
echo "Comando: $@"

# Executa o comando principal (normalmente python main.py)
exec "$@"