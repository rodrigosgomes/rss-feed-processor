#!/usr/bin/env python3
"""
RSS Feed Processor - Main Application Module

Este módulo é o ponto de entrada principal do RSS Feed Processor.
Ele orquestra o processo de:
1. Buscar artigos de feeds RSS
2. Filtrar por data
3. Gerar resumos usando IA
4. Enviar email com o conteúdo formatado

Author: Rodrigo Gomes
Date: 2024
"""

import argparse
import logging
import smtplib
import sys
from datetime import datetime, timedelta
from typing import List, Optional

import pytz

from agents.rss_reader import RssReader
from agents.summarizer import Summarizer
from config.settings import RSS_FEED_URLS, EMAIL_SETTINGS, GEMINI_API_KEY
from utils.email_sender import EmailSender
from utils.gemini_client import GeminiClient
from utils.logger import logger

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
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
    
    return parser.parse_args()

def setup_logging(debug: bool = False) -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        debug (bool): Se True, ativa logging detalhado (DEBUG level)
    """
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    
    # Garante que todos os handlers respeitam o nível de debug
    for handler in logger.handlers:
        handler.setLevel(level)
    
    if debug:
        logger.debug("Debug logging ativado")


def get_feed_urls(args: argparse.Namespace) -> List[str]:
    """
    Obtém a lista de URLs de feeds para processar.
    
    Args:
        args: Argumentos da linha de comando
        
    Returns:
        List[str]: Lista de URLs de feeds RSS
    """
    if args.feeds:
        feeds = [feed.strip() for feed in args.feeds.split(',')]
        logger.info(f"Usando {len(feeds)} feeds específicos fornecidos via CLI")
        return feeds
    
    logger.info(f"Usando {len(RSS_FEED_URLS)} feeds padrão do arquivo de configuração")
    return RSS_FEED_URLS

def test_connections() -> bool:
    """
    Testa as conexões com APIs externas antes de executar o processo principal.
    
    Testa:
    1. Conexão com a API do Gemini (para geração de resumos)
    2. Conexão SMTP (para envio de emails)
    
    Returns:
        bool: True se todas as conexões foram bem-sucedidas, False caso contrário
    """
    logger.info("=== Testando Conexões ===")
    
    # Teste 1: API do Gemini
    try:
        logger.info("1. Testando conexão com API do Gemini...")
        client = GeminiClient(GEMINI_API_KEY)
        
        logger.info("Inicializando modelo Gemini...")
        if not client.initialize_model():
            raise Exception("Falha ao inicializar modelo Gemini")
        
        logger.info("✓ Conexão com API do Gemini bem-sucedida")
        
    except Exception as e:
        logger.error(f"✗ Falha na conexão com API do Gemini: {str(e)}")
        return False
    
    # Teste 2: Servidor SMTP
    try:
        logger.info("2. Testando conexão SMTP...")
        
        with smtplib.SMTP(EMAIL_SETTINGS['smtp_server'], EMAIL_SETTINGS['smtp_port']) as server:
            logger.info("Servidor SMTP conectado, iniciando TLS...")
            server.starttls()
            
            logger.info("TLS iniciado, tentando login...")
            server.login(EMAIL_SETTINGS['sender_email'], EMAIL_SETTINGS['sender_password'])
            
        logger.info("✓ Conexão SMTP bem-sucedida")
        
    except Exception as e:
        logger.error(f"✗ Falha na conexão SMTP: {str(e)}")
        return False
    
    logger.info("✓ Todos os testes de conexão foram bem-sucedidos!")
    return True

def process_news(days: int = 1, feed_urls: Optional[List[str]] = None, dry_run: bool = False) -> None:
    """
    Processa notícias dos feeds RSS e envia resumo por email.
    
    Args:
        days (int): Número de dias de notícias para processar
        feed_urls (Optional[List[str]]): URLs específicos de feeds ou None para usar padrão
        dry_run (bool): Se True, executa sem enviar email
        
    Raises:
        Exception: Re-propaga exceções de processamento
    """
    try:
        logger.info("=== Iniciando Processamento de Notícias ===")
        logger.info(f"Processando notícias dos últimos {days} dias")
        
        # Usa feeds fornecidos ou padrão
        feeds_to_process = feed_urls or RSS_FEED_URLS
        logger.info(f"Usando {len(feeds_to_process)} feeds RSS")
        
        # Inicializa o leitor RSS
        rss_reader = RssReader(feeds_to_process)
        
        # Define intervalo de datas com timezone awareness
        date_cutoff = datetime.now(pytz.UTC) - timedelta(days=days)
        end_date = datetime.now(pytz.UTC)
        logger.info(f"Intervalo de datas: {date_cutoff.date()} até {end_date.date()}")
        
        # Busca e processa feeds RSS
        news_items = rss_reader.fetch_news(days=days)
        logger.info(f"Coletados {len(news_items) if news_items else 0} itens dos feeds RSS")
        
        # Filtra itens por data
        news_items = [
            item for item in news_items 
            if item.published_date is not None and item.published_date >= date_cutoff
        ]
        
        if not news_items:
            logger.warning("Nenhum item de notícia encontrado no intervalo de datas especificado.")
            return
        
        logger.info(f"Encontrados {len(news_items)} itens no intervalo de datas")
        
        # Inicializa o resumidor
        summarizer = Summarizer()
        
        # Gera resumos agrupados por dia
        summary = summarizer.summarize(news_items, days=days)
        
        logger.info("=== SAÍDA DO RESUMIDOR - DEBUG ===")
        logger.info(f"Tipo de resumo: {type(summary)}")
        logger.info(f"Chaves do resumo: {list(summary.keys()) if hasattr(summary, 'keys') else 'Não é um dicionário'}")
        logger.info(f"Conteúdo do resumo: {summary}")
        
        if not summary:
            logger.warning("Nenhum resumo foi gerado. Verifique a conexão com a API do Gemini.")
            return
        
        if dry_run:
            logger.info("=== MODO DRY RUN - Email conteria: ===")
            logger.info(f"Resumos gerados para {len(summary)} dias/seções")
            for key in summary.keys():
                if key != 'linkedin_content':
                    logger.info(f"Data: {key}")
            return
        
        # Inicializa e envia email
        email_sender = EmailSender(EMAIL_SETTINGS)
        email_sender.send_email(summary)
        
        logger.info("✓ Processamento de notícias concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"✗ Falha no processamento: {str(e)}")
        raise


def main() -> None:
    """Função principal da aplicação."""
    try:
        args = parse_args()
        setup_logging(args.debug)
        
        logger.info("=== RSS Feed Processor Iniciado ===")
        logger.info(f"Argumentos: days={args.days}, dry_run={args.dry_run}, debug={args.debug}")
        
        # Testa conexões antes de prosseguir
        if not test_connections():
            logger.error("✗ Testes de conexão falharam. Verifique suas configurações.")
            sys.exit(1)
        
        # Processa notícias
        process_news(
            days=args.days,
            feed_urls=get_feed_urls(args) if args.feeds else None,
            dry_run=args.dry_run
        )
        
        logger.info("=== Aplicação Finalizada ===")
        
    except KeyboardInterrupt:
        logger.info("Aplicação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro fatal na aplicação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
