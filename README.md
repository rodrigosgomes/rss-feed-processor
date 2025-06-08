# RSS Feed Processor

**Sistema Inteligente de Processamento de Feeds RSS** - Agora com Arquitetura Refatorada! 🎉

Este projeto é um processador automatizado de feeds RSS que:
- 📰 Lê artigos de múltiplas fontes RSS
- 🤖 Gera resumos inteligentes usando Google Gemini AI
- 📧 Envia emails diários formatados em HTML
- 📱 Cria conteúdo otimizado para LinkedIn
- 🏗️ **NOVO**: Arquitetura modular com Application Factory Pattern
- 🖥️ **NOVO**: Interface CLI moderna com múltiplos comandos

## 🆕 Nova Arquitetura (2025)

O projeto foi completamente refatorado com:

### 🏗️ Application Factory Pattern
- **Injeção de Dependências**: Lazy loading de componentes
- **Configuração Centralizada**: Dataclasses com validação robusta
- **Separação de Responsabilidades**: Módulos independentes e testáveis
- **Melhores Práticas**: Seguindo padrões modernos de Python

### 🖥️ Interface CLI Moderna
```bash
# Nova interface principal (recomendada)
python cli.py run --dry-run --days 3
python cli.py test
python cli.py validate
python cli.py list-feeds

# Interface legada (mantida para compatibilidade)
python src/main.py --dry-run --days 3
```

### 🧪 Testes Abrangentes
- **Testes Unitários**: Cobertura completa dos módulos refatorados
- **Mocks e Fixtures**: Isolamento de dependências externas
- **Validação de Configuração**: Testes para sistema de configuração
- **CI/CD Ready**: Suite de testes preparada para automação

## ✨ Funcionalidades

- **Leitura Inteligente**: Processa múltiplos feeds RSS simultaneamente
- **Resumos com IA**: Utiliza Google Gemini para gerar resumos concisos
- **Email Automático**: Envia relatórios diários formatados
- **Conteúdo Social**: Gera posts otimizados para LinkedIn
- **Filtros de Data**: Processa notícias de períodos específicos
- **Logs Detalhados**: Sistema completo de logging e debug

## 🚀 Instalação Rápida

1. **Clone e configure o ambiente:**
```powershell
git clone <repo-url>
cd product_reader
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Configure as credenciais:**
   - Crie um arquivo `.env` na raiz do projeto
   - Configure suas credenciais (veja seção de Configuração)

3. **Execute o sistema:**
```powershell
.\run_app.ps1
```

## ⚙️ Configuração

### Arquivo `.env`
```env
# Configurações de Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=sua-senha-de-app
RECIPIENT_EMAIL=destinatario@email.com

# API do Google Gemini
GEMINI_API_KEY=sua-chave-api-gemini
```

### Feeds RSS (`src/config/feeds.txt`)
```
https://feeds.folha.uol.com.br/folha/dinheiro/rss091.xml
https://www.infomoney.com.br/feed/
https://valor.globo.com/rss/home/
```

## 📊 Uso

### 🖥️ Interface CLI Moderna (Recomendada)

```bash
# ✅ Execução básica com validação
python cli.py run                              # Processa últimas 24 horas
python cli.py run --days 3                     # Processa últimos 3 dias
python cli.py run --dry-run                    # Executa sem enviar email
python cli.py --debug run --dry-run            # Debug mode com dry-run

# 🚀 Atalhos inteligentes (NOVO!)
python cli.py --days 3                         # Atalho: processa últimos 3 dias
python cli.py --dry-run                        # Atalho: executa sem enviar email
python cli.py --debug --dry-run                # Atalho: debug + dry-run

# 🔧 Comandos de teste e validação
python cli.py test                             # Testa todas as conexões
python cli.py validate                         # Valida configuração
python cli.py list-feeds                       # Lista feeds configurados

# 🎯 Opções avançadas
python cli.py run --feeds "url1,url2"          # Usa feeds específicos
python cli.py run --skip-test                  # Pula teste de conexões
python cli.py --config custom.env run          # Usa arquivo de config customizado
```

### 📋 Comandos Disponíveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `run` | Executa processamento completo | `cli.py run --days 2` |
| `test` | Testa conexões (Gemini + SMTP) | `cli.py test` |
| `validate` | Valida configuração | `cli.py validate` |
| `list-feeds` | Lista feeds configurados | `cli.py list-feeds` |

### 🔄 Interface Legada (Compatibilidade)

```bash
# Interface original mantida para compatibilidade
python src/main.py --dry-run --days 3
python src/main.py --test-connections
python src/main.py --debug
```

### 🚀 Execução com PowerShell

...existing code...