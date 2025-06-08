#!/usr/bin/env python3
"""
Testes para a CLI refatorada (cli.py).

Testa a funcionalidade da nova interface de linha de comando
com múltiplos comandos e argumentos específicos.
"""

import pytest
import argparse
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Importar módulos da CLI
sys.path.insert(0, 'c:\\Projects\\agents\\product_reader')
from cli import (
    create_parser, main, cmd_run, cmd_test, 
    cmd_validate, cmd_list_feeds
)


class TestCreateParser:
    """Testes para a função create_parser."""
    
    def test_create_parser_basic(self):
        """Testa criação básica do parser."""
        parser = create_parser()
        
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == 'rss-processor'
        assert 'RSS Feed Processor' in parser.description
    
    def test_create_parser_default_command(self):
        """Testa comando padrão (run)."""
        parser = create_parser()
        args = parser.parse_args([])
        
        assert args.command == 'run'
        assert args.days == 1
        assert args.dry_run is False
        assert args.feeds is None
    
    def test_create_parser_run_command_with_args(self):
        """Testa comando run com argumentos."""
        parser = create_parser()
        args = parser.parse_args(['run', '--days', '3', '--dry-run', '--feeds', 'url1,url2'])
        
        assert args.command == 'run'
        assert args.days == 3
        assert args.dry_run is True
        assert args.feeds == 'url1,url2'
    
    def test_create_parser_test_command(self):
        """Testa comando test."""
        parser = create_parser()
        args = parser.parse_args(['test'])
        
        assert args.command == 'test'
    
    def test_create_parser_validate_command(self):
        """Testa comando validate."""
        parser = create_parser()
        args = parser.parse_args(['validate'])
        
        assert args.command == 'validate'
    
    def test_create_parser_list_feeds_command(self):
        """Testa comando list-feeds."""
        parser = create_parser()
        args = parser.parse_args(['list-feeds'])
        
        assert args.command == 'list-feeds'
    
    def test_create_parser_global_debug_flag(self):
        """Testa flag global de debug."""
        parser = create_parser()
        args = parser.parse_args(['--debug', 'run'])
        
        assert args.debug is True
        assert args.command == 'run'
    
    def test_create_parser_global_config_path(self):
        """Testa configuração de caminho global."""
        parser = create_parser()
        args = parser.parse_args(['--config-path', '/custom/path', 'run'])
        
        assert args.config_path == '/custom/path'
        assert args.command == 'run'


class TestCmdRun:
    """Testes para o comando run."""
    
    @patch('cli.create_app')
    def test_cmd_run_success(self, mock_create_app):
        """Testa execução bem-sucedida do comando run."""
        # Mock da aplicação
        mock_app = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.articles_found = 5
        mock_result.articles_processed = 5
        mock_result.summaries_generated = 5
        mock_result.emails_sent = 1
        mock_result.errors = []
        
        mock_app.process_feeds.return_value = mock_result
        mock_create_app.return_value = mock_app
        
        # Mock dos argumentos
        args = Mock()
        args.days = 1
        args.dry_run = False
        args.feeds = None
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_run(args)
            
            assert result == 0  # Exit code success
            output = mock_stdout.getvalue()
            assert '✅ Processamento concluído com sucesso!' in output
            assert '📊 Estatísticas:' in output
            
        mock_app.process_feeds.assert_called_once_with(
            feeds=None, days_back=1, dry_run=False
        )
    
    @patch('cli.create_app')
    def test_cmd_run_with_custom_feeds(self, mock_create_app):
        """Testa comando run com feeds customizados."""
        mock_app = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.articles_found = 3
        mock_result.articles_processed = 3
        mock_result.summaries_generated = 3
        mock_result.emails_sent = 1
        mock_result.errors = []
        
        mock_app.process_feeds.return_value = mock_result
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.days = 2
        args.dry_run = True
        args.feeds = 'http://feed1.com,http://feed2.com'
        args.debug = False
        args.config_path = None
        
        result = cmd_run(args)
        
        assert result == 0
        mock_app.process_feeds.assert_called_once_with(
            feeds=['http://feed1.com', 'http://feed2.com'], 
            days_back=2, 
            dry_run=True
        )
    
    @patch('cli.create_app')
    def test_cmd_run_failure(self, mock_create_app):
        """Testa falha no comando run."""
        mock_app = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.errors = ['Erro 1', 'Erro 2']
        
        mock_app.process_feeds.return_value = mock_result
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.days = 1
        args.dry_run = False
        args.feeds = None
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_run(args)
            
            assert result == 1  # Exit code error
            output = mock_stdout.getvalue()
            assert '❌ Processamento falhou!' in output
            assert 'Erro 1' in output
            assert 'Erro 2' in output
    
    @patch('cli.create_app')
    def test_cmd_run_exception(self, mock_create_app):
        """Testa exceção durante comando run."""
        mock_create_app.side_effect = Exception("Erro na criação da app")
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_run(args)
            
            assert result == 1
            output = mock_stdout.getvalue()
            assert '❌ Erro durante execução:' in output


