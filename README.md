# 🌟 WegNots - Sistema de Monitoramento de E-mails e Notificações

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-339933.svg)](https://nodejs.org/)
[![Vite](https://img.shields.io/badge/vite-powered-646CFF.svg)](https://vitejs.dev/)
[![Material-UI](https://img.shields.io/badge/mui-styled-007FFF.svg)](https://mui.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-5.0+-47A248.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)

![Última Atualização](https://img.shields.io/badge/última_atualização-Abril_2025-informational)

Sistema profissional para monitoramento de e-mails IMAP e envio de notificações via Telegram, desenvolvido com foco em robustez, escalabilidade e seguindo boas práticas de desenvolvimento.

---

# WegNots System

WegNots is a comprehensive email monitoring system with Telegram notifications and web-based administration.

## System Components

- **MongoDB Database**: Stores all application data
- **Monitor Service**: Python-based email monitoring service that checks for new emails and sends alerts via Telegram
- **Admin Panel**: Web interface for system management and configuration

## Quick Start Guide

### Prerequisites

- **Docker** and **Docker Compose** must be installed
- **Python 3.9+** is recommended for configuration utilities (optional)

### Installation and Setup

1. **Initialize the System**:
   - Run `start.bat` to begin system initialization
   - The script will check if Docker is running and guide you through initial setup
   - You'll be prompted to configure Telegram notifications and email monitoring

2. **Configure the System**:
   - After initialization, run `configure.bat` to set up email accounts and Telegram
   - You can add multiple email accounts to monitor
   - Configure notification settings for each account

3. **Check System Status**:
   - Use `health_check.bat` to verify all services are running correctly
   - This will check database, API, and UI connectivity

4. **Access the Admin Interface**:
   - Open a web browser and navigate to `http://localhost:5173`
   - Log in using your credentials

### System Management

#### Starting the System

- Run `start.bat` to initialize all components
- The script performs pre-flight checks to ensure Docker is running
- System status is displayed after startup

#### Configuring the System

- Run `configure.bat` for an easy-to-use configuration menu
- Options include:
  - Configure Telegram settings
  - Manage email accounts
  - Test configuration
  - Access the advanced configuration manager

#### Monitoring System Health

- Run `health_check.bat` to check if all services are running correctly
- The script checks:
  - Container status
  - API accessibility
  - Database connectivity
  - UI availability

#### Shutting Down the System

- Run `stop.bat` to gracefully shut down all components
- This sends proper shutdown notifications and stops all containers

## Deployment Across Different Servers

WegNots can be deployed across different servers with these components communicating over the network:

1. **Using a Shared Network**:
   - Modify `docker-compose.yml` to use external networks
   - Set explicit IP addresses or use a container orchestration platform

2. **Configuring Multiple Installations**:
   - Each installation can monitor different email accounts
   - Configure each instance to report to the same Telegram chat

3. **Database Synchronization**:
   - Configure MongoDB for replication if needed across multiple deployments

## Troubleshooting

### Common Issues

1. **Services not starting**:
   - Check Docker status with `docker ps`
   - Review logs with `docker-compose logs -f`

2. **Configuration problems**:
   - Verify config.ini in the monitor directory
   - Run `configure.bat` to update settings

3. **Email monitoring not working**:
   - Ensure proper IMAP settings for your email provider
   - Check if less secure apps are allowed (for Gmail)
   - Verify network connectivity to IMAP servers

### Logs

- Monitor logs are stored in `monitor/logs/`
- Container logs can be viewed with:
  - `docker-compose logs -f` (all services)
  - `docker-compose logs -f monitor` (just monitor service)
  - `docker-compose logs -f mongodb` (just database)
  - `docker-compose logs -f admin` (just admin UI)

## Security Considerations

- Passwords are stored in config.ini - ensure this file has appropriate permissions
- Consider using environment variables for sensitive information in production
- The MongoDB database is accessible only within the Docker network by default

---

Desenvolvido com ❤️ pela equipe MegaSec.
Para suporte, contate-nos em suporte@megasec.com.br
