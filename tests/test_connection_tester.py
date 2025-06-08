#!/usr/bin/env python3
"""
Testes para o módulo connection_tester.py.

Testa a funcionalidade da classe ConnectionTester,
testes de conectividade com Gemini API e SMTP.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib
import socket

from utils.connection_tester import ConnectionTester
from config.config import Configuration, EmailConfig


class TestConnectionTester:
    """Testes para a classe ConnectionTester."""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture que retorna uma configuração mock."""
        email_config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            email_user='test@gmail.com',
            email_password='password123',
            from_email='test@gmail.com',
            to_email='recipient@gmail.com',
            use_tls=True
        )
        
        return Configuration(
            gemini_api_key='test_api_key',
            email_config=email_config,
            rss_feeds=['http://example.com/feed.xml'],
            days_back=1,
            debug=False
        )
    
    def test_connection_tester_initialization(self, mock_config):
        """Testa inicialização do ConnectionTester."""
        tester = ConnectionTester(mock_config)
        
        assert tester.config == mock_config
        assert tester.logger is not None
    
    @patch('utils.connection_tester.genai.configure')
    @patch('utils.connection_tester.genai.GenerativeModel')
    def test_test_gemini_api_success(self, mock_model_class, mock_configure, mock_config):
        """Testa teste bem-sucedido da API Gemini."""
        # Mock do modelo Gemini
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        tester = ConnectionTester(mock_config)
        result = tester.test_gemini_api()
        
        assert result is True
        mock_configure.assert_called_once_with(api_key='test_api_key')
        mock_model_class.assert_called_once_with('gemini-pro')
        mock_model.generate_content.assert_called_once_with("Test connection")
    
    @patch('utils.connection_tester.genai.configure')
    @patch('utils.connection_tester.genai.GenerativeModel')
    def test_test_gemini_api_failure(self, mock_model_class, mock_configure, mock_config):
        """Testa falha no teste da API Gemini."""
        # Mock que gera erro
        mock_configure.side_effect = Exception("API Key inválida")
        
        tester = ConnectionTester(mock_config)
        result = tester.test_gemini_api()
        
        assert result is False
        mock_configure.assert_called_once_with(api_key='test_api_key')
    
    @patch('utils.connection_tester.genai.configure')
    @patch('utils.connection_tester.genai.GenerativeModel')
    def test_test_gemini_api_empty_response(self, mock_model_class, mock_configure, mock_config):
        """Testa resposta vazia da API Gemini."""
        # Mock do modelo com resposta vazia
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        tester = ConnectionTester(mock_config)
        result = tester.test_gemini_api()
        
        assert result is False
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_success(self, mock_smtp_class, mock_config):
        """Testa conexão SMTP bem-sucedida."""
        # Mock do servidor SMTP
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is True
        mock_smtp_class.assert_called_once_with('smtp.gmail.com', 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with('test@gmail.com', 'password123')
        mock_smtp.quit.assert_called_once()
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_no_tls(self, mock_smtp_class, mock_config):
        """Testa conexão SMTP sem TLS."""
        # Configurar para não usar TLS
        mock_config.email_config.use_tls = False
        
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is True
        mock_smtp.starttls.assert_not_called()  # Não deve chamar starttls
        mock_smtp.login.assert_called_once_with('test@gmail.com', 'password123')
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_failure(self, mock_smtp_class, mock_config):
        """Testa falha na conexão SMTP."""
        # Mock que gera erro
        mock_smtp_class.side_effect = smtplib.SMTPException("Erro de conexão")
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is False
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_auth_failure(self, mock_smtp_class, mock_config):
        """Testa falha de autenticação SMTP."""
        # Mock do servidor SMTP com falha na autenticação
        mock_smtp = Mock()
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, "Invalid credentials")
        mock_smtp_class.return_value = mock_smtp
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is False
        mock_smtp.quit.assert_called_once()  # Deve fechar a conexão mesmo com erro
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_socket_error(self, mock_smtp_class, mock_config):
        """Testa erro de socket na conexão SMTP."""
        # Mock que gera erro de socket
        mock_smtp_class.side_effect = socket.gaierror("Nome ou serviço não conhecido")
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is False
    
    @patch.object(ConnectionTester, 'test_gemini_api')
    @patch.object(ConnectionTester, 'test_smtp_connection')
    def test_test_all_connections_success(self, mock_smtp_test, mock_gemini_test, mock_config):
        """Testa teste de todas as conexões bem-sucedido."""
        mock_gemini_test.return_value = True
        mock_smtp_test.return_value = True
        
        tester = ConnectionTester(mock_config)
        result = tester.test_all_connections()
        
        assert result is True
        mock_gemini_test.assert_called_once()
        mock_smtp_test.assert_called_once()
    
    @patch.object(ConnectionTester, 'test_gemini_api')
    @patch.object(ConnectionTester, 'test_smtp_connection')
    def test_test_all_connections_gemini_failure(self, mock_smtp_test, mock_gemini_test, mock_config):
        """Testa falha no teste da API Gemini."""
        mock_gemini_test.return_value = False
        mock_smtp_test.return_value = True
        
        tester = ConnectionTester(mock_config)
        result = tester.test_all_connections()
        
        assert result is False
        mock_gemini_test.assert_called_once()
        mock_smtp_test.assert_called_once()  # Deve testar ambos mesmo com falha
    
    @patch.object(ConnectionTester, 'test_gemini_api')
    @patch.object(ConnectionTester, 'test_smtp_connection')
    def test_test_all_connections_smtp_failure(self, mock_smtp_test, mock_gemini_test, mock_config):
        """Testa falha no teste SMTP."""
        mock_gemini_test.return_value = True
        mock_smtp_test.return_value = False
        
        tester = ConnectionTester(mock_config)
        result = tester.test_all_connections()
        
        assert result is False
        mock_gemini_test.assert_called_once()
        mock_smtp_test.assert_called_once()
    
    @patch.object(ConnectionTester, 'test_gemini_api')
    @patch.object(ConnectionTester, 'test_smtp_connection')
    def test_test_all_connections_both_failure(self, mock_smtp_test, mock_gemini_test, mock_config):
        """Testa falha em ambos os testes."""
        mock_gemini_test.return_value = False
        mock_smtp_test.return_value = False
        
        tester = ConnectionTester(mock_config)
        result = tester.test_all_connections()
        
        assert result is False
        mock_gemini_test.assert_called_once()
        mock_smtp_test.assert_called_once()
    
    @patch.object(ConnectionTester, 'test_gemini_api')
    @patch.object(ConnectionTester, 'test_smtp_connection')
    def test_test_all_connections_with_exception(self, mock_smtp_test, mock_gemini_test, mock_config):
        """Testa exceção durante teste de conexões."""
        mock_gemini_test.side_effect = Exception("Erro inesperado")
        mock_smtp_test.return_value = True
        
        tester = ConnectionTester(mock_config)
        result = tester.test_all_connections()
        
        assert result is False
        mock_gemini_test.assert_called_once()
        # SMTP ainda deve ser testado mesmo com exceção no Gemini
        mock_smtp_test.assert_called_once()
    
    def test_connection_tester_with_debug_config(self, mock_config):
        """Testa ConnectionTester com configuração de debug."""
        mock_config.debug = True
        
        tester = ConnectionTester(mock_config)
        
        # Verifica se o logger foi configurado corretamente
        assert tester.logger is not None
        assert tester.config.debug is True
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_port_465(self, mock_smtp_class, mock_config):
        """Testa conexão SMTP com porta 465 (SSL)."""
        # Configurar porta SSL
        mock_config.email_config.smtp_port = 465
        
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is True
        mock_smtp_class.assert_called_once_with('smtp.gmail.com', 465)
    
    @patch('utils.connection_tester.smtplib.SMTP')
    def test_test_smtp_connection_custom_server(self, mock_smtp_class, mock_config):
        """Testa conexão SMTP com servidor customizado."""
        # Configurar servidor customizado
        mock_config.email_config.smtp_server = 'mail.example.com'
        mock_config.email_config.smtp_port = 25
        
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        
        tester = ConnectionTester(mock_config)
        result = tester.test_smtp_connection()
        
        assert result is True
        mock_smtp_class.assert_called_once_with('mail.example.com', 25)
