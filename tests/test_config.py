#!/usr/bin/env python3
"""
Testes para o módulo de configuração refatorado.

Testa a funcionalidade das dataclasses Configuration e EmailConfig,
validação de parâmetros e carregamento de configurações.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from config.config import (
    Configuration, EmailConfig, load_configuration, 
    ConfigurationError, validate_email_settings
)


class TestEmailConfig:
    """Testes para a dataclass EmailConfig."""
    
    def test_email_config_creation(self):
        """Testa criação básica do EmailConfig."""
        config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            sender_email='test@gmail.com',
            sender_password='password123'
        )
        
        assert config.smtp_server == 'smtp.gmail.com'
        assert config.smtp_port == 587
        assert config.sender_email == 'test@gmail.com'
        assert config.sender_password == 'password123'
        assert config.sender_name == "RSS Feed Processor"  # Valor padrão
    
    def test_email_config_to_dict(self):
        """Testa conversão para dicionário."""
        config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            sender_email='test@gmail.com',
            sender_password='password123'
        )
        
        result = config.to_dict()
        
        assert isinstance(result, dict)
        assert result['smtp_server'] == 'smtp.gmail.com'
        assert result['smtp_port'] == 587
        assert result['sender_email'] == 'test@gmail.com'


class TestConfiguration:
    """Testes para a dataclass Configuration."""
    
    def test_configuration_creation(self):
        """Testa criação básica da Configuration."""
        email_config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            sender_email='test@gmail.com',
            sender_password='password123'
        )
        
        config = Configuration(
            gemini_api_key='test_api_key',
            email_config=email_config,
            feed_urls=['http://example.com/feed.xml'],
            debug=False
        )
        
        assert config.gemini_api_key == 'test_api_key'
        assert config.feed_urls == ['http://example.com/feed.xml']
        assert config.debug is False
        assert config.email_config == email_config
    
    def test_configuration_default_values(self):
        """Testa valores padrão da Configuration."""
        config = Configuration()
        
        assert config.feed_urls == []  # Valor padrão
        assert config.debug is False   # Valor padrão
        assert config.gemini_api_key == ""  # Valor padrão
    
    def test_email_settings_property(self):
        """Testa a propriedade email_settings."""
        email_config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            sender_email='test@gmail.com',
            sender_password='password123'
        )
        
        config = Configuration(email_config=email_config)
        
        settings = config.email_settings
        assert isinstance(settings, dict)
        assert settings['smtp_server'] == 'smtp.gmail.com'


class TestValidateEmailSettings:
    """Testes para a função validate_email_settings (compatibilidade)."""
    
    def test_validate_valid_email_settings(self):
        """Testa validação de configuração de email válida."""
        settings = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'test@gmail.com',
            'sender_password': 'password123'
        }
        
        result = validate_email_settings(settings)
        assert result is True
    
    def test_validate_invalid_email_settings(self):
        """Testa validação com configuração inválida."""
        settings = {
            'smtp_server': '',  # Vazio
            'smtp_port': 'invalid',  # Tipo inválido
            'sender_email': 'test@gmail.com',
            'sender_password': 'password123'
        }
        
        result = validate_email_settings(settings)
        assert result is False


class TestLoadConfiguration:
    """Testes para a função load_configuration."""
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test_gemini_key',
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@gmail.com',
        'SENDER_PASSWORD': 'password123'
    })
    @patch('config.config.read_file_lines')
    def test_load_configuration_from_env(self, mock_read_file_lines):
        """Testa carregamento de configuração das variáveis de ambiente."""
        mock_read_file_lines.side_effect = [
            ['http://feed1.com/rss'],  # feeds
            ['recipient@example.com']   # recipients
        ]
        
        config = load_configuration()
        
        assert config.gemini_api_key == 'test_gemini_key'
        assert config.email_config.smtp_server == 'smtp.gmail.com'
        assert config.email_config.smtp_port == 587
        assert config.email_config.sender_email == 'test@gmail.com'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_configuration_missing_gemini_key(self):
        """Testa erro quando GEMINI_API_KEY está faltando."""
        with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
            load_configuration()
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test_key',
        'DEBUG': 'true'
    })
    @patch('config.config.read_file_lines')
    def test_load_configuration_debug_mode(self, mock_read_file_lines):
        """Testa carregamento com modo debug ativado."""
        mock_read_file_lines.side_effect = [
            ['http://feed1.com/rss'],  # feeds
            []   # recipients
        ]
        
        # Precisamos mockar a validação pois não temos email config completo
        with patch.object(Configuration, 'validate'):
            config = load_configuration()
            assert config.debug is True


class TestConfigurationError:
    """Testes para a exceção ConfigurationError."""
    
    def test_configuration_error_creation(self):
        """Testa criação da exceção ConfigurationError."""
        error = ConfigurationError("Teste de erro")
        
        assert str(error) == "Teste de erro"
        assert isinstance(error, Exception)
