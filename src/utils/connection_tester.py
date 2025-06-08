#!/usr/bin/env python3
"""
Connection Tester - Utilitário para Testar Conexões

Este módulo é responsável por testar todas as conexões
necessárias antes da execução da aplicação.

Author: Rodrigo Gomes
Date: 2025
"""

import smtplib
from typing import Dict, Any
import logging

from utils.gemini_client import GeminiClient


logger = logging.getLogger(__name__)


class ConnectionTester:
    """
    Classe responsável por testar conexões com APIs e serviços externos.
    """
    
    def __init__(self, gemini_api_key: str, email_settings: Dict[str, Any]):
        """
        Inicializa o testador de conexões.
        
        Args:
            gemini_api_key: Chave da API do Gemini
            email_settings: Configurações de email SMTP
        """
        self.gemini_api_key = gemini_api_key
        self.email_settings = email_settings
    
    def test_gemini_connection(self) -> bool:
        """
        Testa conexão com a API do Gemini.
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            logger.info("🤖 Testando conexão com API do Gemini...")
            
            if not self.gemini_api_key:
                logger.error("❌ Chave da API do Gemini não configurada")
                return False
            
            client = GeminiClient(self.gemini_api_key)
            
            if not client.initialize_model():
                logger.error("❌ Falha ao inicializar modelo Gemini")
                return False
            
            logger.info("✅ Conexão com API do Gemini bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão com Gemini: {str(e)}")
            return False
    
    def test_smtp_connection(self) -> bool:
        """
        Testa conexão SMTP para envio de emails.
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            logger.info("📧 Testando conexão SMTP...")
            
            if not self.email_settings:
                logger.error("❌ Configurações de email não encontradas")
                return False
            
            required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password']
            for field in required_fields:
                if not self.email_settings.get(field):
                    logger.error(f"❌ Campo obrigatório ausente: {field}")
                    return False
            
            # Testa conexão real
            with smtplib.SMTP(
                self.email_settings['smtp_server'], 
                self.email_settings['smtp_port']
            ) as server:
                logger.debug("📡 Conectado ao servidor SMTP")
                server.starttls()
                logger.debug("🔐 TLS iniciado")
                server.login(
                    self.email_settings['sender_email'], 
                    self.email_settings['sender_password']
                )
                logger.debug("🔑 Login realizado")
            
            logger.info("✅ Conexão SMTP bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão SMTP: {str(e)}")
            return False
    
    def test_all(self) -> bool:
        """
        Executa todos os testes de conexão.
        
        Returns:
            bool: True se todas as conexões estão funcionando
        """
        logger.info("🔧 === Iniciando Testes de Conexão ===")
        
        results = []
        
        # Teste 1: API do Gemini
        gemini_ok = self.test_gemini_connection()
        results.append(gemini_ok)
        
        # Teste 2: SMTP
        smtp_ok = self.test_smtp_connection()
        results.append(smtp_ok)
        
        # Resultado final
        all_ok = all(results)
        
        if all_ok:
            logger.info("✅ Todos os testes de conexão passaram!")
        else:
            logger.error("❌ Alguns testes de conexão falharam")
            logger.error("🔧 Verifique suas configurações antes de prosseguir")
        
        return all_ok
    
    def get_connection_status(self) -> Dict[str, bool]:
        """
        Retorna status detalhado de todas as conexões.
        
        Returns:
            Dict[str, bool]: Status de cada conexão
        """
        return {
            'gemini': self.test_gemini_connection(),
            'smtp': self.test_smtp_connection()
        }
