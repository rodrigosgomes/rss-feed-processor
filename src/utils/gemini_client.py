#!/usr/bin/env python3
"""
Gemini Client Module - Cliente para API do Google Gemini

Este módulo fornece interface para interação com a API do Google Gemini:
1. Inicialização de modelos com fallback para modelos gratuitos
2. Geração de conteúdo com retry automático
3. Tratamento de rate limiting e quota exceeded
4. Backoff exponencial para controle de requisições

Author: Rodrigo Gomes
Date: 2024
"""

import json
from time import sleep
from typing import Optional, Any

import google.generativeai as genai

from utils.logger import logger


class GeminiClient:
    """
    Cliente para interação com a API do Google Gemini.
    
    Gerencia conexões, retry automático e fallback entre modelos
    para garantir disponibilidade do serviço.
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa o cliente Gemini.
        
        Args:
            api_key (str): Chave da API do Google Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = None
        self.retry_count = 3
        self.base_delay = 5  # Delay base em segundos
        self.max_delay = 60  # Delay máximo em segundos
        
        # Modelos gratuitos disponíveis como fallback
        self.free_models = [
            'models/gemma-3-1b-it', 
            'models/gemma-3-4b-it', 
            'models/gemma-3-12b-it', 
            'models/gemma-3-27b-it'
        ]
        self.current_model_index = 0

    def initialize_model(self, model_name: str = 'gemini-1.5-flash') -> bool:
        """
        Inicializa o modelo Gemini com retries e fallback.
        
        Args:
            model_name (str): Nome do modelo preferido
            
        Returns:
            bool: True se inicialização bem-sucedida
        """
        self.preferred_model = model_name
        return self._try_initialize_model(model_name)

    def _try_initialize_model(self, model_name: str) -> bool:
        """
        Tenta inicializar um modelo específico com retries.
        
        Args:
            model_name (str): Nome do modelo a inicializar
            
        Returns:
            bool: True se bem-sucedido
        """
        for attempt in range(self.retry_count):
            try:
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"✓ Modelo inicializado com sucesso: {model_name}")
                return True
            except Exception as e:
                error_str = str(e)
                if ("quota" in error_str.lower() or "404" in error_str) and self._try_next_free_model():
                    return True
                if self._should_retry(e, attempt):
                    continue
                raise

    def _try_next_free_model(self) -> bool:
        """
        Tenta inicializar o próximo modelo gratuito disponível.
        
        Returns:
            bool: True se bem-sucedido
        """
        initial_index = self.current_model_index
        
        while True:
            try:
                if self.current_model_index >= len(self.free_models):
                    self.current_model_index = 0
                  # Se testamos todos os modelos, desiste
                if self.current_model_index == initial_index and initial_index != 0:
                    return False
                
                model_name = self.free_models[self.current_model_index]
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"✓ Alternando para modelo gratuito: {model_name}")
                self.current_model_index += 1  # Move para próximo modelo
                return True
            except Exception as e:
                logger.warning(f"✗ Falha ao inicializar modelo gratuito {self.free_models[self.current_model_index]}: {str(e)}")
                self.current_model_index += 1

    def generate_content(self, prompt: str) -> Any:
        """
        Gera conteúdo usando o modelo Gemini com retries automáticos.
        
        Args:
            prompt (str): Prompt para geração de conteúdo
            
        Returns:
            Any: Resposta do modelo Gemini
            
        Raises:
            Exception: Se falha em gerar conteúdo após todas as tentativas
        """
        if not self.model:
            if not self.initialize_model():
                raise Exception("Falha ao inicializar qualquer modelo")

        for attempt in range(self.retry_count):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                error_str = str(e)
                if ("quota" in error_str.lower() or "404" in error_str) and self._try_next_free_model():
                    # Tenta novamente com o novo modelo
                    try:
                        response = self.model.generate_content(prompt)
                        return response
                    except Exception as new_e:
                        logger.error(f"✗ Erro com modelo de fallback: {str(new_e)}")
                if self._should_retry(e, attempt):
                    continue
                raise

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determina se deve tentar novamente baseado no erro e tentativa.
        
        Args:
            error (Exception): Erro ocorrido
            attempt (int): Número da tentativa atual
            
        Returns:
            bool: True se deve tentar novamente
        """
        if attempt >= self.retry_count - 1:
            return False

        error_str = str(error)
        
        # Verifica se é erro de rate limit
        if "429" in error_str or "quota" in error_str.lower():
            delay = self._calculate_delay(attempt, error_str)
            logger.warning(f"Rate limit atingido. Aguardando {delay} segundos...")
            sleep(delay)
            return True
            
        # Outros erros retriáveis (server errors)
        if any(code in error_str for code in ["500", "502", "503", "504"]):
            delay = self._calculate_delay(attempt)
            logger.warning(f"Erro do servidor. Aguardando {delay} segundos...")
            sleep(delay)
            return True
            
        return False

    def _calculate_delay(self, attempt: int, error_str: Optional[str] = None) -> int:
        """
        Calcula tempo de delay para retry com backoff exponencial.
        
        Args:
            attempt (int): Número da tentativa
            error_str (Optional[str]): String do erro para extrair delay específico
            
        Returns:
            int: Tempo de delay em segundos
        """
        # Tenta extrair delay específico da mensagem de erro
        if error_str:
            try:
                if "retry_delay" in error_str:
                    error_dict = json.loads(error_str[error_str.find("{"):error_str.rfind("}")+1])
                    if "retry_delay" in error_dict:
                        return int(error_dict["retry_delay"]["seconds"])
            except:
                pass

        # Backoff exponencial padrão
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay

    def list_models(self) -> list:
        """
        Lista modelos disponíveis com lógica de retry.
        
        Returns:
            list: Lista de nomes dos modelos disponíveis
        """
        for attempt in range(self.retry_count):
            try:
                return [m.name for m in genai.list_models()]
            except Exception as e:
                if self._should_retry(e, attempt):
                    continue
                raise
