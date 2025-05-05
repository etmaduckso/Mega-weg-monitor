@echo off
echo =======================================================
echo            LIMPEZA COMPLETA DO AMBIENTE WEGNOTS
echo =======================================================
echo.

echo Parando e removendo todos os contêineres relacionados ao WegNots...
docker stop mongodb-new monitor wegnots 2>nul
docker rm mongodb-new monitor wegnots 2>nul
docker-compose down -v

echo Removendo todas as imagens não utilizadas...
docker image prune -f

echo Removendo todos os volumes não utilizados...
docker volume prune -f

echo Verificando status do ambiente...
docker ps -a | findstr "mongodb\|monitor\|wegnots"

echo.
echo =======================================================
echo Limpeza concluída. O ambiente está pronto para reinicialização.
echo.
echo Execute start.bat para iniciar o sistema novamente.
echo =======================================================
echo.
pause