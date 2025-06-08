#!/usr/bin/env python3
"""
Testes para o módulo de aplicação (app.py).

Testa a funcionalidade da classe RSSFeedProcessor,
ProcessingResult e a função create_app.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

from app import RSSFeedProcessor, ProcessingResult, create_app
from config.config import Configuration, EmailConfig, ConfigurationError


class TestProcessingResult:
    """Testes para a dataclass ProcessingResult."""
    
    def test_processing_result_creation(self):
        """Testa criação básica do ProcessingResult."""
        result = ProcessingResult(
            articles_found=10,
            articles_processed=8,
            summaries_generated=8,
            emails_sent=1,
            success=True,
            errors=[]
        )
        
        assert result.articles_found == 10
        assert result.articles_processed == 8
        assert result.summaries_generated == 8
        assert result.emails_sent == 1
        assert result.success is True
        assert result.errors == []
    
    def test_processing_result_with_errors(self):
        """Testa ProcessingResult com erros."""
        errors = ["Erro 1", "Erro 2"]
        result = ProcessingResult(
            articles_found=5,
            articles_processed=3,
            summaries_generated=3,
            emails_sent=0,
            success=False,
            errors=errors
        )
        
        assert result.success is False
        assert len(result.errors) == 2
        assert "Erro 1" in result.errors
        assert "Erro 2" in result.errors


class TestRSSFeedProcessor:
    """Testes para a classe RSSFeedProcessor."""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture que retorna uma configuração mock."""
        email_config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            email_user='test@gmail.com',
            email_password='password123',
            from_email='test@gmail.com',
            to_email='recipient@gmail.com'
        )
        
        return Configuration(
            gemini_api_key='test_api_key',
            email_config=email_config,
            rss_feeds=['http://example.com/feed.xml'],
            days_back=1,
            debug=False
        )
    
    def test_processor_initialization(self, mock_config):
        """Testa inicialização do RSSFeedProcessor."""
        processor = RSSFeedProcessor(mock_config)
        
        assert processor.config == mock_config
        assert processor.logger is not None
        assert processor._rss_reader is None
        assert processor._summarizer is None
        assert processor._email_sender is None
    
    @patch('app.RssReader')
    def test_rss_reader_property(self, mock_rss_reader_class, mock_config):
        """Testa a propriedade rss_reader (lazy loading)."""
        mock_rss_reader_instance = Mock()
        mock_rss_reader_class.return_value = mock_rss_reader_instance
        
        processor = RSSFeedProcessor(mock_config)
        
        # Primeira chamada cria o objeto
        reader = processor.rss_reader
        assert reader == mock_rss_reader_instance
        mock_rss_reader_class.assert_called_once()
        
        # Segunda chamada retorna o mesmo objeto
        reader2 = processor.rss_reader
        assert reader2 == mock_rss_reader_instance
        assert mock_rss_reader_class.call_count == 1  # Não chama novamente
    
    @patch('app.Summarizer')
    def test_summarizer_property(self, mock_summarizer_class, mock_config):
        """Testa a propriedade summarizer (lazy loading)."""
        mock_summarizer_instance = Mock()
        mock_summarizer_class.return_value = mock_summarizer_instance
        
        processor = RSSFeedProcessor(mock_config)
        
        # Primeira chamada cria o objeto
        summarizer = processor.summarizer
        assert summarizer == mock_summarizer_instance
        mock_summarizer_class.assert_called_once_with(mock_config.gemini_api_key)
        
        # Segunda chamada retorna o mesmo objeto
        summarizer2 = processor.summarizer
        assert summarizer2 == mock_summarizer_instance
        assert mock_summarizer_class.call_count == 1
    
    @patch('app.EmailSender')
    def test_email_sender_property(self, mock_email_sender_class, mock_config):
        """Testa a propriedade email_sender (lazy loading)."""
        mock_email_sender_instance = Mock()
        mock_email_sender_class.return_value = mock_email_sender_instance
        
        processor = RSSFeedProcessor(mock_config)
        
        # Primeira chamada cria o objeto
        email_sender = processor.email_sender
        assert email_sender == mock_email_sender_instance
        mock_email_sender_class.assert_called_once_with(mock_config.email_config)
        
        # Segunda chamada retorna o mesmo objeto
        email_sender2 = processor.email_sender
        assert email_sender2 == mock_email_sender_instance
        assert mock_email_sender_class.call_count == 1
    
    @patch('app.ConnectionTester')
    def test_connection_tester_property(self, mock_connection_tester_class, mock_config):
        """Testa a propriedade connection_tester (lazy loading)."""
        mock_connection_tester_instance = Mock()
        mock_connection_tester_class.return_value = mock_connection_tester_instance
        
        processor = RSSFeedProcessor(mock_config)
        
        # Primeira chamada cria o objeto
        connection_tester = processor.connection_tester
        assert connection_tester == mock_connection_tester_instance
        mock_connection_tester_class.assert_called_once_with(mock_config)
        
        # Segunda chamada retorna o mesmo objeto
        connection_tester2 = processor.connection_tester
        assert connection_tester2 == mock_connection_tester_instance
        assert mock_connection_tester_class.call_count == 1
    
    def test_test_connections_success(self, mock_config):
        """Testa teste de conexões bem-sucedido."""
        processor = RSSFeedProcessor(mock_config)
        
        # Mock do connection_tester
        mock_connection_tester = Mock()
        mock_connection_tester.test_all_connections.return_value = True
        processor._connection_tester = mock_connection_tester
        
        result = processor.test_connections()
        
        assert result is True
        mock_connection_tester.test_all_connections.assert_called_once()
    
    def test_test_connections_failure(self, mock_config):
        """Testa teste de conexões com falha."""
        processor = RSSFeedProcessor(mock_config)
        
        # Mock do connection_tester
        mock_connection_tester = Mock()
        mock_connection_tester.test_all_connections.return_value = False
        processor._connection_tester = mock_connection_tester
        
        result = processor.test_connections()
        
        assert result is False
        mock_connection_tester.test_all_connections.assert_called_once()
    
    def test_process_feeds_no_feeds(self, mock_config):
        """Testa processamento quando não há feeds configurados."""
        mock_config.rss_feeds = []
        processor = RSSFeedProcessor(mock_config)
        
        result = processor.process_feeds()
        
        assert result.articles_found == 0
        assert result.articles_processed == 0
        assert result.summaries_generated == 0
        assert result.emails_sent == 0
        assert result.success is True
        assert len(result.errors) == 0
    
    def test_process_feeds_with_custom_feeds(self, mock_config):
        """Testa processamento com feeds customizados."""
        processor = RSSFeedProcessor(mock_config)
        
        # Mocks
        mock_rss_reader = Mock()
        mock_summarizer = Mock()
        mock_email_sender = Mock()
        
        # Configurar mocks
        mock_articles = [{'title': 'Article 1', 'content': 'Content 1'}]
        mock_rss_reader.read_feeds.return_value = mock_articles
        mock_summarizer.summarize_articles.return_value = ['Summary 1']
        mock_email_sender.send_email.return_value = True
        
        processor._rss_reader = mock_rss_reader
        processor._summarizer = mock_summarizer
        processor._email_sender = mock_email_sender
        
        custom_feeds = ['http://custom.com/feed.xml']
        result = processor.process_feeds(feeds=custom_feeds)
        
        assert result.articles_found == 1
        assert result.articles_processed == 1
        assert result.summaries_generated == 1
        assert result.emails_sent == 1
        assert result.success is True
        
        # Verifica se o feed customizado foi usado
        mock_rss_reader.read_feeds.assert_called_once_with(
            custom_feeds, mock_config.days_back
        )
    
    def test_process_feeds_dry_run(self, mock_config):
        """Testa processamento em modo dry-run."""
        processor = RSSFeedProcessor(mock_config)
        
        # Mocks
        mock_rss_reader = Mock()
        mock_summarizer = Mock()
        mock_email_sender = Mock()
        
        # Configurar mocks
        mock_articles = [{'title': 'Article 1', 'content': 'Content 1'}]
        mock_rss_reader.read_feeds.return_value = mock_articles
        mock_summarizer.summarize_articles.return_value = ['Summary 1']
        
        processor._rss_reader = mock_rss_reader
        processor._summarizer = mock_summarizer
        processor._email_sender = mock_email_sender
        
        result = processor.process_feeds(dry_run=True)
        
        assert result.articles_found == 1
        assert result.articles_processed == 1
        assert result.summaries_generated == 1
        assert result.emails_sent == 0  # Não envia email em dry-run
        assert result.success is True
        
        # Verifica que email não foi enviado
        mock_email_sender.send_email.assert_not_called()
    
    def test_process_feeds_with_error(self, mock_config):
        """Testa processamento com erro durante execução."""
        processor = RSSFeedProcessor(mock_config)
        
        # Mock que gera erro
        mock_rss_reader = Mock()
        mock_rss_reader.read_feeds.side_effect = Exception("Erro no RSS")
        processor._rss_reader = mock_rss_reader
        
        result = processor.process_feeds()
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "Erro no RSS" in str(result.errors[0])
    
    def test_list_feeds(self, mock_config):
        """Testa listagem de feeds configurados."""
        processor = RSSFeedProcessor(mock_config)
        
        feeds = processor.list_feeds()
        
        assert feeds == mock_config.rss_feeds
        assert len(feeds) == 1
        assert 'http://example.com/feed.xml' in feeds


