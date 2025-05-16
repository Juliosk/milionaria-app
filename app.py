import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import random
import json
import requests

st.set_page_config(page_title="Análise +Milionária", layout="wide")

@st.cache_data
def carregar_dados():
    url = "https://loteriascaixa-api.herokuapp.com/api/mais_milionaria"
    response = requests.get(url)
    data = response.json()

    # DEBUG: visualizar a resposta da API
    st.write("Resposta da API:", data)

    if "data" in data:
        df = pd.json_normalize(data["data"])
        df = df[["concurso", "dezenas", "trevos"]]
        df = df.dropna()
        df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
        df["trevos"] = df["trevos"].apply(lambda x: list(map(int, x)))
        return df
    else:
        st.error("Erro: chave 'data' não encontrada na resposta da API.")
        return pd.DataFrame(columns=["concurso", "dezenas", "trevos"])

df = carregar_dados()

st.title("🎲 Análise Interativa da +Milionária")
st.markdown("Analise frequências, padrões e obtenha previsões com base nos concursos mais recentes.")

# Frequência total dos números
numeros = df["dezenas"].explode()
freq_numeros = numeros.value_counts().sort_index()

# Frequência total dos trevos
trevos = df["trevos"].explode()
freq_trevos = trevos.value_counts().sort_index()

# Gráfico de frequência dos números
st.subheader("Frequência dos Números")
fig, ax = plt.subplots(figsize=(14, 4))
sns.barplot(x=freq_numeros.index, y=freq_numeros.values, ax=ax, palette="viridis")
ax.set_title("Números Mais Frequentes")
ax.set_ylabel("Frequência")
st.pyplot(fig)

# Gráfico de frequência dos trevos
st.subheader("Frequência dos Trevos")
fig2, ax2 = plt.subplots(figsize=(8, 3))
sns.barplot(x=freq_trevos.index, y=freq_trevos.values, ax=ax2, palette="pastel")
ax2.set_title("Frequência dos Trevos da Sorte")
st.pyplot(fig2)

# Previsão baseada nos 15 mais frequentes
st.subheader("Previsões com Base em Frequência Histórica")
top15 = freq_numeros.sort_values(ascending=False).head(15).index.tolist()
combinacoes_previstas = random.sample(list(combinations(top15, 6)), 5)

for i, comb in enumerate(combinacoes_previstas, 1):
    st.write(f"**Combinação {i}:**", sorted(comb))

# Concursos recentes
st.subheader("Concursos Recentes")
st.dataframe(df.sort_values(by="concurso", ascending=False).head(10).reset_index(drop=True))
