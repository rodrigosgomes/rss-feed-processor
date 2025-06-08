#!/usr/bin/env python3
"""
RSS Feed Processor - Main Application Module (Legacy Compatibility)

Este módulo mantém compatibilidade com a interface de linha de comando legada
do RSS Feed Processor, mas utiliza a nova arquitetura refatorada.

Para a nova interface CLI, use o arquivo cli.py na raiz do projeto.

Author: Rodrigo Gomes
Date: 2025
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Importa a nova arquitetura
from app import create_app, ProcessingResult
from config.config import load_configuration, ConfigurationError
from utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments (legacy compatibility).
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='RSS Feed Processor - Processa feeds RSS e envia resumos por email',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                           # Processa últimas 24 horas
  python main.py --days 3                  # Processa últimos 3 dias
  python main.py --dry-run                 # Executa sem enviar email
  python main.py --feeds "url1,url2"       # Usa feeds específicos
  python main.py --debug                   # Ativa logging detalhado

NOTA: Esta é a interface legada. Para novos recursos, use:
  python cli.py --help
        """
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=1,
        help='Número de dias de notícias para processar (padrão: 1)'
    )
    parser.add_argument(
        '--feeds', 
        type=str,
        help='Lista de feeds específicos separados por vírgula'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Executa sem enviar emails (apenas mostra o conteúdo)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Ativa logging detalhado para debug'
    )
    parser.add_argument(
        '--test-connections',
        action='store_true',
        help='Testa apenas as conexões e sai'
    )
    
    return parser.parse_args()


def get_feed_urls(args: argparse.Namespace) -> Optional[List[str]]:
    """
    Obtém a lista de URLs de feeds para processar.
    
    Args:
        args: Argumentos da linha de comando
        
    Returns:
        Optional[List[str]]: Lista de URLs de feeds RSS ou None para usar padrão
    """
    if args.feeds:
        feeds = [feed.strip() for feed in args.feeds.split(',')]
        return feeds
    
    return None  # Usa configuração padrão


def print_result_summary(result: ProcessingResult) -> None:
    """
    Imprime um resumo dos resultados do processamento.
    
    Args:
        result: Resultado do processamento
    """
    print("\n" + "="*50)
    print("📊 RESUMO DO PROCESSAMENTO")
    print("="*50)
    
    print(f"📰 Artigos encontrados: {result.articles_found}")
    print(f"⚙️  Artigos processados: {result.articles_processed}")
    print(f"📝 Resumos gerados: {result.summaries_generated}")
    print(f"📧 Emails enviados: {result.emails_sent}")
    
    if result.success:
        print(f"✅ Status: Sucesso")
    else:
        print(f"❌ Status: Falha")
        
        if result.errors:
            print(f"\n🚨 Erros encontrados:")
            for i, error in enumerate(result.errors, 1):
                print(f"  {i}. {error}")
    
    print("="*50)


def legacy_test_connections() -> bool:
    """
    Testa as conexões usando a nova arquitetura.
    
    Returns:
        bool: True se todas as conexões foram bem-sucedidas
    """
    try:
        print("=== TESTANDO CONEXÕES ===")
        
        # Cria aplicação para teste
        app = create_app()
        
        # Testa conexões
        result = app.test_connections()
        
        if result:
            print("✅ Todos os testes de conexão foram bem-sucedidos!")
        else:
            print("❌ Alguns testes de conexão falharam!")
            
        return result
        
    except ConfigurationError as e:
        print(f"❌ Erro de configuração: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante teste de conexões: {e}")
        return False


def legacy_process_news(days: int = 1, feed_urls: Optional[List[str]] = None, 
                       dry_run: bool = False, debug: bool = False) -> bool:
    """
    Processa notícias usando a nova arquitetura.
    
    Args:
        days: Número de dias para processar
        feed_urls: URLs específicos de feeds ou None para usar padrão
        dry_run: Se True, executa sem enviar email
        debug: Se True, ativa logging detalhado
        
    Returns:
        bool: True se processamento foi bem-sucedido
    """
    try:
        print("=== INICIANDO PROCESSAMENTO ===")
        print(f"📅 Processando notícias dos últimos {days} dias")
        
        if dry_run:
            print("🔍 Modo DRY RUN ativado - emails não serão enviados")
        
        if feed_urls:
            print(f"📡 Usando {len(feed_urls)} feeds específicos")
        else:
            print("📡 Usando feeds padrão da configuração")
        
        # Cria aplicação
        app = create_app()
        
        # Processa feeds
        result = app.process_feeds(
            feeds=feed_urls,
            days_back=days,
            dry_run=dry_run
        )
        
        # Mostra resumo
        print_result_summary(result)
        
        return result.success
        
    except ConfigurationError as e:
        print(f"❌ Erro de configuração: {e}")
        print("\n💡 Dica: Verifique seu arquivo .env e configurações")
        return False
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False


def main() -> None:
    """Função principal da aplicação (legacy compatibility)."""
    try:
        # Parse argumentos
        args = parse_args()
        
        # Configura logging global
        logger = setup_logger(debug=args.debug, name='RSSFeedProcessor-Legacy')
        
        print("🚀 RSS Feed Processor (Legacy Interface)")
        print("="*50)
        
        if args.debug:
            print("🔍 Modo debug ativado")
        
        # Se apenas teste de conexões
        if args.test_connections:
            success = legacy_test_connections()
            sys.exit(0 if success else 1)
        
        # Testa conexões primeiro
        print("1️⃣ Testando conexões...")
        if not legacy_test_connections():
            print("\n❌ Testes de conexão falharam. Verifique suas configurações.")
            print("\n💡 Dica: Use 'python cli.py test' para mais detalhes")
            sys.exit(1)
        
        # Processa notícias
        print("\n2️⃣ Processando notícias...")
        success = legacy_process_news(
            days=args.days,
            feed_urls=get_feed_urls(args),
            dry_run=args.dry_run,
            debug=args.debug
        )
        
        if success:
            print("\n🎉 Processamento concluído com sucesso!")
            print("\n💡 Para mais recursos, experimente: python cli.py --help")
        else:
            print("\n❌ Processamento falhou!")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Processamento interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
