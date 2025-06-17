#!/usr/bin/env python3
"""
Configuration Module - Gerenciamento de Configurações Refatorado

Este módulo implementa um sistema de configuração mais robusto
usando dataclasses e validação aprimorada.

Author: Rodrigo Gomes
Date: 2025
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exceção para erros de configuração."""
    pass


@dataclass
class EmailConfig:
    """Configuração de email SMTP."""
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    sender_name: str = "RSS Feed Processor"
    recipients: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para compatibilidade."""
        return {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_email': self.sender_email,
            'sender_password': self.sender_password,
            'sender_name': self.sender_name,
            'recipients': self.recipients,
            # Mantém compatibilidade com código antigo
            'recipient_email': self.recipients[0] if self.recipients else ''
        }


@dataclass
class Configuration:
    """Configuração principal da aplicação."""
    # Configurações básicas
    debug: bool = False
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    
    # APIs
    gemini_api_key: str = ""
    
    # Email
    email_config: Optional[EmailConfig] = None
    
    # Feeds RSS
    feed_urls: List[str] = field(default_factory=list)
    
    # Arquivos de configuração
    feeds_file: str = "config/feeds.txt"
    recipients_file: str = "config/recipients.txt"
    
    @property
    def email_settings(self) -> Dict[str, Any]:
        """Retorna configurações de email como dict para compatibilidade."""
        if self.email_config is None:
            return {}
        return self.email_config.to_dict()
    
    def validate(self) -> None:
        """Valida toda a configuração."""
        errors = []
        
        # Validar API key do Gemini
        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY não configurada")
        
        # Validar configuração de email
        if self.email_config is None:
            errors.append("Configuração de email não encontrada")
        else:
            try:
                self._validate_email_config(self.email_config)
            except ConfigurationError as e:
                errors.append(str(e))
        
        # Validar feeds RSS
        if not self.feed_urls:
            errors.append("Nenhum feed RSS configurado")
        
        if errors:
            raise ConfigurationError("Erros de configuração encontrados:\n" + "\n".join(f"- {e}" for e in errors))
    
    def _validate_email_config(self, email_config: EmailConfig) -> None:
        """Valida configuração de email."""
        if not email_config.smtp_server:
            raise ConfigurationError("SMTP server não configurado")
        
        if not email_config.sender_email:
            raise ConfigurationError("Email do remetente não configurado")
        
        if not email_config.sender_password:
            raise ConfigurationError("Senha do email não configurada")
        
        if not (1 <= email_config.smtp_port <= 65535):
            raise ConfigurationError(f"Porta SMTP inválida: {email_config.smtp_port}")


def read_file_lines(filepath: str, project_root: Optional[Path] = None) -> List[str]:
    """
    Lê linhas de um arquivo, ignorando comentários e linhas vazias.
    
    Args:
        filepath: Caminho do arquivo
        project_root: Diretório raiz do projeto
        
    Returns:
        List[str]: Lista de linhas não vazias
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent
    
    full_path = project_root / filepath
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = []
            for line in f:
                line = line.strip()
                # Ignora linhas vazias e comentários
                if line and not line.startswith('#'):
                    lines.append(line)
            return lines
    except FileNotFoundError:
        logger.warning(f"Arquivo não encontrado: {full_path}")
        return []
    except Exception as e:
        logger.error(f"Erro ao ler arquivo {full_path}: {e}")
        return []


def load_email_config() -> Optional[EmailConfig]:
    """Carrega configuração de email das variáveis de ambiente."""
    try:
        smtp_port_str = os.getenv('SMTP_PORT', '587')
        smtp_port = int(smtp_port_str)
        
        config = EmailConfig(
            smtp_server=os.getenv('SMTP_SERVER', ''),
            smtp_port=smtp_port,
            sender_email=os.getenv('SENDER_EMAIL', ''),
            sender_password=os.getenv('SENDER_PASSWORD', ''),
            sender_name=os.getenv('SENDER_NAME', 'RSS Feed Processor')
        )
        
        # Carrega lista de destinatários
        project_root = Path(__file__).parent.parent
        recipients = read_file_lines('config/recipients.txt', project_root)

        # Se recipients.txt não existir ou estiver vazio, tenta variável de ambiente
        if not recipients:
            env_recipients = os.getenv('RECIPIENT_EMAIL', '')
            if env_recipients:
                # Suporta múltiplos destinatários separados por vírgula ou ponto e vírgula
                recipients = [email.strip() for email in env_recipients.replace(';', ',').split(',') if email.strip()]
        config.recipients = recipients

        if not config.recipients:
            logger.error('Nenhum destinatário configurado. Configure recipients.txt ou a variável RECIPIENT_EMAIL.')

        return config
        
    except (ValueError, TypeError) as e:
        logger.error(f"Erro ao carregar configuração de email: {e}")
        return None


def load_configuration(env_file: str = '.env') -> Configuration:
    """
    Carrega configuração completa da aplicação.
    
    Args:
        env_file: Arquivo de variáveis de ambiente
        
    Returns:
        Configuration: Configuração carregada e validada
    """
    # Carrega variáveis de ambiente
    project_root = Path(__file__).parent.parent
    env_path = project_root / env_file
    
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Variáveis de ambiente carregadas de: {env_path}")
    else:
        logger.warning(f"Arquivo .env não encontrado: {env_path}")
    
    # Cria configuração
    config = Configuration(
        debug=os.getenv('DEBUG', 'false').lower() == 'true',
        project_root=project_root,
        gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
        email_config=load_email_config()
    )
    
    # Carrega feeds RSS
    config.feed_urls = read_file_lines(config.feeds_file, project_root)
    
    # Valida configuração
    config.validate()
    
    logger.info("✅ Configuração carregada e validada com sucesso")
    return config


# Compatibilidade com código legado
def validate_email_settings(settings: Dict[str, Any]) -> bool:
    """Mantém compatibilidade com validação legada."""
    try:
        EmailConfig(
            smtp_server=settings.get('smtp_server', ''),
            smtp_port=int(settings.get('smtp_port', 587)),
            sender_email=settings.get('sender_email', ''),
            sender_password=settings.get('sender_password', ''),
            sender_name=settings.get('sender_name', 'RSS Feed Processor')
        )
        return True
    except Exception:
        return False


# Exporta configurações globais para compatibilidade
try:
    _global_config = load_configuration()
    
    RSS_FEED_URLS = _global_config.feed_urls
    EMAIL_SETTINGS = _global_config.email_settings
    GEMINI_API_KEY = _global_config.gemini_api_key
    
except Exception as e:
    logger.error(f"Erro ao carregar configuração global: {e}")
    RSS_FEED_URLS = []
    EMAIL_SETTINGS = {}
    GEMINI_API_KEY = ""
