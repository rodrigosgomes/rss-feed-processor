#!/usr/bin/env python3
"""
RSS Feed Processor Application

Este módulo implementa o Application Factory Pattern para criar
uma instância configurada da aplicação RSS Feed Processor.

Author: Rodrigo Gomes
Date: 2025
"""

from dataclasses import dataclass
from typing import List, Optional
import logging

from agents.rss_reader import RssReader
from agents.summarizer import Summarizer
from config.config import load_configuration, Configuration
from utils.email_sender import EmailSender
from utils.connection_tester import ConnectionTester
from utils.logger import setup_logger


@dataclass
class ProcessingResult:
    """Resultado do processamento de feeds RSS."""
    articles_found: int
    articles_processed: int
    summaries_generated: int
    emails_sent: int
    success: bool
    errors: List[str]


class RSSFeedProcessor:
    """
    Classe principal da aplicação RSS Feed Processor.
    
    Implementa o padrão Application Factory para criar uma instância
    configurada da aplicação com todas as dependências injetadas.
    """
    
    def __init__(self, config: Configuration):
        """
        Inicializa o processador com configuração.
        
        Args:
            config: Configuração da aplicação
        """
        self.config = config
        self.logger = setup_logger(debug=config.debug)
          # Dependências serão injetadas no momento da execução (lazy loading)
        self._rss_reader: Optional[RssReader] = None
        self._summarizer: Optional[Summarizer] = None
        self._email_sender: Optional[EmailSender] = None
        self._connection_tester: Optional[ConnectionTester] = None
    
    @property
    def rss_reader(self) -> RssReader:
        """Lazy loading do RSS Reader."""
        if self._rss_reader is None:
            self._rss_reader = RssReader(self.config.feed_urls)
        return self._rss_reader
    
    @property
    def summarizer(self) -> Summarizer:
        """Lazy loading do Summarizer."""
        if self._summarizer is None:
            self._summarizer = Summarizer()
        return self._summarizer
    
    @property
    def email_sender(self) -> EmailSender:
        """Lazy loading do Email Sender."""
        if self._email_sender is None:
            self._email_sender = EmailSender(self.config.email_settings)
        return self._email_sender
    
    @property
    def connection_tester(self) -> ConnectionTester:
        """Lazy loading do Connection Tester."""
        if self._connection_tester is None:
            self._connection_tester = ConnectionTester(
                self.config.gemini_api_key, 
                self.config.email_settings
            )
        return self._connection_tester
    
    def test_connections(self) -> bool:
        """
        Testa todas as conexões necessárias.
        
        Returns:
            bool: True se todas as conexões estão funcionando
        """
        self.logger.info("🔧 Testando conexões...")
        return self.connection_tester.test_all()
    
    def list_feeds(self) -> List[str]:
        """
        Retorna lista de feeds configurados.
        
        Returns:
            List[str]: Lista de URLs de feeds RSS
        """
        return self.config.feed_urls
    
    def process_feeds(self, feeds: Optional[List[str]] = None, 
                     days_back: int = 1, dry_run: bool = False) -> ProcessingResult:
        """
        Processa feeds RSS e gera resumos.
        
        Args:
            feeds: URLs específicos de feeds ou None para usar configuração
            days_back: Número de dias para buscar artigos
            dry_run: Se True, não envia emails
            
        Returns:
            ProcessingResult: Resultado do processamento
        """
        result = ProcessingResult(
            articles_found=0,
            articles_processed=0,
            summaries_generated=0,
            emails_sent=0,
            success=False,
            errors=[]
        )
        
        try:
            self.logger.info(f"🚀 Iniciando processamento (últimos {days_back} dias)")
            
            # Usar feeds customizados se fornecidos
            if feeds:
                self.logger.info(f"📡 Usando {len(feeds)} feeds customizados")
                # Cria novo reader com feeds customizados
                rss_reader = RssReader(feeds)
            else:
                self.logger.info(f"📡 Usando {len(self.config.feed_urls)} feeds configurados")
                rss_reader = self.rss_reader
            
            # 1. Buscar artigos
            self.logger.info("📰 Buscando artigos dos feeds RSS...")
            articles = rss_reader.fetch_news(days=days_back)
            result.articles_found = len(articles) if articles else 0
            
            if not articles:
                self.logger.warning("⚠️ Nenhum artigo encontrado")
                result.success = True  # Não é erro, apenas não há conteúdo
                return result
            
            self.logger.info(f"✅ Encontrados {len(articles)} artigos")
            result.articles_processed = len(articles)
            
            # 2. Gerar resumos
            self.logger.info("🤖 Gerando resumos com IA...")
            summaries = self.summarizer.summarize(articles, days=days_back)
            
            if summaries:
                # Conta número de seções de resumo (excluindo linkedin_content)
                result.summaries_generated = len([k for k in summaries.keys() if k != 'linkedin_content'])
                self.logger.info(f"✅ Gerados resumos para {result.summaries_generated} seções")
            else:
                self.logger.error("❌ Falha ao gerar resumos")
                result.errors.append("Falha na geração de resumos")
                return result
            
            # 3. Enviar email (se não for dry run)
            if dry_run:
                self.logger.info("🔍 DRY RUN - Email não será enviado")
                self._log_dry_run_content(summaries)
                result.emails_sent = 0
            else:
                self.logger.info("📧 Enviando email...")
                try:
                    self.email_sender.send_email(summaries)
                    result.emails_sent = 1
                    self.logger.info("✅ Email enviado com sucesso")
                except Exception as e:
                    self.logger.error(f"❌ Falha ao enviar email: {e}")
                    result.errors.append(f"Falha no envio de email: {str(e)}")
                    return result
            
            result.success = True
            self.logger.info("🎉 Processamento concluído com sucesso!")
            
        except Exception as e:
            error_msg = f"Erro durante processamento: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            result.errors.append(error_msg)
        
        return result
    
    def _log_dry_run_content(self, summaries: dict) -> None:
        """Log do conteúdo que seria enviado por email no dry run."""
        self.logger.info("📋 Conteúdo que seria enviado:")
        for date, content in summaries.items():
            if date != 'linkedin_content':
                self.logger.info(f"  📅 {date}: {len(str(content))} caracteres")


def create_app(config_path: Optional[str] = None) -> RSSFeedProcessor:
    """
    Application Factory - Cria instância configurada da aplicação.
    
    Args:
        config_path: Caminho para arquivo de configuração opcional
        
    Returns:
        RSSFeedProcessor: Instância configurada da aplicação
    """
    if config_path:
        config = load_configuration(config_path)
    else:
        config = load_configuration()
    
    return RSSFeedProcessor(config)
