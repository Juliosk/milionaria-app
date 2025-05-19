import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Análise da Mega-Sena", layout="wide")

@st.cache_data
def carregar_dados():
    url = "https://loteriascaixa-api.herokuapp.com/api/megasena"
    response = requests.get(url)
    data = response.json()
    
    # Exibe toda a estrutura para debug
    st.write("Dados do concurso:", data)
    
    return data

# Carregar dados da API
dados = carregar_dados()

# Título e dados principais
st.title("📊 Análise do Último Concurso da Mega-Sena")
st.markdown(f"**Concurso nº {dados['concurso']}** realizado em **{dados['data']}**")
st.markdown(f"📍 Local: {dados['local']}")
st.markdown(f"🎯 Dezenas Sorteadas: `{', '.join(dados['dezenas'])}`")

# Tabela de premiações
st.subheader("🏆 Premiações")
df_premios = pd.DataFrame(dados["premiacoes"])
df_premios["valorPremio"] = df_premios["valorPremio"].apply(lambda x: f\"R$ {x:,.2f}\".replace(\",\", \"X\").replace(\".\", \",\").replace(\"X\", \".\"))
st.dataframe(df_premios.rename(columns={
    \"descricao\": \"Acertos\",
    \"ganhadores\": \"Ganhadores\",
    \"valorPremio\": \"Prêmio\"
}))

# Info extra
st.markdown(f\"💰 Valor Arrecadado: R$ {dados['valorArrecadado']:,.2f}\".replace(\",\", \"X\").replace(\".\", \",\").replace(\"X\", \".\"))
st.markdown(f\"📈 Estimativa Próximo Concurso (nº {dados['proximoConcurso']} em {dados['dataProximoConcurso']}): R$ {dados['valorEstimadoProximoConcurso']:,.2f}\".replace(\",\", \"X\").replace(\".\", \",\").replace(\"X\", \".\"))

