@echo off
echo =======================================================
echo            ENCERRAMENTO DO SISTEMA WEGNOTS
echo =======================================================
echo.

REM Store current directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Docker is installed and running
echo Verificando se o Docker está em execução...
docker ps > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Docker não está em execução.
    echo Os serviços podem já estar parados.
    pause
    exit /b 1
)

echo Parando todos os serviços do WegNots...
echo.

REM Shutdown services with proper notification
echo Enviando notificações de encerramento...
docker exec monitor python -c "from config_manager import load_config, send_system_shutdown_notification; config = load_config(); send_system_shutdown_notification(config)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Aviso: Não foi possível enviar notificação de encerramento. Continuando com o encerramento...
)

REM Stop the services with Docker Compose (with explicit compose file)
echo Parando todos os serviços com Docker Compose...
docker-compose -f "%SCRIPT_DIR%docker-compose.yml" down --timeout 30

REM Double check if containers are still running
echo Verificando se todos os contêineres foram encerrados...
docker ps | findstr /C:"mongodb-new" /C:"monitor" /C:"wegnots" > nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Alguns contêineres ainda estão em execução. Forçando o encerramento...
    
    REM Force stop containers
    echo Forçando parada dos contêineres...
    FOR %%c IN (wegnots monitor mongodb-new) DO (
        echo Parando %%c...
        docker stop %%c 2>nul
        
        REM Wait a moment for container to stop
        timeout /t 2 /nobreak > nul
        
        echo Removendo %%c...
        docker rm -f %%c 2>nul
    )
    
    REM Final verification
    echo Verificação final dos contêineres...
    docker ps | findstr /C:"mongodb-new" /C:"monitor" /C:"wegnots" > nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        echo AVISO: Alguns contêineres ainda podem estar em execução.
        echo Execute 'docker ps' para verificar o status.
    ) ELSE (
        echo Todos os contêineres foram encerrados com sucesso.
    )
)

echo.
echo =======================================================
echo Sistema WegNots foi encerrado!
echo.
echo Para iniciar o sistema novamente, use:
echo   - start.bat
echo =======================================================
echo.

REM Display current container status
echo Status atual dos contêineres:
docker ps
echo.
pause
