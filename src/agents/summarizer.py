#!/usr/bin/env python3
"""
Summarizer Module - Geração de Resumos com IA

Este módulo é responsável por:
1. Agrupar artigos de notícias por data
2. Gerar resumos individuais usando IA (Gemini)
3. Criar conteúdo otimizado para LinkedIn
4. Organizar os dados para envio por email

Author: Rodrigo Gomes
Date: 2024
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz

from config.settings import GEMINI_API_KEY
from models.news_item import NewsItem
from templates.prompts import ARTICLE_SUMMARY_PROMPT, LINKEDIN_CONTENT_PROMPT
from utils.gemini_client import GeminiClient
from utils.logger import logger


class Summarizer:
    """
    Classe responsável por gerar resumos de notícias usando IA.
    
    Utiliza a API do Google Gemini para:
    - Gerar resumos individuais de artigos
    - Criar conteúdo otimizado para LinkedIn
    - Organizar dados por data para email
    """
    
    def __init__(self):
        """Inicializa o resumidor com cliente Gemini."""
        logger.info("Inicializando resumidor de IA Gemini")
        self.client = GeminiClient(GEMINI_API_KEY)
        self.client.initialize_model()

    def _generate_social_content(self, news_items: List[NewsItem]) -> Optional[str]:
        """
        Gera conteúdo otimizado para LinkedIn baseado nos artigos.
        
        Args:
            news_items (List[NewsItem]): Lista de artigos de notícias
            
        Returns:
            Optional[str]: Conteúdo para LinkedIn ou None se falhar
        """
        try:
            logger.info("Gerando conteúdo para LinkedIn")
            
            # Prepara texto consolidado dos artigos
            articles_text = "\n\n".join([
                f"Título: {item.title}\n"
                f"Resumo: {item.summary or item.description}\n" 
                f"Fonte: {item.source}"
                for item in news_items
            ])
            
            # Gera conteúdo usando prompt específico
            prompt = LINKEDIN_CONTENT_PROMPT.format(articles_text=articles_text)
            response = self.client.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("Não foi possível gerar conteúdo para LinkedIn")
                return None
                
            # Limpa formatação do post
            content = response.text
            if "Post:" in content:
                content = content.split("Post:", 1)[1].strip()
            
            logger.info("✓ Conteúdo para LinkedIn gerado com sucesso")
            return content
            
        except Exception as e:
            logger.error(f"✗ Erro gerando conteúdo para LinkedIn: {str(e)}")
            return None

    def summarize(self, news_items: List[NewsItem], days: int = 1) -> Dict[Any, Any]:
        """
        Processa e resume lista de artigos, agrupando por data.
        
        Args:
            news_items (List[NewsItem]): Lista de artigos para resumir
            days (int): Número de dias para filtrar (usado para validação)
              Returns:
            Dict[Any, Any]: Dicionário com artigos resumidos agrupados por data
                           e conteúdo LinkedIn opcional
        """
        logger.info("=== Iniciando Geração de Resumos ===")
        logger.info(f"Total de artigos a processar: {len(news_items)}")
        
        # Obtém intervalo de datas em UTC - mesma lógica do main.py
        date_cutoff = datetime.now(pytz.UTC) - timedelta(days=days)
        end_date = datetime.now(pytz.UTC)
        logger.info(f"Intervalo de datas: {date_cutoff.date()} a {end_date.date()}")
        
        # Filtra artigos para o intervalo especificado
        filtered_news = [
            item for item in news_items 
            if item.published_date >= date_cutoff
        ]
        
        if not filtered_news:
            logger.warning(f"Nenhum artigo encontrado entre {date_cutoff.date()} e {end_date.date()}")
            return {}
            
        logger.info(f"Encontrados {len(filtered_news)} artigos no intervalo")
        
        # Agrupa artigos por data e gera resumos
        summarized_news = {}
        
        for item in filtered_news:
            try:
                item_date = item.published_date.date()
                
                # Inicializa estrutura para a data se necessário
                if item_date not in summarized_news:
                    summarized_news[item_date] = {'items': []}
                    
                # Gera resumo para o artigo
                summary = self._generate_article_summary(item)
                
                # Cria novo item com resumo
                summarized_item = item.__class__(
                    title=item.title,
                    description=item.description,
                    link=item.link,
                    published_date=item.published_date,
                    source=item.source,
                    summary=summary
                )
                
                summarized_news[item_date]['items'].append(summarized_item)
                
            except Exception as e:
                logger.error(f"Erro ao processar artigo '{item.title}': {str(e)}")
                
                # Inclui artigo sem resumo em caso de erro
                item.summary = "Erro ao gerar resumo para este artigo."
                item_date = item.published_date.date()
                
                if item_date not in summarized_news:
                    summarized_news[item_date] = {'items': []}
                    
                summarized_news[item_date]['items'].append(item)
        
        # Gera conteúdo para LinkedIn
        linkedin_content = self._generate_social_content(filtered_news)
        if linkedin_content:
            summarized_news['linkedin_content'] = linkedin_content
        
        logger.info(f"✓ Resumos finalizados para {len(summarized_news)} dias/seções")
        return summarized_news

    def _generate_article_summary(self, news_item: NewsItem) -> str:
        """
        Gera o resumo para um único artigo de notícia.
        
        Args:
            news_item (NewsItem): O artigo de notícia a ser resumido
            
        Returns:
            str: O resumo gerado para o artigo
        """
        try:
            logger.info(f"Gerando resumo para o artigo: {news_item.title}")
            prompt = ARTICLE_SUMMARY_PROMPT.format(
                title=news_item.title,
                description=news_item.description,
                source=news_item.source
            )
            response = self.client.generate_content(prompt)
            logger.info("✓ Resumo do artigo gerado com sucesso")
            return response.text
        except Exception as e:
            logger.error(f"✗ Erro ao gerar resumo do artigo: {str(e)}")
            return "Erro ao gerar resumo. Por favor, verifique os logs."
