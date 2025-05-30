#!/usr/bin/env python3
"""
Settings Module - Configurações Centralizadas do Sistema

Este módulo é responsável por:
1. Carregar variáveis de ambiente do arquivo .env
2. Validar configurações críticas (email, feeds RSS, API keys)
3. Ler arquivos de configuração (feeds.txt, recipients.txt)
4. Fornecer configurações validadas para outros módulos

Author: Rodrigo Gomes
Date: 2024
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exceção levantada quando há erro na configuração."""
    pass


def validate_email_settings(settings: Dict[str, Any]) -> bool:
    """
    Valida configurações de email SMTP.
    
    Args:
        settings (Dict[str, Any]): Dicionário com configurações de email
        
    Returns:
        bool: True se válidas
        
    Raises:
        ConfigurationError: Se alguma configuração estiver inválida
    """
    required_fields = ["smtp_server", "smtp_port", "sender_email", "sender_password"]
    for field in required_fields:
        if not settings.get(field):
            raise ConfigurationError(f"Configuração de email obrigatória ausente: {field}")
    
    try:
        port = int(settings["smtp_port"])
        if port < 1 or port > 65535:
            raise ConfigurationError(f"Porta SMTP inválida: {port}")
    except ValueError:
        raise ConfigurationError("Porta SMTP deve ser um número")
    
    return True


def validate_rss_feeds(urls: List[str]) -> bool:
    """
    Valida URLs de feeds RSS.
    
    Args:
        urls (List[str]): Lista de URLs de feeds RSS
        
    Returns:
        bool: True se válidas
        
    Raises:
        ConfigurationError: Se alguma URL estiver inválida
    """
    if not urls:
        raise ConfigurationError("Nenhuma URL de feed RSS fornecida")
    
    for url in urls:
        if not url.startswith(('http://', 'https://')):
            raise ConfigurationError(f"URL de feed RSS inválida: {url}")
    
    return True


def validate_api_key(api_key: str) -> bool:
    """
    Valida chave da API do Gemini.
    
    Args:
        api_key (str): Chave da API
        
    Returns:
        bool: True se válida
        
    Raises:
        ConfigurationError: Se a chave estiver ausente
    """
    if not api_key:
        raise ConfigurationError("Chave da API ausente")
    return True


def read_file_lines(filepath: str) -> List[str]:
    """
    Lê linhas de um arquivo, filtrando linhas vazias e comentários.
    
    Args:
        filepath (str): Caminho do arquivo a ser lido
          Returns:
        List[str]: Lista de linhas válidas do arquivo
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = []
            for line in f:
                line = line.strip()
                # Ignora linhas vazias e comentários (linhas começadas com #)
                if line and not line.startswith('#'):
                    lines.append(line)
            return lines
    except FileNotFoundError:
        logger.warning(f"Arquivo de configuração não encontrado: {filepath}")
        return []


# ===== CARREGAMENTO DE CONFIGURAÇÕES =====

# Carrega variáveis de ambiente do arquivo .env na raiz do projeto
project_root = Path(__file__).parent.parent.parent
env_file = project_root / '.env'
load_dotenv(env_file)

# Obtém caminhos dos arquivos de configuração
config_dir = Path(__file__).parent
feeds_file = config_dir / 'feeds.txt'
recipients_file = config_dir / 'recipients.txt'

# Obtém e valida URLs de feeds RSS
RSS_FEED_URLS = read_file_lines(str(feeds_file))
if not RSS_FEED_URLS:  # Fallback para variável de ambiente se arquivo estiver vazio
    RSS_FEED_URLS = [url.strip() for url in os.getenv('RSS_FEED_URLS', '').split(',') if url.strip()]
validate_rss_feeds(RSS_FEED_URLS)

# Obtém destinatários - prioriza variável de ambiente para GitHub Actions
recipient_email = os.getenv("RECIPIENT_EMAIL")
if not recipient_email:
    # Fallback para arquivo se variável de ambiente não estiver definida
    recipients = read_file_lines(str(recipients_file))
    recipient_email = recipients[0] if recipients else None

if not recipient_email:
    raise ConfigurationError("Nenhum email de destinatário encontrado em recipients.txt ou variável RECIPIENT_EMAIL")

# Obtém e valida configurações de email
EMAIL_SETTINGS = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL"),
    "sender_password": os.getenv("SENDER_PASSWORD"),
    "recipient_email": recipient_email
}
validate_email_settings(EMAIL_SETTINGS)

# Obtém e valida chave da API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
validate_api_key(GEMINI_API_KEY)