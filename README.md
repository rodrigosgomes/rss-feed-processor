# RSS Feed Processor

**Sistema Inteligente de Processamento de Feeds RSS**

Este projeto é um processador automatizado de feeds RSS que:
- 📰 Lê artigos de múltiplas fontes RSS
- 🤖 Gera resumos inteligentes usando Google Gemini AI
- 📧 Envia emails diários formatados em HTML
- 📱 Cria conteúdo otimizado para LinkedIn

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

### Execução Básica
```powershell
# Processa notícias do último dia
.\run_app.ps1

# Processa últimos 3 dias
.\run_app.ps1 --days 3

# Modo debug (sem enviar email)
.\run_app.ps1 --dry-run
```

### Opções da Linha de Comando
- `--days N`: Número de dias para processar (padrão: 1)
- `--dry-run`: Executa sem enviar emails
- `--verbose`: Logs mais detalhados

## 🏗️ Arquitetura do Sistema

```
product_reader/
├── 📁 src/                          # Código fonte principal
│   ├── 🏠 main.py                   # Ponto de entrada da aplicação
│   ├── 📁 agents/                   # Agentes de processamento
│   │   ├── rss_reader.py           # Leitor de feeds RSS
│   │   └── summarizer.py           # Gerador de resumos com IA
│   ├── 📁 config/                   # Configurações do sistema
│   │   ├── settings.py             # Configurações centralizadas
│   │   ├── feeds.txt              # URLs dos feeds RSS
│   │   └── recipients.txt         # Lista de destinatários
│   ├── 📁 models/                   # Modelos de dados
│   │   └── news_item.py           # Estrutura de itens de notícia
│   ├── 📁 templates/                # Templates e prompts
│   │   ├── email_template.html     # Template HTML do email
│   │   └── prompts.py             # Prompts para IA
│   └── 📁 utils/                    # Utilitários
│       ├── email_sender.py        # Envio de emails
│       ├── gemini_client.py       # Cliente da API Gemini
│       ├── logger.py              # Sistema de logging
│       └── date_helpers.py        # Manipulação de datas
├── 📁 tests/                        # Testes automatizados
├── 📄 requirements.txt              # Dependências do projeto
├── 📄 .env                          # Variáveis de ambiente
└── 📄 run_app.ps1                   # Script de execução

```

## 🔧 Desenvolvimento

### Executando Testes
```powershell
# Instalar dependências de desenvolvimento
pip install pytest pytest-cov

# Executar todos os testes
pytest tests/

# Executar com coverage
pytest --cov=src tests/
```

### Padrões de Código
- **Documentação**: Todos os módulos e funções documentados em português
- **Type Hints**: Tipagem explícita em Python
- **Logging**: Sistema padronizado de logs com emojis
- **Error Handling**: Tratamento robusto de exceções

## 🐛 Solução de Problemas

### Erro de Envio de Email
```
✗ Falha no envio do email: Authentication failed
```
**Solução**: 
- Verifique as credenciais SMTP no arquivo `.env`
- Para Gmail, use senha de aplicativo específica
- Verifique se 2FA está habilitado

### Erro de API Gemini
```
✗ Quota exceeded for Gemini API
```
**Solução**: 
- Verifique sua cota na Google Cloud Console
- O sistema automaticamente tenta modelos gratuitos como fallback

### Feeds RSS Inacessíveis
```
✗ Failed to fetch feed: Connection timeout
```
**Solução**: 
- Verifique conexão com internet
- Confirme se URLs dos feeds estão corretas em `feeds.txt`

## 📈 Monitoramento

O sistema gera logs detalhados que incluem:
- ✅ Status de processamento de cada feed
- 📊 Estatísticas de artigos processados
- ⏱️ Tempo de execução de cada etapa
- 🚨 Alertas de erro com contexto

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m "Adiciona nova funcionalidade"`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Diretrizes de Contribuição
- Mantenha documentação em português
- Adicione testes para novas funcionalidades
- Siga padrões de código existentes
- Atualize README se necessário

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para detalhes.

---

**Desenvolvido com ❤️ para automatizar o consumo inteligente de notícias**