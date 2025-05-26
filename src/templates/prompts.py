# filepath: rss-feed-processor/src/templates/prompts.py

ARTICLE_SUMMARY_PROMPT = """
Passo 1: Resuma a notícia, capturando o ponto principal e oferecendo um detalhe ou implicação importante.
Passo 2: Mantenha o texto curto e conciso, evitando repetições e informações desnecessárias.
Passo 3: Verifique a aderência ao tema e ao tom da notícia.
Passo 4: Verifique se o resumo mantem os mesmos detalhes e informações que o artigo original.
Passo 5: O resumo não deve conter informações adicionais ou opiniões pessoais.
Passo 6: O resumo deve ser escrito em português do brasil, sem erros gramaticais ou ortográficos.
Passo 7: O resumo deve ser claro e fácil de entender, mesmo para quem não leu o artigo original.
Passo 8: O resumo não deve citar as fontes ou autores do artigo original, apenas o conteúdo.
Passo 9: O resumo deve ser escrito em um parágrafo único, sem quebras de linha ou listas.
Passo 10: O resumo não pode trocar nomes próprios ou termos técnicos por sinônimos, a menos que seja absolutamente necessário.

O resumo deve estar no formato 
"Resumo:[resumo]"

Title: {title}
Description: {description}
Source: {source}
"""

LINKEDIN_CONTENT_PROMPT = """
Crie uma publicação no estilo LinkedIn sobre Product Management baseada nos artigos abaixo.
Use estas diretrizes:

1. Estilo e Tom:
   - Linguagem acessível para iniciantes
   - Tom profissional mas conversacional
   - Texto engajador e motivacional
   - Use emojis estrategicamente

2. Estrutura:
   - Gancho inicial forte
   - 3-4 parágrafos curtos
   - Call-to-action ao final
   - Hashtags relevantes (5-7)

3. Elementos de Marketing:
   - Inclua um insight principal
   - Mencione um dado ou estatística impactante
   - Compartilhe uma lição aprendida
   - Faça conexões com o dia a dia

4. Formatação:
   - Use quebras de linha estratégicas
   - Bullet points para pontos principais
   - Limite de caracteres: ~1300
   - Evite jargões técnicos complexos

Artigos do período:
{articles_text}

O texto deve estar no formato:
"Post:[texto formatado para LinkedIn]"
"""
