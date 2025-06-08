#!/usr/bin/env python3
"""
Email Sender Module - Envio de Emails com Resumos de Notícias

Este módulo é responsável por:
1. Renderizar templates HTML com conteúdo de notícias
2. Configurar e enviar emails via SMTP
3. Separar conteúdo LinkedIn do conteúdo de notícias
4. Gerar estatísticas dos dados processados

Author: Rodrigo Gomes
Date: 2024
"""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Any, Optional
import os

from jinja2 import Environment, FileSystemLoader

from utils.logger import logger


class EmailSendError(Exception):
    """Exceção customizada para erros de envio de email."""
    pass


class EmailSender:
    """
    Classe responsável por enviar emails com resumos de notícias.
    
    Utiliza templates Jinja2 para renderizar o conteúdo HTML
    e SMTP para envio dos emails.
    """
    
    def __init__(self, email_settings: Dict[str, Any]):
        """
        Inicializa o enviador de emails.
        
        Args:
            email_settings (Dict[str, Any]): Configurações SMTP e credenciais
        """
        self.settings = email_settings
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates'))        )
        logger.info("✓ Enviador de email inicializado")

    def send_email(self, news_by_date: Dict[Any, Any]) -> None:
        """
        Envia email com resumos de notícias organizados por data.
        
        Args:
            news_by_date (Dict[Any, Any]): Dicionário com notícias agrupadas por data
                                          e conteúdo LinkedIn opcional
            
        Raises:
            EmailSendError: Se ocorrer erro no envio do email
        """
        try:
            if not news_by_date:
                raise EmailSendError("Nenhum item de notícia para enviar")

            logger.info("=== Preparando Email ===")
            
            # Separa conteúdo de notícias do conteúdo LinkedIn
            filtered_news = {}
            linkedin_content = None
            
            for key, value in news_by_date.items():
                if key == 'linkedin_content':
                    linkedin_content = value
                    logger.info("✓ Conteúdo LinkedIn encontrado")
                elif (isinstance(key, datetime) or 
                      isinstance(key, str) or 
                      hasattr(key, 'year')):
                    if isinstance(value, dict) and 'items' in value:
                        filtered_news[key] = value
                        logger.info(f"✓ Processando {len(value['items'])} artigos para {key}")

            if not filtered_news:
                raise EmailSendError("Nenhum item de notícia válido encontrado nos dados")            
            # Renderiza template HTML com os dados
            template = self.template_env.get_template('email_template.html')
            template_data = {
                'news_by_date': filtered_news,
                'linkedin_content': linkedin_content,
                'stats': self._generate_stats(filtered_news)
            }
            
            html_content = template.render(**template_data)
            msg = MIMEMultipart('alternative')            # Gera linha de assunto baseada no intervalo de datas
            dates = sorted(list(filtered_news.keys()))
            
            if len(dates) == 1:
                subject = f"Resumo Diário de Notícias - {dates[0].strftime('%Y-%m-%d')}"
            else:
                subject = f"Resumo de Notícias {dates[0].strftime('%Y-%m-%d')} a {dates[-1].strftime('%Y-%m-%d')}"
            
            msg['Subject'] = subject
            msg['From'] = self.settings['sender_email']
            
            # Obtém lista de destinatários
            recipients = self.settings.get('recipients', [])
            if not recipients:
                # Fallback para compatibilidade com configuração antiga
                recipient_email = self.settings.get('recipient_email', '')
                if recipient_email:
                    recipients = [recipient_email]
                else:
                    raise EmailSendError("Nenhum destinatário configurado")
            
            msg['To'] = ', '.join(recipients)
            msg.attach(MIMEText(html_content, 'html'))

            # Conecta e envia via SMTP
            logger.info("Conectando ao servidor SMTP")
            try:
                with smtplib.SMTP(self.settings['smtp_server'], self.settings['smtp_port']) as server:
                    server.starttls()
                    logger.info("Realizando login SMTP")
                    server.login(self.settings['sender_email'], self.settings['sender_password'])
                    logger.info("Enviando email")
                    # Envia para todos os destinatários
                    server.send_message(msg, to_addrs=recipients)
                    logger.info("✓ Email enviado com sucesso!")
            except Exception as smtp_error:
                raise EmailSendError(f"Falha no envio do email: {str(smtp_error)}")

        except Exception as e:
            logger.error(f"✗ Falha no envio do email: {str(e)}")
            raise EmailSendError(str(e))

    def _generate_stats(self, news_data: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Gera estatísticas dos dados de notícias para incluir no email.
        
        Args:
            news_data (Dict[Any, Any]): Dados de notícias agrupados por data
            
        Returns:
            Dict[str, Any]: Estatísticas incluindo total de artigos, dias e fontes
        """
        total_articles = sum(len(date_data['items']) for date_data in news_data.values())
        sources = set()
        
        for date_data in news_data.values():
            for item in date_data['items']:
                if hasattr(item, 'source'):
                    sources.add(item.source)
                
        return {
            'total_articles': total_articles,
            'total_days': len(news_data),
            'total_sources': len(sources),
            'sources': list(sources)
        }