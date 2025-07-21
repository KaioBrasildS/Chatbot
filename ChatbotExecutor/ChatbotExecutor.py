# Importação das bibliotecas para acessar os codigos python para o chatbot
import sys
import os

# Ajuste dos caminhos para importar modulos locais
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importação das bibliotecas para ajuste de texto
# import ollama
import io
import contextlib
import re
# import textwrap

# Importação das biliotecas para visualização de dados e previsão ARIMA
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA

# Importação do gerador de chat e do processador de dados
from .chatbot_llm import chat_generater
from ServicesDataProcessor.ServicesDataProcessor  import ServicesDataProcessor

# Inicialização do processador de dados com o arquivo CSV do café
ServDatProc = ServicesDataProcessor("data/gold/cafe.csv")





def extrair_codigo(texto):
    # Tenta primeiro extrair o bloco de código bem formatado com fechamento
    match = re.search(r"```python\s*(.*?)```", texto, flags=re.DOTALL)
    if match:
        return match.group(1).strip()

    # Se não encontrar com fechamento, tenta até o começo da explicação
    match = re.search(r"```python\s*(.*?)(?:\n[A-ZÁÀÉÊÍÓÚÇa-záàéêíóúç ]+?:|A explicação é|Explicação:)", texto, flags=re.DOTALL)
    if match:
        return match.group(1).strip()

    print("Código Python não encontrado no texto.")
    return None
# Classe principal do executor do chatbot
class ChatbotExecutor:
    # Definição do construtor da classe
    def __init__(self, ServDatProc, usar_groq=True):
        """
        Inicializa o executor do chatbot com o os dados que serão usados,
        a periodicidade padrão e se será usado Groq ou Ollama.
        Parametros:
        ServDatProc: Instância do processador de dados que contém o DataFrame original.
        usar_groq: Booleano que define se o modelo Groq será usado (True) ou Ollama (False).
        """
        self.ServicesDataProcessor = ServDatProc
        self.periodicidade = 'D'  # Default diária
        self.usar_groq = usar_groq  # Define se usa Groq ou Ollama

    # Definição do método para prever os dados usando ARIMA
    def prever_arima(self, serie, passos=5):
        """
        Cria um modelo ARIMA(5,1,0) simples para prever os próximos valores da série temporal.
        Parâmetros:
        serie: Série temporal a ser prevista.
        passos: Número de passos à frente para previsão (default é 5).
        Retorna:
        previsões dos próximos valores da série temporal.
        """
       # Faz a previsão usando ARIMA(5,1,0) se possivel.
        try:
            modelo = ARIMA(serie, order=(5,1,0))
            modelo_fit = modelo.fit()
            previsoes = modelo_fit.forecast(steps=passos)
            return previsoes
        # Caso ocorra algum erro, retorna uma mensagem.
        except Exception as e:
            return f"Erro ao executar previsão ARIMA: {e}"

    def responder(self, pergunta):
        """
        Processa a pergunta e gerá uma resposta baseando se nos dados do café,
        usando o modelo Groq ou Ollama.
        Parâmetros:
        pergunta: String com a pergunta do usuário sobre os dados do café.
        Retorna:
        Resposta gerada pelo modelo, que pode incluir visualizações ou código Python.
        """
        # Verifica se a pergunta contém uma solicitação de periodicidade
        nova_periodicidade = self.ServicesDataProcessor.extrair_periodicidade(
            pergunta
        )
        # Se uma nova periodicidade for encontrada, atualiza a periodicidade do executor
        if nova_periodicidade:
            self.periodicidade = nova_periodicidade
            # Confirma a alteração da periodicidade
            return f"Periodicidade alterada para: {self.periodicidade}"
        # Se a periodicidade não foi definida, solicita ao usuário que informe uma
        if not self.periodicidade:
            return ("Por favor, informe a periodicidade da série"
            "(ex: diária, semanal, mensal)."
            )
        # Agrupa os dados originais pela periodicidade definida
        df = self.ServicesDataProcessor.agrupar_periodicidade(
            self.ServicesDataProcessor.df_original, self.periodicidade
        )
        # Verifica se a pergunta contém uma solicitação de previsão
        if re.search(
            r'\b(previsão|prever|forecast|fazer previsão)\b',
              pergunta.lower()
              ):
            # Define a serie para a previsão usando Data como índice
            serie = df.set_index("Data")["À vista R$"]
            # Faz as previsões usando ARIMA
            previsoes = self.prever_arima(serie)
            # Cria a figura para mostrar o gráfico das previsões
            fig, ax = plt.subplots()
            # Plota a série original
            serie.plot(ax=ax, label="Preço do café (real)", color="blue")
            # Plota as previsões
            previsoes.plot(ax=ax, label="Previsão", color="red")
            plt.title("Previsão do preço do café")
            plt.legend()
            st.pyplot(fig)
            return "Previsão gerada com sucesso. Veja o gráfico acima."
        # Se a pergunta não for sobre previsão, gera uma resposta com o modelo
        else:
            # Se o modelo Groq for usado, chama a função de geração de chat
            if getattr(self, "usar_groq", False):
                # Gera a resposta usando o modelo Groq(codigos e explicação)
                resposta_modelo = chat_generater(df.columns.tolist(), pergunta)
            # Se o modelo Groq não for usado, chama a função de geração de chat do Ollama(Indisponível)
            else:
                aviso = (
                    "O modelo local está indisponível no momento."
                    " Ative o uso do modelo Groq para continuar."
                )
                st.warning(aviso)
                return aviso
        print("Resposta do modelo recebida:\n", resposta_modelo)

        # Extrai o código e a explicação separadamente
        codigo = extrair_codigo(resposta_modelo)
        # Remove o bloco de código do texto original
        explicacao_bruta = re.sub(r"```(?:python)?\s*.*?```", "", resposta_modelo, flags=re.DOTALL).strip()
        print("Código extraído:")
        print(codigo)

        try:
            # Definição das variáveis locais para o exec
            local_vars = {"df": df, "plt": plt, "sns": sns}
            # captura o print() do código gerado
            buf = io.StringIO()
            # Executa o código Python gerado pelo modelo utilizando as variáveis locais
            with contextlib.redirect_stdout(buf):
                exec(codigo, local_vars, local_vars)
            # Recupera aquilo que foi printado pelo código executado   
            output = buf.getvalue()

            # Força a exibição do gráfico se plt ou sns forem usados
            fig = plt.gcf()  # Pega a figura atual sempre, antes de limpar
            if fig.axes:
                st.pyplot(fig)
                plt.clf()  # Limpa a figura para evitar sobreposição futura

            # Exibe texto do print(), se houver
            if output.strip():
                st.code(output)

            # Exibe explicação separadamente, só se existir
            if explicacao_bruta:
                st.markdown("**Explicação:**")
                st.markdown(explicacao_bruta)

            return "Código executado com sucesso. Veja o gráfico acima."
        # Exceção caso ocorra algum erro na execução do código
        except Exception as e:
            return f"Ocorreu um erro ao executar o código gerado: {e}"