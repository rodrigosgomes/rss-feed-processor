#!/usr/bin/env python3
"""
Final Validation Script for RSS Feed Processor

Este script executa uma validação completa do sistema refatorado,
testando todas as funcionalidades principais e verificando se
o sistema está pronto para produção.

Author: Rodrigo Gomes
Date: 2025
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple, Dict

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.config import load_configuration, Configuration, ConfigurationError
from app import RSSFeedProcessor, create_app
from utils.connection_tester import ConnectionTester
from utils.logger import setup_logger


class ValidationResult:
    """Resultado de uma validação."""
    
    def __init__(self, test_name: str, success: bool, message: str, duration: float = 0.0):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.duration = duration
    
    def __str__(self):
        status = "✅ PASS" if self.success else "❌ FAIL"
        return f"{status} | {self.test_name:<30} | {self.message}"


class FinalValidator:
    """Validador final do sistema."""
    
    def __init__(self):
        self.logger = setup_logger(debug=True)
        self.results: List[ValidationResult] = []
        self.config: Configuration = None
    
    def run_validation(self) -> bool:
        """Executa validação completa."""
        self.logger.info("🚀 Iniciando Validação Final do RSS Feed Processor")
        self.logger.info("=" * 60)
        
        # Lista de testes a executar
        tests = [
            self._test_configuration_loading,
            self._test_configuration_validation,
            self._test_cli_help,
            self._test_cli_validate_command,
            self._test_cli_list_feeds,
            self._test_cli_argument_parsing,
            self._test_app_creation,
            self._test_connection_testing,
            self._test_backward_compatibility,
            self._test_documentation_examples,
        ]
        
        # Executa cada teste
        for test_func in tests:
            try:
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time
                result.duration = duration
                self.results.append(result)
                
                if result.success:
                    self.logger.info(f"✅ {result.test_name}: {result.message}")
                else:
                    self.logger.error(f"❌ {result.test_name}: {result.message}")
                    
            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0.0
                result = ValidationResult(
                    test_func.__name__,
                    False,
                    f"Exceção: {str(e)}",
                    duration
                )
                self.results.append(result)
                self.logger.error(f"❌ {result.test_name}: {result.message}")
        
        # Relatório final
        self._print_final_report()
        
        # Retorna True se todos os testes passaram
        return all(result.success for result in self.results)
    
    def _test_configuration_loading(self) -> ValidationResult:
        """Testa carregamento de configuração."""
        try:
            self.config = load_configuration()
            return ValidationResult(
                "Configuration Loading",
                True,
                f"Configuração carregada ({len(self.config.feed_urls)} feeds)"
            )
        except Exception as e:
            return ValidationResult(
                "Configuration Loading",
                False,
                f"Erro ao carregar configuração: {str(e)}"
            )
    
    def _test_configuration_validation(self) -> ValidationResult:
        """Testa validação de configuração."""
        try:
            if not self.config:
                self.config = load_configuration()
            
            self.config.validate()
            return ValidationResult(
                "Configuration Validation",
                True,
                "Configuração validada com sucesso"
            )
        except ConfigurationError as e:
            return ValidationResult(
                "Configuration Validation",
                False,
                f"Erro de validação: {str(e)}"
            )
    
    def _test_cli_help(self) -> ValidationResult:
        """Testa comando de ajuda da CLI."""
        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "RSS Feed Processor" in result.stdout:
                return ValidationResult(
                    "CLI Help Command",
                    True,
                    "Comando de ajuda funcionando"
                )
            else:
                return ValidationResult(
                    "CLI Help Command",
                    False,
                    f"Falha no comando de ajuda (código: {result.returncode})"
                )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "CLI Help Command",
                False,
                "Timeout no comando de ajuda"
            )
    
    def _test_cli_validate_command(self) -> ValidationResult:
        """Testa comando validate da CLI."""
        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "validate"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return ValidationResult(
                    "CLI Validate Command",
                    True,
                    "Comando validate executado com sucesso"
                )
            else:
                return ValidationResult(
                    "CLI Validate Command",
                    False,
                    f"Falha no comando validate (código: {result.returncode})"
                )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "CLI Validate Command",
                False,
                "Timeout no comando validate"
            )
    
    def _test_cli_list_feeds(self) -> ValidationResult:
        """Testa comando list-feeds da CLI."""
        try:
            result = subprocess.run(
                [sys.executable, "cli.py", "list-feeds", "--format", "simple"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "feeds configurados" in result.stderr:
                return ValidationResult(
                    "CLI List Feeds Command",
                    True,
                    "Comando list-feeds funcionando"
                )
            else:
                return ValidationResult(
                    "CLI List Feeds Command",
                    False,
                    f"Falha no comando list-feeds (código: {result.returncode})"
                )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "CLI List Feeds Command",
                False,
                "Timeout no comando list-feeds"
            )
    
    def _test_cli_argument_parsing(self) -> ValidationResult:
        """Testa parsing inteligente de argumentos."""
        test_cases = [
            ["--days", "3", "--dry-run"],
            ["--debug", "--days", "1"],
            ["--dry-run"],
        ]
        
        for args in test_cases:
            try:
                result = subprocess.run(
                    [sys.executable, "cli.py"] + args + ["--skip-test"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    return ValidationResult(
                        "CLI Argument Parsing",
                        False,
                        f"Falha no parsing de argumentos: {args}"
                    )
            except subprocess.TimeoutExpired:
                return ValidationResult(
                    "CLI Argument Parsing",
                    False,
                    f"Timeout no parsing de argumentos: {args}"
                )
        
        return ValidationResult(
            "CLI Argument Parsing",
            True,
            "Parsing inteligente de argumentos funcionando"
        )
    
    def _test_app_creation(self) -> ValidationResult:
        """Testa criação da aplicação."""
        try:
            if not self.config:
                self.config = load_configuration()
            
            app = RSSFeedProcessor(self.config)
            
            # Testa propriedades lazy loading
            _ = app.rss_reader
            _ = app.summarizer
            _ = app.email_sender
            _ = app.connection_tester
            
            return ValidationResult(
                "App Creation",
                True,
                "Aplicação criada com lazy loading funcionando"
            )
        except Exception as e:
            return ValidationResult(
                "App Creation",
                False,
                f"Erro na criação da aplicação: {str(e)}"
            )
    
    def _test_connection_testing(self) -> ValidationResult:
        """Testa funcionalidade de teste de conexões."""
        try:
            if not self.config:
                self.config = load_configuration()
            
            tester = ConnectionTester(self.config.gemini_api_key, self.config.email_settings)
            
            # Testa conexão Gemini
            gemini_result = tester.test_gemini_connection()
            
            if gemini_result:
                return ValidationResult(
                    "Connection Testing",
                    True,
                    "Testes de conexão funcionando"
                )
            else:
                return ValidationResult(
                    "Connection Testing",
                    False,
                    "Falha no teste de conexão Gemini"
                )
        except Exception as e:
            return ValidationResult(
                "Connection Testing",
                False,
                f"Erro nos testes de conexão: {str(e)}"
            )
    
    def _test_backward_compatibility(self) -> ValidationResult:
        """Testa compatibilidade com versão anterior."""
        try:
            # Verifica se main.py ainda funciona
            from main import main as legacy_main
            
            return ValidationResult(
                "Backward Compatibility",
                True,
                "Interface legada disponível"
            )
        except ImportError as e:
            return ValidationResult(
                "Backward Compatibility",
                False,
                f"Erro na compatibilidade: {str(e)}"
            )
    
    def _test_documentation_examples(self) -> ValidationResult:
        """Verifica se os exemplos da documentação funcionam."""
        # Testa alguns comandos básicos mencionados no README
        examples = [
            ["validate"],
            ["list-feeds", "--format", "simple"],
            ["test", "--component", "config"],
        ]
        
        for example in examples:
            try:
                result = subprocess.run(
                    [sys.executable, "cli.py"] + example,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    return ValidationResult(
                        "Documentation Examples",
                        False,
                        f"Exemplo da documentação falhou: {example}"
                    )
            except subprocess.TimeoutExpired:
                return ValidationResult(
                    "Documentation Examples",
                    False,
                    f"Timeout no exemplo: {example}"
                )
        
        return ValidationResult(
            "Documentation Examples",
            True,
            "Exemplos da documentação funcionando"
        )
    
    def _print_final_report(self):
        """Imprime relatório final."""
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info("📊 RELATÓRIO FINAL DE VALIDAÇÃO")
        self.logger.info("=" * 60)
        
        for result in self.results:
            print(result)
        
        self.logger.info("=" * 60)
        self.logger.info(f"📈 Resultados: {passed}/{total} testes passaram ({success_rate:.1f}%)")
        
        if success_rate == 100:
            self.logger.info("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para produção.")
        elif success_rate >= 80:
            self.logger.info("⚠️ Maioria dos testes passou, mas há issues para resolver.")
        else:
            self.logger.error("❌ Muitos testes falharam. Sistema necessita correções.")
        
        self.logger.info("=" * 60)


def main():
    """Função principal."""
    validator = FinalValidator()
    success = validator.run_validation()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
