@echo off
echo =======================================================
echo            WEGNOTS CONFIGURATION UTILITY
echo =======================================================
echo.

REM Check if Python is installed
echo Checking if Python is installed...
python --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo This utility requires Python to run.
    echo Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo Python is installed correctly.
echo.

REM Check if the monitor container is running
echo Checking if monitor service is running...
docker ps | findstr "wegnots-monitor" > nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Monitor service is running. Some configurations might require a restart.
    echo.
    set MONITOR_RUNNING=1
) ELSE (
    echo Monitor service is not running. You can make configuration changes safely.
    echo.
    set MONITOR_RUNNING=0
)

:menu
cls
echo =======================================================
echo            WEGNOTS CONFIGURATION UTILITY
echo =======================================================
echo.
echo 1. Configure Telegram settings
echo 2. Manage email accounts
echo 3. Test configuration
echo 4. Run config_manager.py (advanced)
echo 5. Exit
echo.
set /p CHOICE="Enter your choice (1-5): "

IF "%CHOICE%"=="1" (
    call :configure_telegram
    goto menu
)

IF "%CHOICE%"=="2" (
    call :manage_email
    goto menu
)

IF "%CHOICE%"=="3" (
    call :test_configuration
    goto menu
)

IF "%CHOICE%"=="4" (
    call :run_config_manager
    goto menu
)

IF "%CHOICE%"=="5" (
    exit /b 0
)

echo Invalid choice. Please try again.
timeout /t 2 /nobreak > nul
goto menu

:configure_telegram
cls
echo =======================================================
echo              TELEGRAM CONFIGURATION
echo =======================================================
echo.
echo Please provide your Telegram Bot token and chat ID for notifications.
echo You can get a Bot token from BotFather on Telegram.
echo.
set /p BOT_TOKEN="Telegram Bot Token: "
set /p CHAT_ID="Telegram Chat ID: "

IF NOT EXIST "monitor\config.ini" (
    echo [TELEGRAM] > monitor\config.ini
    echo token=%BOT_TOKEN% >> monitor\config.ini
    echo chat_id=%CHAT_ID% >> monitor\config.ini
    echo. >> monitor\config.ini
) ELSE (
    REM Update existing config using powershell to preserve other settings
    powershell -Command "(Get-Content monitor\config.ini) -replace '(?<=token=).*', '%BOT_TOKEN%' -replace '(?<=chat_id=).*', '%CHAT_ID%' | Set-Content monitor\config.ini"
)

echo.
echo Telegram settings saved.
echo.
IF "%MONITOR_RUNNING%"=="1" (
    echo NOTE: The monitor service is currently running.
    echo You may need to restart the system for changes to take effect.
    echo.
)
pause
exit /b 0

:manage_email
cls
echo =======================================================
echo              EMAIL ACCOUNT MANAGEMENT
echo =======================================================
echo.
echo 1. Add new email account
echo 2. List configured email accounts
echo 3. Back to main menu
echo.
set /p EMAIL_CHOICE="Enter your choice (1-3): "

IF "%EMAIL_CHOICE%"=="1" (
    call :add_email
    goto manage_email
)

IF "%EMAIL_CHOICE%"=="2" (
    call :list_emails
    goto manage_email
)

IF "%EMAIL_CHOICE%"=="3" (
    exit /b 0
)

echo Invalid choice. Please try again.
timeout /t 2 /nobreak > nul
goto manage_email

:add_email
cls
echo =======================================================
echo              ADD EMAIL ACCOUNT
echo =======================================================
echo.
echo Please provide the email account details:
echo.
set /p EMAIL="Email address: "
set /p EMAIL_SERVER="IMAP server (e.g., imap.gmail.com): "
set /p EMAIL_PORT="IMAP port (usually 993): "
set /p EMAIL_PASSWORD="Password: "

IF NOT EXIST "monitor\config.ini" (
    echo [TELEGRAM] > monitor\config.ini
    echo token= >> monitor\config.ini
    echo chat_id= >> monitor\config.ini
    echo. >> monitor\config.ini
)

echo. >> monitor\config.ini
echo [IMAP_%EMAIL%] >> monitor\config.ini
echo server=%EMAIL_SERVER% >> monitor\config.ini
echo port=%EMAIL_PORT% >> monitor\config.ini
echo username=%EMAIL% >> monitor\config.ini
echo password=%EMAIL_PASSWORD% >> monitor\config.ini
echo is_active=True >> monitor\config.ini

echo.
echo Email account added successfully.
echo.
IF "%MONITOR_RUNNING%"=="1" (
    echo NOTE: The monitor service is currently running.
    echo You may need to restart the system for changes to take effect.
)
pause
exit /b 0

:list_emails
cls
echo =======================================================
echo              CONFIGURED EMAIL ACCOUNTS
echo =======================================================
echo.

IF NOT EXIST "monitor\config.ini" (
    echo No configuration file exists yet.
    echo Please add an email account first.
    echo.
    pause
    exit /b 0
)

echo The following email accounts are configured:
echo.

REM Use findstr to list sections starting with IMAP_ that aren't TELEGRAM
findstr /B /C:"[IMAP_" "monitor\config.ini" | findstr /V /C:"[TELEGRAM]"

echo.
pause
exit /b 0

:test_configuration
cls
echo =======================================================
echo              TEST CONFIGURATION
echo =======================================================
echo.

IF NOT EXIST "monitor\config.ini" (
    echo No configuration file exists yet.
    echo Please configure Telegram and add email accounts first.
    echo.
    pause
    exit /b 0
)

echo Testing Telegram notification...
echo.

REM Use Python to send a test message using the configuration
pushd monitor
python -c "from config_manager import load_config, send_telegram_notification; config = load_config(); success = send_telegram_notification(config, '🧪 *WegNots Test Message*\n\nThis is a test notification from the configuration utility.'); print('✅ Notification sent successfully!' if success else '❌ Failed to send notification. Please check your Telegram settings.')"
popd

echo.
echo.
pause
exit /b 0

:run_config_manager
cls
echo =======================================================
echo              ADVANCED CONFIGURATION
echo =======================================================
echo.
echo Starting the full configuration manager...
echo.

pushd monitor
python config_manager.py
popd

echo.
echo Configuration manager completed.
echo.
pause
exit /b 0