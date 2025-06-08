#!/usr/bin/env python3
"""
RSS Feed Processor CLI

Interface de linha de comando moderna e robusta para o RSS Feed Processor.
Implementa múltiplos comandos com argumentos específicos e validação.

Author: Rodrigo Gomes
Date: 2025
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
import logging

# Adiciona src ao path para imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from app import create_app, ProcessingResult, RSSFeedProcessor
from config.config import load_configuration, Configuration, ConfigurationError
from utils.connection_tester import ConnectionTester
from utils.logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """Cria o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        prog='rss-processor',
        description='🚀 RSS Feed Processor - Processa feeds RSS e envia resumos por email',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 Comandos Disponíveis:
  run         Executa o processamento completo (padrão)
  test        Testa conexões e configurações
  validate    Valida configuração sem executar
  list-feeds  Lista todos os feeds configurados

📋 Exemplos de Uso:
  %(prog)s run                              # Processa últimas 24 horas
  %(prog)s run --days 3                     # Processa últimos 3 dias
  %(prog)s run --dry-run                    # Executa sem enviar email
  %(prog)s run --feeds url1,url2            # Usa feeds específicos
  
  %(prog)s --days 3                         # Atalho: processa últimos 3 dias
  %(prog)s --dry-run                        # Atalho: executa sem enviar email
  %(prog)s --debug --dry-run                # Atalho: debug + dry-run
  
  %(prog)s test                             # Testa todas as conexões
  %(prog)s validate                         # Valida configuração
  %(prog)s list-feeds                       # Lista feeds configurados