class TestCreateApp:
    """Testes para a função create_app."""
    
    @patch('app.load_configuration')
    def test_create_app_success(self, mock_load_config):
        """Testa criação bem-sucedida da aplicação."""
        # Mock da configuração
        email_config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            email_user='test@gmail.com',
            email_password='password123',
            from_email='test@gmail.com',
            to_email='recipient@gmail.com'
        )
        
        mock_config = Configuration(
            gemini_api_key='test_api_key',
            email_config=email_config,
            rss_feeds=['http://example.com/feed.xml'],
            days_back=1,
            debug=False
        )
        
        mock_load_config.return_value = mock_config
        
        app = create_app()
        
        assert isinstance(app, RSSFeedProcessor)
        assert app.config == mock_config
        mock_load_config.assert_called_once()
    
    @patch('app.load_configuration')
    def test_create_app_configuration_error(self, mock_load_config):
        """Testa erro de configuração durante criação da aplicação."""
        mock_load_config.side_effect = ConfigurationError("Erro na configuração")
        
        with pytest.raises(ConfigurationError, match="Erro na configuração"):
            create_app()
    
    @patch('app.load_configuration')
    def test_create_app_with_custom_config_path(self, mock_load_config):
        """Testa criação da aplicação com caminho customizado de configuração."""
        # Mock da configuração
        email_config = EmailConfig(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            email_user='test@gmail.com',
            email_password='password123',
            from_email='test@gmail.com',
            to_email='recipient@gmail.com'
        )
        
        mock_config = Configuration(
            gemini_api_key='test_api_key',
            email_config=email_config
        )
        
        mock_load_config.return_value = mock_config
        
        custom_path = "/custom/path/config"
        app = create_app(config_path=custom_path)
        
        assert isinstance(app, RSSFeedProcessor)
        mock_load_config.assert_called_once_with(config_path=custom_path)
