@echo off
echo =======================================================
echo            WEGNOTS SYSTEM HEALTH CHECK
echo =======================================================
echo.

REM Check if Docker is installed and running
echo Checking if Docker is running...
docker ps > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not running.
    echo The services may not be started.
    pause
    exit /b 1
)

echo Docker is running correctly.
echo.

@echo off
echo =======================================================
echo            WEGNOTS SYSTEM HEALTH CHECK
echo =======================================================
echo.

REM Check if Docker is running
echo Verificando se o Docker está em execução...
docker ps > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Docker não está em execução.
    echo Os serviços podem não estar iniciados.
    pause
    exit /b 1
)

echo.
echo Verificando status dos serviços WegNots...
docker ps --format "{{.Names}} - {{.Status}}" | findstr "mongodb-new monitor wegnots"
IF %ERRORLEVEL% NEQ 0 (
    echo Nenhum serviço WegNots encontrado em execução!
    echo Por favor, execute start.bat para inicializar o sistema.
    pause
    exit /b 1
)

echo.
echo Verificando status de saúde dos containers...
for %%c in (mongodb-new monitor wegnots) do (
    for /f "tokens=*" %%h in ('docker inspect --format="{{.State.Health.Status}}" %%c') do (
        echo Serviço %%c: %%h
    )
)

echo.
echo Verificando conectividade da API Monitor...
curl -s -o nul -w "Status da API Monitor: %%{http_code}\n" http://localhost:5000/health
IF %ERRORLEVEL% NEQ 0 (
    echo Não foi possível conectar à API Monitor. O serviço pode estar iniciando ou com problemas.
)

echo.
echo Verificando conectividade da interface Admin...
curl -s -o nul -w "Status da interface Admin: %%{http_code}\n" http://localhost:5173
IF %ERRORLEVEL% NEQ 0 (
    echo Não foi possível conectar à interface Admin. O serviço pode estar iniciando ou com problemas.
)

echo.
echo Verificando conexão com o banco de dados...
docker exec mongodb-new mongo --eval "db.adminCommand('ping')" > nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Conexão com o banco de dados: OK
) ELSE (
    echo Falha ao conectar ao banco de dados.
)

echo.
echo =======================================================
echo Para visualizar logs detalhados, use:
echo   - docker-compose logs -f
echo   - docker-compose logs -f monitor
echo   - docker-compose logs -f mongodb-new
echo   - docker-compose logs -f wegnots
echo =======================================================
echo.
pause