🔧 Configuração:
  Configure suas chaves de API e SMTP no arquivo .env
  Ajuste os feeds RSS em config/feeds.txt
  Configure destinatários em config/recipients.txt
        """
    )
    
    # Argumentos globais
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='🐛 Ativa logging detalhado para debug'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='.env',
        help='📄 Arquivo de configuração (padrão: .env)'
    )
    
    # Subcomandos
    subparsers = parser.add_subparsers(
        dest='command',
        help='Comando a executar',
        metavar='COMANDO'
    )
    
    # Comando: run (padrão)
    run_parser = subparsers.add_parser(
        'run',
        help='🚀 Executa processamento completo'
    )
    run_parser.add_argument(
        '--days', 
        type=int, 
        default=1,
        help='📅 Número de dias para buscar artigos (padrão: 1)'
    )
    run_parser.add_argument(
        '--feeds', 
        type=str,
        help='📡 Lista de feeds específicos (separados por vírgula)'
    )
    run_parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='🔍 Executa sem enviar emails (apenas mostra conteúdo)'
    )
    run_parser.add_argument(
        '--skip-test', 
        action='store_true',
        help='⚡ Pula testes de conexão (execução mais rápida)'
    )
    
    # Comando: test
    test_parser = subparsers.add_parser(
        'test',
        help='🔧 Testa conexões e configurações'
    )
    test_parser.add_argument(
        '--component',
        choices=['all', 'gemini', 'smtp', 'config'],
        default='all',
        help='🎯 Componente específico para testar'
    )
    
    # Comando: validate
    validate_parser = subparsers.add_parser(
        'validate',
        help='✅ Valida configuração sem executar'
    )
    
    # Comando: list-feeds
    list_parser = subparsers.add_parser(
        'list-feeds',
        help='📋 Lista todos os feeds configurados'
    )
    list_parser.add_argument(
        '--format',
        choices=['simple', 'detailed', 'json'],
        default='simple',
        help='📊 Formato de saída'
    )
    
    return parser


def cmd_run(args: argparse.Namespace, config: Configuration) -> int:
    """Executa o comando run."""
    logger = setup_logger(debug=args.debug)
    
    try:
        # Cria aplicação
        app = RSSFeedProcessor(config)
        
        # Testa conexões (se não for pulado)
        if not args.skip_test:
            if not app.test_connections():
                logger.error("❌ Falha nos testes de conexão")
                return 1
        
        # Processa feeds específicos se fornecidos
        if args.feeds:
            feed_urls = [url.strip() for url in args.feeds.split(',')]
            config.feed_urls = feed_urls
            logger.info(f"🎯 Usando {len(feed_urls)} feeds específicos")        # Executa processamento
        result = app.process_feeds(days_back=args.days, dry_run=args.dry_run)
        
        # Log resultado
        if result.success:
            logger.info(f"✅ Sucesso! Artigos: {result.articles_found}, "
                       f"Resumos: {result.summaries_generated}, "
                       f"Emails: {result.emails_sent}")
            return 0
        else:
            logger.error(f"❌ Falha no processamento: {'; '.join(result.errors)}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        return 1


def cmd_test(args: argparse.Namespace, config: Configuration) -> int:
    """Executa o comando test."""
    logger = setup_logger(debug=args.debug)
    
    try:
        tester = ConnectionTester(config.gemini_api_key, config.email_settings)
        
        if args.component == 'all':
            success = tester.test_all()
        elif args.component == 'gemini':
            success = tester.test_gemini_connection()
        elif args.component == 'smtp':
            success = tester.test_smtp_connection()
        elif args.component == 'config':
            logger.info("🔧 Testando configuração...")
            config.validate()
            logger.info("✅ Configuração válida")
            success = True
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Erro nos testes: {str(e)}")
        return 1


def cmd_validate(args: argparse.Namespace, config: Configuration) -> int:
    """Executa o comando validate."""
    logger = setup_logger(debug=args.debug)
    
    try:
        logger.info("🔍 Validando configuração...")
        config.validate()
        
        logger.info("✅ Configuração válida!")
        logger.info(f"  📧 Email: {config.email_config.sender_email if config.email_config else 'Não configurado'}")
        logger.info(f"  🤖 Gemini: {'Configurado' if config.gemini_api_key else 'Não configurado'}")
        logger.info(f"  📡 Feeds: {len(config.feed_urls)} configurados")
        logger.info(f"  👥 Destinatários: {len(config.email_config.recipients) if config.email_config else 0}")
        
        return 0
        
    except ConfigurationError as e:
        logger.error(f"❌ Configuração inválida: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro na validação: {str(e)}")
        return 1


def cmd_list_feeds(args: argparse.Namespace, config: Configuration) -> int:
    """Executa o comando list-feeds."""
    logger = setup_logger(debug=args.debug)
    
    try:
        if not config.feed_urls:
            logger.warning("⚠️ Nenhum feed configurado")
            return 0
        
        if args.format == 'simple':
            logger.info(f"📡 {len(config.feed_urls)} feeds configurados:")
            for i, url in enumerate(config.feed_urls, 1):
                print(f"  {i:2d}. {url}")
                
        elif args.format == 'detailed':
            logger.info(f"📡 Feeds RSS Configurados ({len(config.feed_urls)} total):")
            for i, url in enumerate(config.feed_urls, 1):
                domain = url.split('/')[2] if '//' in url else url
                print(f"  {i:2d}. {domain}")
                print(f"      🔗 {url}")
                
        elif args.format == 'json':
            import json
            feeds_data = {
                'total': len(config.feed_urls),
                'feeds': [{'index': i, 'url': url} for i, url in enumerate(config.feed_urls, 1)]
            }
            print(json.dumps(feeds_data, indent=2))
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar feeds: {str(e)}")
        return 1


def main() -> int:
    """Função principal da CLI."""
    parser = create_parser()
    
    # Intercepta argumentos comuns e insere 'run' automaticamente se necessário
    if len(sys.argv) > 1:
        common_run_args = ['--days', '--dry-run', '--skip-test', '--feeds']
        commands = ['run', 'test', 'validate', 'list-feeds']
        global_args = ['--debug', '--config']
        
        # Verifica se há argumentos específicos do 'run' sem comando explícito
        has_run_args = any(arg.startswith(tuple(common_run_args)) for arg in sys.argv[1:])
        has_command = any(arg in commands for arg in sys.argv[1:])
        
        if has_run_args and not has_command:
            # Separa argumentos globais dos argumentos do comando 'run'
            new_argv = [sys.argv[0]]  # Mantém o nome do programa
            run_args = []
            
            i = 1
            while i < len(sys.argv):
                arg = sys.argv[i]
                
                if arg == '--debug':
                    new_argv.append(arg)
                    i += 1
                elif arg == '--config':
                    new_argv.extend([arg, sys.argv[i + 1]])
                    i += 2
                elif arg.startswith('--config='):
                    new_argv.append(arg)
                    i += 1
                elif arg.startswith(tuple(common_run_args)):
                    # Argumento específico do 'run'
                    if arg.startswith('--days') and '=' not in arg and i + 1 < len(sys.argv):
                        run_args.extend([arg, sys.argv[i + 1]])
                        i += 2
                    elif arg.startswith('--feeds') and '=' not in arg and i + 1 < len(sys.argv):
                        run_args.extend([arg, sys.argv[i + 1]])
                        i += 2
                    else:
                        run_args.append(arg)
                        i += 1
                else:
                    run_args.append(arg)
                    i += 1
            
            # Reconstrói sys.argv com ordem correta: [programa, globals, 'run', run_args]
            sys.argv = new_argv + ['run'] + run_args
            
    args = parser.parse_args()
    
    # Se nenhum comando foi especificado, usar 'run' como padrão
    if args.command is None:
        args.command = 'run'
        # Adiciona argumentos padrão do run se não existirem
        if not hasattr(args, 'days'):
            args.days = 1
        if not hasattr(args, 'dry_run'):
            args.dry_run = False
        if not hasattr(args, 'skip_test'):
            args.skip_test = False
        if not hasattr(args, 'feeds'):
            args.feeds = None
    
    # Configura logger inicial
    logger = setup_logger(debug=args.debug)
    
    try:
        # Carrega configuração
        logger.info("🔧 Carregando configuração...")
        config = load_configuration(args.config)
        
        # Executa comando
        if args.command == 'run':
            return cmd_run(args, config)
        elif args.command == 'test':
            return cmd_test(args, config)
        elif args.command == 'validate':
            return cmd_validate(args, config)
        elif args.command == 'list-feeds':
            return cmd_list_feeds(args, config)
        else:
            logger.error(f"❌ Comando desconhecido: {args.command}")
            return 1
            
    except ConfigurationError as e:
        logger.error(f"❌ Erro de configuração: {str(e)}")
        logger.error("💡 Dica: Execute 'rss-processor validate' para verificar sua configuração")
        return 1
    except KeyboardInterrupt:
        logger.info("⏹️ Execução interrompida pelo usuário")
        return 0
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        if args.debug:
            import traceback
            logger.debug(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
