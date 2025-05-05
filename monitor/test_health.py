#!/usr/bin/env python3
"""
Script para testar o endpoint de health check
"""
import requests
import sys
import os

def test_health_endpoint():
    try:
        # Use container hostname or environment variable
        host = os.environ.get('HEALTH_CHECK_HOST', '0.0.0.0')
        response = requests.get(f'http://{host}:5000/health', timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao conectar ao endpoint de saúde: {e}")
        return False

if __name__ == "__main__":
    success = test_health_endpoint()
    sys.exit(0 if success else 1)
