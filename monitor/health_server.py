#!/usr/bin/env python3
"""
Servidor HTTP simples para health checks do sistema WegNots
"""

import os
import sys
import logging
import threading
import http.server
import socketserver
from datetime import datetime

# Configura logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('wegnots.health')

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """Handler que responde ao healthcheck do Docker"""
    
    def do_GET(self):
        """Processa requisições GET"""
        if self.path == '/health':
            # Responde ao healthcheck
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response = f'{{"status": "healthy", "timestamp": "{timestamp}"}}'
            self.wfile.write(response.encode('utf-8'))
            logger.debug(f"Healthcheck respondido: {response}")
        elif self.path == '/':
            # Página inicial simples
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>WegNots Monitor</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #333; }}
                    .status {{ padding: 10px; border-radius: 5px; background-color: #d4edda; color: #155724; }}
                </style>
            </head>
            <body>
                <h1>WegNots Email Monitor</h1>
                <div class="status">
                    <p><strong>Status:</strong> Em execução</p>
                    <p><strong>Horário:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <p>O sistema está monitorando emails e enviando notificações.</p>
                <p><a href="/health">Verificar Saúde do Sistema</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            # Rota não encontrada
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
            
    def log_message(self, format, *args):
        """Sobrescreve o método de log para usar o nosso logger"""
        try:
            # Trata o caso em que args não tenha elementos suficientes
            if len(args) >= 3:
                logger.debug(f"[HealthCheckHandler] {args[0]} {args[1]} {args[2]}")
            else:
                logger.debug(f"[HealthCheckHandler] {' '.join(str(arg) for arg in args)}")
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")

def start_health_server(port=5000, bind="0.0.0.0"):
    """Inicia o servidor HTTP para health checks"""
    try:
        # Cria diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
        
        # Configura e inicia o servidor HTTP
        handler = HealthCheckHandler
        httpd = socketserver.ThreadingTCPServer((bind, port), handler)
        
        logger.info(f"Iniciando servidor de health check na porta {port}")
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True  # Define como daemon para que não bloqueie o encerramento
        server_thread.start()
        logger.info(f"Servidor de health check iniciado com sucesso em http://{bind}:{port}/")
        
        return httpd
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor de health check: {e}")
        return None

if __name__ == "__main__":
    # Teste standalone
    server = start_health_server()
    try:
        logger.info("Pressione Ctrl+C para encerrar...")
        # Mantém o programa em execução
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Encerrando servidor...")
        server.shutdown()