#!/usr/bin/env python3
"""
Logger Module - Sistema de Logging Centralizado

Este módulo configura o sistema de logging para todo o projeto:
1. Configura formatação padronizada de logs
2. Define níveis de log apropriados
3. Fornece instância de logger global para uso em outros módulos

Author: Rodrigo Gomes
Date: 2024
"""

import logging


def setup_logger(debug: bool = False, name: str = 'RSSFeedProcessor') -> logging.Logger:
    """
    Configura e retorna uma instância de logger formatada para o projeto.
    
    Args:
        debug (bool): Se True, ativa nível DEBUG
        name (str): Nome do logger
    
    Returns:
        logging.Logger: Instância configurada do logger
    """
    # Cria logger principal
    logger = logging.getLogger(name)
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    # Evita duplicação se logger já foi configurado
    if logger.handlers:
        # Atualiza nível se necessário
        for handler in logger.handlers:
            handler.setLevel(level)
        return logger

    # Cria handler para console com formatação
    console = logging.StreamHandler()
    console.setLevel(level)
    
    # Cria formatador com timestamp e informações de nível
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Adiciona formatador ao handler
    console.setFormatter(formatter)
    
    # Adiciona handler ao logger
    logger.addHandler(console)
    
    return logger


# Instância global do logger para uso em outros módulos
logger = setup_logger()