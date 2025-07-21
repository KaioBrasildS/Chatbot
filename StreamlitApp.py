import streamlit as st
# Modulo que carrega carrega os dados e extrai a periodicidade
from ServicesDataProcessor.ServicesDataProcessor import ServicesDataProcessor

# Modulo responsavel pelas funções do chatbot
from ChatbotExecutor.ChatbotExecutor import ChatbotExecutor

# Inicio da configuração do Streamlit
st.title("Chatbot de Séries Temporais do preço do café com groq e ollama futuramente")
st.markdown("""
    Este chatbot permite que você faça perguntas sobre séries temporais do preço do café,
    utilizando modelos de IA Groq (nuvem) ou Ollama (local) que será adicionado futurtamente.
    Os dados são provenientes do INDICADOR DO CAFÉ ARÁBICA CEPEA/ESALQ encontrados no site 
    [CEPEA](https://www.cepea.org.br/br/consultas-ao-banco-de-dados-do-site.aspx)
""")

# Novo seletor: escolha do modelo
modelo_escolhido = st.radio("Escolha o modelo de IA:", ["Groq (nuvem)", "Ollama (local)"])
usar_groq = modelo_escolhido == "Groq (nuvem)"

# Inicializa o processador de dados com dataframe do café
data_handler = ServicesDataProcessor("data/gold/cafe.csv")

# Carrega os dados do DataFrame para o streamlit
@st.cache_data
def carregar():
    return data_handler.load_data()

try:
    df = carregar()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Passa o parâmetro para o executor
executor = ChatbotExecutor(data_handler, usar_groq=usar_groq)

# Mostrar dataframe original
with st.expander("Visualizar dados originais"):
    st.dataframe(df.head(10))

# Seleciona a periodicidade da série temporal
periodicidade = st.selectbox("Selecione a periodicidade da série:", options=["D", "W", "M"])
executor.periodicidade = periodicidade

# Pergunta do usuário
pergunta = st.text_input("Faça uma pergunta para o chatbot sobre os preços do café ou peça previsão:")

# Resposta do chatbot
if pergunta:
    resposta = executor.responder(pergunta)
    st.markdown("### Resposta:")

    if "indisponível" in resposta.lower():
        st.warning(resposta)
    else:
        st.text(resposta)


