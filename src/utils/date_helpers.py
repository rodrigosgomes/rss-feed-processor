#!/usr/bin/env python3
"""
Date Helpers Module - Utilitários para Manipulação de Datas

Este módulo fornece funções utilitárias para:
1. Formatação e parsing de datas em diferentes formatos
2. Conversão entre fusos horários
3. Cálculo de intervalos de datas
4. Agrupamento de notícias por data

Author: Rodrigo Gomes
Date: 2024
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union, Any
from zoneinfo import ZoneInfo

import pytz


def format_date(date: Union[datetime, str]) -> str:
    """
    Converte datetime ou string de data para formato brasileiro.
    
    Args:
        date (Union[datetime, str]): Data a ser formatada
        
    Returns:
        str: Data formatada em português brasileiro
    """
    if isinstance(date, str):
        date = parse_date_string(date)
    
    # Garante que a data tenha informação de timezone
    if date.tzinfo is None:
        date = date.replace(tzinfo=pytz.UTC)
    
    # Converte para horário de Brasília para exibição
    local_tz = ZoneInfo('America/Sao_Paulo')
    local_date = date.astimezone(local_tz)
    
    # Formata em português brasileiro
    months = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    month_name = months[local_date.month]
    return f"{local_date.day} de {month_name} de {local_date.year}"


def parse_date_string(date_str: str) -> datetime:
    """
    Converte string de data em vários formatos para objeto datetime.
    
    Args:
        date_str (str): String de data a ser convertida
        
    Returns:
        datetime: Objeto datetime com timezone UTC se não especificado
        
    Raises:
        ValueError: Se não conseguir fazer parse da string
    """
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',      # ISO com timezone
        '%Y-%m-%dT%H:%M:%SZ',       # ISO UTC
        '%Y-%m-%dT%H:%M:%S.%f%z',   # ISO com microssegundos e timezone
        '%Y-%m-%dT%H:%M:%S.%fZ',    # ISO com microssegundos UTC
        '%a, %d %b %Y %H:%M:%S %z', # RFC822 com timezone
        '%a, %d %b %Y %H:%M:%S %Z', # RFC822 com nome do timezone
        '%Y-%m-%d %H:%M:%S',        # Formato básico
        '%Y-%m-%d',                 # Apenas data
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # Se não tem timezone, assume UTC
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=pytz.UTC)
            return parsed_date
        except ValueError:
            continue
    
    raise ValueError(f"Não foi possível fazer parse da data: {date_str}")


def get_date_range(days: int = 1) -> Tuple[datetime, datetime]:
    """
    Obtém intervalo de datas para um número específico de dias.
    
    Args:
        days (int): Número de dias para o intervalo
        
    Returns:
        Tuple[datetime, datetime]: Data inicial e final do intervalo
    """
    local_tz = ZoneInfo('America/Sao_Paulo')
    end_date = datetime.now(local_tz)
    
    # Define fim do dia (23:59:59)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Calcula data inicial e define início do dia (00:00:00)
    start_date = (end_date - timedelta(days=days-1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    return start_date, end_date


def group_news_by_date(news_items: List[Any]) -> Dict[str, List[Any]]:
    """
    Agrupa itens de notícias por data de publicação.
    
    Args:
        news_items (List[Any]): Lista de itens de notícias
        
    Returns:
        Dict[str, List[Any]]: Dicionário com notícias agrupadas por data formatada
    """
    grouped_news = defaultdict(list)
    
    for item in news_items:
        if hasattr(item, 'published_date') and item.published_date:
            try:
                pub_date = format_date(item.published_date)
                grouped_news[pub_date].append(item)
            except Exception as e:
                print(f"Erro ao formatar data para item {item.title}: {str(e)}")
                continue
                
    return dict(grouped_news)