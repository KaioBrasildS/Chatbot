from groq import Groq
# from ollama import chat as ollama_chat  # Descomente se quiser suporte local

USE_GROQ = True  # Altere para False se quiser usar o Ollama local

from .key import key as api_key  # Importa a chave da API Groq
if USE_GROQ:
    client = Groq(api_key=api_key)  # Inicializa o cliente Groq com a chave da API
else:
    print("Modelo Ollama não está implementado no momento.")
def chat_generater(dataset, comando):
    prompt = f"""
    Você é um assistente Python especializado em séries temporais. O usuário está analisando a coluna 'À vista R$', que representa o preço do café, em um DataFrame chamado 'df', já carregado.

    A coluna 'À vista R$' pode ser mencionada pelo usuário como "preço", "valor" ou "valor do café", mas no código Python use sempre o nome exato da coluna 'À vista R$'.

    Dataset:
        Colunas disponíveis: {dataset}

    Análise desejada:
        {comando}

    Regras obrigatórias de resposta:

    1. Gere apenas o código Python, isolado dentro de um bloco markdown com crases, começando com ```python e terminando com ```. É obrigatório incluir a linha de fechamento com exatamente três crases (```).

    2. Nunca escreva nada antes ou depois do bloco de código. Apenas gere o conteúdo entre ```python (na primeira linha) e ``` (na última linha, sozinha).

    3. Use apenas colunas reais do DataFrame `df`.

    4. Regras obrigatórias para gráficos:
        - Use datas no eixo x caso seja possivel (ex: "mostrar por data", "com datas", "em série", etc).
        - Se o gráfico mostrar dados ordenados (ex: maiores valores, ranking, ordenação por alguma métrica), o eixo x deve usar rótulos legíveis correspondentes aos índices reais do DataFrame (datas ou índices), apresentados na ordem correta.
        - Evite usar índices genéricos como range(10) sem relação com os dados reais.
        - Os rótulos no eixo x devem ser claros, legíveis e sem sobreposição ou distorção.
        - Nunca gere gráficos com eixo x truncado, sobreposto ou distorcido.
        - Sempre finalize com plt.tight_layout() e plt.show().
        

    5. Após o código, escreva uma explicação interpretativa, curta, baseada nos dados reais de `df_plot`. A explicação deve vir apenas depois do fechamento do bloco de código com três crases (```) e não pode estar dentro do bloco.

        - A explicação deve usar os valores reais calculados no código.
        - Nunca use placeholders como [valor máximo], [data], [resultado] — sempre substitua com os números reais.
        - Evite texto quebrado caractere por caractere. Use frases completas, claras e diretas.
        - Evite frases genéricas como “Aqui está o gráfico”.
        - Evite termos técnicos desnecessários como "eixo x", "eixo y", "gráfico de barra". Foque em interpretar os valores reais do gráfico de forma clara e direta.
        - Use linguagem natural, evitando jargões técnicos ou termos complexos.
        - A explicação deve incluir pelo menos um dado numérico real do `df_plot`, como um valor de pico, data ou nome do item com maior valor.
        - A explicação deve usar diretamente os dados reais contidos em `df_plot`, acessando-os via `.iloc`, `.max()`, `.min()`, `.loc` ou similares no próprio código anterior. Nunca invente ou estime os valores.
        - Todos os números usados na explicação devem ser extraídos diretamente do `df_plot` dentro do código Python — por exemplo, com `df_plot['À vista R$'].max()` ou `df_plot.iloc[0]['À vista R$']`. Nunca cite valores manualmente fora do código.


    6. **Não use dados fictícios ou exemplos genéricos** — use apenas os dados reais contidos no DataFrame `df`.

    7. A explicação deve ser clara, natural e útil — evite linguagem robótica, frases repetitivas ou apenas descritivas como "Este é o gráfico...".
    
    8. Sempre que possível, crie primeiro um DataFrame derivado chamado `df_plot`, filtrando ou transformando `df` com base no que foi solicitado na pergunta. O gráfico e a explicação devem se basear exclusivamente nesse `df_plot`.
        - Após criar o DataFrame `df_plot`, use `reset_index(drop=True)` e utilize `.index` ou uma coluna nomeada no eixo x. Nunca use índices herdados do DataFrame original.

    9. Se a pergunta não puder ser respondida com os dados disponíveis, retorne uma mensagem clara informando que a pergunta não pode ser respondida com os dados atuais.

    Sua resposta deve conter apenas um bloco de código entre crases e uma explicação logo abaixo.
    """

    if USE_GROQ:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content

    else:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