class TestCmdTest:
    """Testes para o comando test."""
    
    @patch('cli.create_app')
    def test_cmd_test_success(self, mock_create_app):
        """Testa comando test bem-sucedido."""
        mock_app = Mock()
        mock_app.test_connections.return_value = True
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_test(args)
            
            assert result == 0
            output = mock_stdout.getvalue()
            assert '✅ Todos os testes de conectividade passaram!' in output
        
        mock_app.test_connections.assert_called_once()
    
    @patch('cli.create_app')
    def test_cmd_test_failure(self, mock_create_app):
        """Testa falha no comando test."""
        mock_app = Mock()
        mock_app.test_connections.return_value = False
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_test(args)
            
            assert result == 1
            output = mock_stdout.getvalue()
            assert '❌ Alguns testes de conectividade falharam!' in output


class TestCmdValidate:
    """Testes para o comando validate."""
    
    @patch('cli.create_app')
    def test_cmd_validate_success(self, mock_create_app):
        """Testa comando validate bem-sucedido."""
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_validate(args)
            
            assert result == 0
            output = mock_stdout.getvalue()
            assert '✅ Configuração validada com sucesso!' in output
    
    @patch('cli.create_app')
    def test_cmd_validate_failure(self, mock_create_app):
        """Testa falha na validação."""
        from config.config import ConfigurationError
        mock_create_app.side_effect = ConfigurationError("Configuração inválida")
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_validate(args)
            
            assert result == 1
            output = mock_stdout.getvalue()
            assert '❌ Erro na configuração:' in output
            assert 'Configuração inválida' in output


class TestCmdListFeeds:
    """Testes para o comando list-feeds."""
    
    @patch('cli.create_app')
    def test_cmd_list_feeds_with_feeds(self, mock_create_app):
        """Testa listagem de feeds com feeds configurados."""
        mock_app = Mock()
        mock_app.list_feeds.return_value = [
            'http://feed1.com/rss',
            'http://feed2.com/rss',
            'http://feed3.com/rss'
        ]
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_list_feeds(args)
            
            assert result == 0
            output = mock_stdout.getvalue()
            assert '📡 Feeds RSS configurados:' in output
            assert 'http://feed1.com/rss' in output
            assert 'http://feed2.com/rss' in output
            assert 'http://feed3.com/rss' in output
    
    @patch('cli.create_app')
    def test_cmd_list_feeds_empty(self, mock_create_app):
        """Testa listagem quando não há feeds configurados."""
        mock_app = Mock()
        mock_app.list_feeds.return_value = []
        mock_create_app.return_value = mock_app
        
        args = Mock()
        args.debug = False
        args.config_path = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_list_feeds(args)
            
            assert result == 0
            output = mock_stdout.getvalue()
            assert '⚠️  Nenhum feed RSS configurado.' in output


class TestMainFunction:
    """Testes para a função main."""
    
    @patch('cli.create_parser')
    @patch('cli.cmd_run')
    def test_main_run_command(self, mock_cmd_run, mock_create_parser):
        """Testa função main com comando run."""
        # Mock do parser
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.command = 'run'
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        mock_cmd_run.return_value = 0
        
        with patch('sys.argv', ['cli.py', 'run']):
            result = main()
            
            assert result == 0
            mock_cmd_run.assert_called_once_with(mock_args)
    
    @patch('cli.create_parser')
    @patch('cli.cmd_test')
    def test_main_test_command(self, mock_cmd_test, mock_create_parser):
        """Testa função main com comando test."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.command = 'test'
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        mock_cmd_test.return_value = 0
        
        with patch('sys.argv', ['cli.py', 'test']):
            result = main()
            
            assert result == 0
            mock_cmd_test.assert_called_once_with(mock_args)
        
        # Setup mocks
        mock_reader.return_value.fetch_news.return_value = mock_news_items
        mock_summarizer.return_value.summarize.return_value = mock_summary
        
        # Test dry run mode
        process_news(days=1, feed_urls=['http://test.com'], dry_run=True)
        
        # Verify email was not sent
        mock_sender.return_value.send_email.assert_not_called()

@pytest.mark.asyncio
async def test_process_news_with_email():
    # Mock dependencies
    mock_news_items = [
        MagicMock(
            title='Test Article',
            published_date=datetime.now() - timedelta(hours=1)
        )
    ]
    
    mock_summary = "Test Summary"
    
    with patch('src.main.RssReader') as mock_reader, \
         patch('src.main.Summarizer') as mock_summarizer, \
         patch('src.main.EmailSender') as mock_sender:
        
        # Setup mocks
        mock_reader.return_value.fetch_news.return_value = mock_news_items
        mock_summarizer.return_value.summarize.return_value = mock_summary
        
        # Test normal mode
        process_news(days=1, feed_urls=['http://test.com'], dry_run=False)
        
        # Verify email was sent
        mock_sender.return_value.send_email.assert_called_once_with(mock_summary)
