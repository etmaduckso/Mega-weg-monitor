@echo off
echo =======================================================
echo            INICIALIZAÇÃO DO SISTEMA WEGNOTS
echo =======================================================
echo.

REM Check if Docker is installed and running
echo Verificando se o Docker está instalado e em execução...
docker --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Docker não está instalado ou não está no PATH.
    echo Por favor, instale o Docker Desktop em https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker is running
docker ps > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Docker não está em execução.
    echo Por favor, inicie o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo Docker está funcionando corretamente.
echo.

REM Check if python is installed
echo Verificando se o Python está instalado...
python --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo AVISO: Python não está instalado ou não está no PATH.
    echo Alguns utilitários e scripts podem não funcionar adequadamente.
    echo Python 3.9+ é recomendado para funcionalidade completa.
    echo.
) ELSE (
    echo Python está instalado corretamente.
    echo.
)

REM Check for config.ini file in monitor directory
IF NOT EXIST "monitor\config.ini" (
    echo AVISO: Arquivo de configuração 'monitor\config.ini' não encontrado.
    echo Uma configuração padrão será criada durante a inicialização.
    echo Você pode configurar seus e-mails e configurações do Telegram depois.
    echo.
)

REM Set mode (production or development)
set /p MODE="Executar em modo de desenvolvimento? [S/N] (modo de desenvolvimento ativa o hot-reloading): "
IF /I "%MODE%"=="S" (
    set ENV_MODE=development
) ELSE (
    set ENV_MODE=production
)
echo.

REM Ask for email configuration
set SETUP_EMAILS=
set /p SETUP_EMAILS="Deseja configurar o monitoramento de e-mail agora? [S/N]: "
IF /I "%SETUP_EMAILS%"=="S" (
    call :setup_email_config
)
echo.

echo Iniciando componentes do sistema WegNots...
echo Isso pode levar alguns minutos na primeira execução enquanto as imagens Docker são baixadas.
echo.

REM Limpeza completa de todos os contêineres relacionados ao WegNots
echo Removendo contêineres e redes antigos para garantir uma inicialização limpa...
docker-compose down --volumes --remove-orphans

REM Forçar remoção de contêineres com o mesmo nome caso estejam travados
for %%c in (mongodb-new monitor wegnots) do (
    echo Tentando remover contêiner %%c caso exista...
    docker rm -f %%c 2>nul
)

REM Aguardar a limpeza completa
echo Aguardando 5 segundos para garantir que tudo foi removido corretamente...
timeout /t 5 /nobreak > nul

REM Iniciando serviços com restart: sempre e reconstruindo as imagens
echo Reconstruindo e iniciando os serviços com Docker Compose...
docker-compose build --no-cache
docker-compose up -d --force-recreate

echo.
echo Verificando a saúde dos serviços...
echo Esperando os serviços ficarem saudáveis (até 5 minutos)...
set SERVICES_OK=1
set RETRIES=30
set WAIT_SECONDS=10

:check_health
set SERVICES_OK=1
for %%c in (mongodb-new monitor wegnots) do (
    for /f "tokens=*" %%h in ('docker inspect --format="{{.State.Health.Status}}" %%c') do (
        if NOT "%%h"=="healthy" (
            echo Serviço %%c não está saudável ainda (status: %%h).
            set SERVICES_OK=0
        ) else (
            echo Serviço %%c está saudável.
        )
    )
)

if %SERVICES_OK%==1 (
    goto health_ok
) else (
    set /a RETRIES-=1
    if %RETRIES% LEQ 0 (
        goto health_fail
    )
    echo Aguardando %WAIT_SECONDS% segundos antes de nova verificação...
    timeout /t %WAIT_SECONDS% /nobreak > nul
    goto check_health
)

:health_fail
echo.
echo ATENÇÃO: Nem todos os serviços ficaram saudáveis no tempo esperado.
echo Exibindo logs completos para diagnóstico:
echo.
echo === Logs do serviço MongoDB ===
docker-compose logs --tail=50 mongodb-new
echo.
echo === Logs do serviço Monitor ===
docker-compose logs --tail=50 monitor
echo.
echo === Logs do serviço Admin ===
docker-compose logs --tail=50 wegnots
echo.
echo Executando diagnóstico de rede entre contêineres...
docker network inspect wegnots-network
echo.
echo Dicas para solução de problemas:
echo 1. Verifique se todas as portas necessárias estão disponíveis (27017, 5000, 5173)
echo 2. Verifique se há algum antivírus ou firewall bloqueando as conexões
echo 3. Execute 'docker-compose logs -f' para acompanhar os logs em tempo real
echo 4. Verifique o arquivo de configuração do MongoDB
echo.
pause
echo.
echo Tentando reiniciar os serviços...
docker-compose restart
echo.
echo Verificando novamente os serviços após a reinicialização...
timeout /t 15 /nobreak > nul
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
goto end

:health_ok
echo.
echo =======================================================
echo Sistema WegNots foi iniciado com sucesso!
echo.
echo Você pode acessar a interface de administração em: http://localhost:5173
echo API do Monitor disponível em: http://localhost:5000
echo MongoDB disponível em: localhost:27017
echo.
echo Para monitorar os logs, use:
echo   - docker-compose logs -f
echo.
echo Para parar o sistema, use:
echo   - stop.bat ou docker-compose down
echo =======================================================
echo.

:end
pause
exit /b 0

:setup_email_config
echo.
echo =======================================================
echo               CONFIGURAÇÃO DE E-MAIL
echo =======================================================
echo.
echo Por favor, forneça seu token de Bot do Telegram e ID do Chat para notificações.
echo Você pode obter um token de Bot através do BotFather no Telegram.
echo.
set /p BOT_TOKEN="Token do Bot Telegram: "
set /p CHAT_ID="ID do Chat Telegram: "

REM Create or update config.ini
IF NOT EXIST "monitor\config.ini" (
    echo [TELEGRAM] > monitor\config.ini
    echo token=%BOT_TOKEN% >> monitor\config.ini
    echo chat_id=%CHAT_ID% >> monitor\config.ini
    echo. >> monitor\config.ini
) ELSE (
    REM Update existing config
    powershell -Command "(Get-Content monitor\config.ini) -replace '(?<=token=).*', '%BOT_TOKEN%' -replace '(?<=chat_id=).*', '%CHAT_ID%' | Set-Content monitor\config.ini"
)

echo.
echo Configurações do Telegram salvas. Você pode adicionar contas de e-mail depois através do config_manager.py
echo ou editando o config.ini diretamente.
echo.
exit /b 0