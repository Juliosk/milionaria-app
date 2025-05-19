import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import combinations
import random
import json
import requests
from datetime import datetime
import time

# Configuração da página com tema escuro e layout amplo
st.set_page_config(
    page_title="Análise Futurística de Loterias",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para uma aparência futurística
st.markdown("""
<style>
    /* Tema escuro futurístico */
    .main {
        background-color: #0c0e14;
        color: #e0e0e0;
    }
    .stApp {
        background: linear-gradient(to bottom, #0c0e14 0%, #151a30 100%);
    }
    h1, h2, h3 {
        color: #00ccff !important;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(0, 204, 255, 0.5);
    }
    .stButton>button {
        color: white;
        background-color: #0066cc;
        border: 1px solid #00ccff;
        border-radius: 20px;
        box-shadow: 0 0 10px rgba(0, 204, 255, 0.5);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0099ff;
        box-shadow: 0 0 15px rgba(0, 204, 255, 0.8);
        transform: translateY(-2px);
    }
    div.block-container {
        padding-top: 1rem;
    }
    /* Destaque para números */
    .number-highlight {
        font-weight: bold;
        color: #00ffcc;
        background-color: #001a33;
        padding: 6px 12px;
        border-radius: 50%;
        margin: 2px;
        display: inline-block;
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.5);
    }
    /* Animação de carregamento */
    .loading {
        display: flex;
        justify-content: center;
    }
    .loading::after {
        content: '';
        width: 50px;
        height: 50px;
        border: 10px solid #00ccff;
        border-top-color: transparent;
        border-radius: 50%;
        animation: loading-spinner 1s linear infinite;
    }
    @keyframes loading-spinner {
        to {
            transform: rotate(360deg);
        }
    }
    /* Cards futurísticos */
    .card {
        background: linear-gradient(145deg, #121928, #0d131e);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 204, 255, 0.1);
        margin-bottom: 20px;
        border: 1px solid rgba(0, 204, 255, 0.1);
        backdrop-filter: blur(5px);
    }
    /* Tabelas estilizadas */
    .dataframe {
        background-color: #121928 !important;
        color: #e0e0e0 !important;
        border: 1px solid #2a3a5a !important;
    }
    .dataframe th {
        background-color: #1a2740 !important;
        color: #00ccff !important;
    }
    .dataframe td {
        color: #e0e0e0 !important;
    }
    /* Menu lateral */
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #101420 0%, #1a1f35 100%);
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Lista de loterias disponíveis
LOTERIAS = [
    "megasena",
    "maismilionaria",
    "lotofacil",
    "quina",
    "lotomania",
    "timemania",
    "duplasena",
    "federal",
    "diadesorte",
    "supersete"
]

# Função para exibir mensagem de carregamento
def loading_message(message="Carregando dados..."):
    with st.spinner(message):
        container = st.empty()
        container.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;margin:50px 0;">
            <div style="font-family:'Orbitron',sans-serif;color:#00ccff;margin-bottom:20px;">{message}</div>
            <div class="loading"></div>
        </div>
        """, unsafe_allow_html=True)


        
        return container



# Função para carregar dados da API com cache
@st.cache_data(ttl=3600)
def carregar_dados(loteria="maismilionaria"):
    loading = loading_message(f"Buscando dados da {loteria.upper()}...")
    
    url = f"https://loteriascaixa-api.herokuapp.com/api/{loteria}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve erros na requisição
        data = response.json()
        
        if isinstance(data, list):
            df = pd.json_normalize(data)
            
            # Verifica e trata colunas específicas para cada tipo de loteria
            if loteria == "maismilionaria":
                colunas = ["concurso", "dezenas", "trevos","data"]
                df = df[colunas]
                df = df.dropna()
                df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
                df["trevos"] = df["trevos"].apply(lambda x: list(map(int, x)))
            
            elif loteria in ["megasena", "lotofacil", "quina", "lotomania"]:
                colunas = ["concurso", "data", "dezenas"]
                if all(col in df.columns for col in colunas):
                    df = df[colunas]
                    df = df.dropna(subset=["concurso", "dezenas"])
                    df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
                    # Converter data para datetime
                    df["data"] = pd.to_datetime(df["data"], errors='coerce')
            
            elif loteria == "timemania":
                colunas = ["concurso", "data", "dezenas", "time"]
                if all(col in df.columns for col in colunas):
                    df = df[colunas]
                    df = df.dropna(subset=["concurso", "dezenas"])
                    df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
                    df["data"] = pd.to_datetime(df["data"], errors='coerce')
            
            elif loteria == "duplasena":
                colunas = ["concurso", "data", "dezenas", "dezenas_2"]
                if all(col in df.columns for col in colunas):
                    df = df[colunas]
                    df = df.dropna(subset=["concurso", "dezenas"])
                    df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
                    df["dezenas_2"] = df["dezenas_2"].apply(lambda x: list(map(int, x)))
                    df["data"] = pd.to_datetime(df["data"], errors='coerce')
            
            elif loteria == "federal":
                colunas = ["concurso", "data", "premios"]
                if all(col in df.columns for col in colunas):
                    df = df[colunas]
                    df = df.dropna(subset=["concurso", "premios"])
                    df["data"] = pd.to_datetime(df["data"], errors='coerce')
            
            elif loteria == "diadesorte":
                colunas = ["concurso", "data", "dezenas", "mes"]
                if all(col in df.columns for col in colunas):
                    df = df[colunas]
                    df = df.dropna(subset=["concurso", "dezenas"])
                    df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
                    df["data"] = pd.to_datetime(df["data"], errors='coerce')
            
            elif loteria == "supersete":
                colunas = ["concurso", "data", "dezenas"]
                if all(col in df.columns for col in colunas):
                    df = df[colunas]
                    df = df.dropna(subset=["concurso", "dezenas"])
                    df["dezenas"] = df["dezenas"].apply(lambda x: list(map(int, x)))
                    df["data"] = pd.to_datetime(df["data"], errors='coerce')
            
            loading.empty()
            return df
        else:
            loading.error(f"Erro: Estrutura inesperada na resposta da API para {loteria}.")
            return pd.DataFrame()
            
    except requests.exceptions.RequestException as e:
        loading.error(f"Erro ao conectar com a API para {loteria}: {str(e)}")
        return pd.DataFrame()
    except ValueError as e:
        loading.error(f"Erro ao processar os dados de {loteria}: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        loading.error(f"Erro inesperado ao carregar dados de {loteria}: {str(e)}")
        return pd.DataFrame()

# Função para criar gráfico interativo de frequência
def criar_grafico_frequencia(freq_series, titulo, color_scale, height=400):
    fig = px.bar(
        x=freq_series.index.astype(str),
        y=freq_series.values,
        labels={'x': 'Número', 'y': 'Frequência'},
        title=titulo,
        color=freq_series.values,
        color_continuous_scale=color_scale,
        height=height
    )
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font={"family": "Orbitron", "size": 24, "color": "#00ccff"},
        font={"family": "Arial", "size": 14, "color": "#e0e0e0"},
        title_x=0.5,
        xaxis_title_font={"size": 16, "color": "#00ccff"},
        yaxis_title_font={"size": 16, "color": "#00ccff"},
        margin=dict(l=40, r=40, t=70, b=40),
        hovermode="closest"
    )
    
    # Adiciona efeito de brilho nas barras
    fig.update_traces(
        marker_line_color="#00ffcc",
        marker_line_width=1.5,
        opacity=0.9
    )
    
    # Adiciona grade horizontal
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255, 255, 255, 0.1)"
    )
    
    return fig

# Função para criar o gráfico de calor de frequência por posição
def criar_mapa_calor(df, coluna_dezenas, titulo, max_num, height=500):
    # Criar matriz para armazenar frequências por posição
    num_posicoes = len(df[coluna_dezenas].iloc[0])
    matriz_freq = np.zeros((max_num + 1, num_posicoes))
    
    # Calcular frequências
    for _, row in df.iterrows():
        for pos, num in enumerate(row[coluna_dezenas]):
            matriz_freq[num, pos] += 1
    
    # Remover linha de índice 0 (não existe número 0 em loterias)
    matriz_freq = matriz_freq[1:, :]
    
    # Criar figura com mapa de calor
    fig = go.Figure(data=go.Heatmap(
        z=matriz_freq,
        x=[f"Posição {i+1}" for i in range(num_posicoes)],
        y=list(range(1, max_num + 1)),
        colorscale="Viridis",
        showscale=True,
        hovertemplate="Número: %{y}<br>%{x}<br>Frequência: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        title=titulo,
        height=height,
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font={"family": "Orbitron", "size": 24, "color": "#00ccff"},
        font={"family": "Arial", "size": 14, "color": "#e0e0e0"},
        title_x=0.5,
        xaxis_title="Posição do Sorteio",
        yaxis_title="Número",
        xaxis_title_font={"size": 16, "color": "#00ccff"},
        yaxis_title_font={"size": 16, "color": "#00ccff"},
        margin=dict(l=40, r=40, t=70, b=40)
    )
    
    return fig

# Função para exibir números em formato de bolinha
def exibir_numeros(numeros, classe="number-highlight"):
    html = '<div style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin:10px 0;">'
    for num in sorted(numeros):
        html += f'<span class="{classe}">{num}</span>'
    html += '</div>'
    return html

# Função para gerar combinações inteligentes
def gerar_combinacoes_inteligentes(df, coluna_dezenas, loteria, num_combinacoes=5):
    # Extrair números únicos do dataframe
    numeros = df[coluna_dezenas].explode()
    freq_numeros = numeros.value_counts().sort_values(ascending=False)
    
    # Definir parâmetros específicos por loteria
    params = {
        "maismilionaria": {"qtd_nums": 6, "max_num": 50, "tem_trevos": True, "qtd_trevos": 2, "max_trevo": 6},
        "megasena": {"qtd_nums": 6, "max_num": 60, "tem_trevos": False},
        "lotofacil": {"qtd_nums": 15, "max_num": 25, "tem_trevos": False},
        "quina": {"qtd_nums": 5, "max_num": 80, "tem_trevos": False},
        "lotomania": {"qtd_nums": 20, "max_num": 100, "tem_trevos": False},
        "timemania": {"qtd_nums": 7, "max_num": 80, "tem_trevos": False},
        "duplasena": {"qtd_nums": 6, "max_num": 50, "tem_trevos": False},
        "federal": {"qtd_nums": 0, "max_num": 0, "tem_trevos": False},  # Federal não tem dezenas
        "diadesorte": {"qtd_nums": 7, "max_num": 31, "tem_trevos": True, "qtd_trevos": 1, "max_trevo": 12},
        "supersete": {"qtd_nums": 7, "max_num": 10, "tem_trevos": False}
    }
    
    if loteria not in params:
        return []
    
    qtd_nums = params[loteria]["qtd_nums"]
    if qtd_nums == 0:  # Para loterias como Federal que não têm dezenas
        return []
    
    # Estratégias para geração inteligente de combinações
    combinacoes = []
    
    # Estratégia 1: Top números mais frequentes
    top_nums = freq_numeros.head(int(qtd_nums * 2.5)).index.tolist()
    
    # Estratégia 2: Mistura de frequentes e menos frequentes
    mid_freq = freq_numeros.iloc[len(freq_numeros)//3:2*len(freq_numeros)//3].index.tolist()
    
    # Estratégia 3: Números que não saem há mais tempo
    recentes = df.sort_values('concurso', ascending=False).head(10)
    nums_recentes = set()
    for _, row in recentes.iterrows():
        nums_recentes.update(row[coluna_dezenas])
    nums_atrasados = [n for n in range(1, params[loteria]["max_num"] + 1) if n not in nums_recentes]
    
    # Gerar combinações com diferentes estratégias
    for _ in range(num_combinacoes):
        estrategia = random.randint(1, 4)
        
        if estrategia == 1:  # Mais frequentes
            pool = top_nums.copy()
            random.shuffle(pool)
            comb = sorted(pool[:qtd_nums])
        
        elif estrategia == 2:  # Mistura equilibrada
            n_freq = qtd_nums // 2
            n_mid = qtd_nums - n_freq
            
            pool_freq = top_nums.copy()
            pool_mid = mid_freq.copy()
            
            random.shuffle(pool_freq)
            random.shuffle(pool_mid)
            
            comb = sorted(pool_freq[:n_freq] + pool_mid[:n_mid])
        
        elif estrategia == 3:  # Números atrasados
            n_atr = min(qtd_nums // 2, len(nums_atrasados))
            n_freq = qtd_nums - n_atr
            
            pool_atr = nums_atrasados.copy()
            pool_freq = top_nums.copy()
            
            random.shuffle(pool_atr)
            random.shuffle(pool_freq)
            
            comb = sorted(pool_atr[:n_atr] + pool_freq[:n_freq])
        
        else:  # Completamente aleatória com números válidos
            comb = sorted(random.sample(range(1, params[loteria]["max_num"] + 1), qtd_nums))
        
        combinacoes.append(comb)
    
    # Para loterias com trevos/meses adicionais
    if params[loteria]["tem_trevos"]:
        trevos_combinacoes = []
        
        if loteria == "maismilionaria":
            trevos = df["trevos"].explode()
            freq_trevos = trevos.value_counts().sort_values(ascending=False)
            
            for _ in range(num_combinacoes):
                trevos_list = freq_trevos.head(params[loteria]["max_trevo"]).index.tolist()
                random.shuffle(trevos_list)
                trevos_combinacoes.append(sorted(trevos_list[:params[loteria]["qtd_trevos"]]))
        
        elif loteria == "diadesorte":
            meses = df["mes"].value_counts().sort_values(ascending=False)
            
            for _ in range(num_combinacoes):
                # Para DiadeSorte, apenas um mês é sorteado
                mes_idx = random.randint(1, 12)  # Meses de 1 a 12
                trevos_combinacoes.append([mes_idx])
        
        return combinacoes, trevos_combinacoes
    
    return combinacoes

# Layout principal da aplicação
def main():
    # Barra lateral
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;margin-bottom:30px;">
            <h1 style="font-family:'Orbitron',sans-serif;color:#00ccff;text-shadow:0 0 10px rgba(0,204,255,0.5);">
                LOTERIAS PRO
            </h1>
            <p style="color:#00ffcc;margin-top:-15px;">Análise Futurística</p>
        </div>
        """, unsafe_allow_html=True)
        
        loteria_selecionada = st.selectbox(
            "Selecione a Loteria",
            options=LOTERIAS,
            format_func=lambda x: x.upper(),
            index=0
        )
        
        st.markdown("""
        <div style="padding:10px;background:linear-gradient(145deg,#121928,#0d131e);border-radius:10px;margin-top:20px;">
            <h3 style="color:#00ffcc;font-size:18px;font-family:'Orbitron',sans-serif;">Informações</h3>
            <ul style="color:#e0e0e0;padding-left:20px;">
                <li>Dados atualizados via API</li>
                <li>Análises estatísticas avançadas</li>
                <li>Algoritmos preditivos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top:30px;text-align:center;padding:15px 0;border-top:1px solid rgba(0,204,255,0.2);">
            <p style="color:#999;font-size:12px;">
                VERSÃO 2025.1 | ANALYTICS ENGINE
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Título principal
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;margin-bottom:30px;">
        <div style="font-size:48px;margin-right:15px;color:#00ffcc;">🎯</div>
        <h1>ANÁLISE DE LOTERIAS</h1>
    </div>
    <p style="text-align:center;color:#00ccff;margin-top:-20px;font-size:18px;">
        Estatísticas avançadas e geração inteligente de combinações
    </p>
    """, unsafe_allow_html=True)

    # Carregamento de dados
    df = carregar_dados(loteria_selecionada)
    
    if df.empty:
        st.error(f"Não foi possível carregar dados para {loteria_selecionada.upper()}. Tente novamente mais tarde ou selecione outra loteria.")
        return

    # Exibição do último concurso
    ultimo_concurso = df.sort_values("concurso", ascending=False).iloc[0]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2>📊 Último Concurso</h2>
        """, unsafe_allow_html=True)
        
        if "data" in df.columns:
            #data_formatada = ultimo_concurso["data"].strftime("%d/%m/%Y") if pd.notna(ultimo_concurso["data"]) else "Data não disponível"
            from datetime import datetime

data_bruta = ultimo_concurso.get("data")
try:
    data_formatada = datetime.strptime(data_bruta, "%d/%m/%Y").strftime("%d/%m/%Y") if pd.notna(data_bruta) else "Data não disponível"
except Exception:
    data_formatada = "Data inválida"

            
            
            #st.markdown(f"<p style='color:#00ffcc;'>Concurso <b>{int(ultimo_concurso['concurso'])}</b> | {data_formatada}</p>", unsafe_allow_html=True)
        #else:
         #   st.markdown(f"<p style='color:#00ffcc;'>Concurso <b>{int(ultimo_concurso['concurso'])}</b></p>", unsafe_allow_html=True)
        
        if "dezenas" in df.columns:
            st.markdown("<h3>Números Sorteados</h3>", unsafe_allow_html=True)
            st.markdown(exibir_numeros(ultimo_concurso["dezenas"]), unsafe_allow_html=True)
        
        if loteria_selecionada == "maismilionaria" and "trevos" in df.columns:
            st.markdown("<h3>Trevos</h3>", unsafe_allow_html=True)
            st.markdown(exibir_numeros(ultimo_concurso["trevos"], "number-highlight"), unsafe_allow_html=True)
        
        if loteria_selecionada == "duplasena" and "dezenas_2" in df.columns:
            st.markdown("<h3>Segundo Sorteio</h3>", unsafe_allow_html=True)
            st.markdown(exibir_numeros(ultimo_concurso["dezenas_2"]), unsafe_allow_html=True)
        
        if loteria_selecionada == "timemania" and "time" in df.columns:
            st.markdown(f"<h3>Time do Coração</h3><p style='color:#00ffcc;font-size:18px;text-align:center;'>{ultimo_concurso['time']}</p>", unsafe_allow_html=True)
        
        if loteria_selecionada == "diadesorte" and "mes" in df.columns:
            st.markdown(f"<h3>Mês da Sorte</h3><p style='color:#00ffcc;font-size:18px;text-align:center;'>{ultimo_concurso['mes']}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h2>⚡ Status</h2>", unsafe_allow_html=True)
        
        num_concursos = len(df)
        
        # Métricas específicas por tipo de loteria
        if "dezenas" in df.columns:
            numeros = df["dezenas"].explode()
            num_mais_comum = numeros.value_counts().idxmax()
            st.markdown(f"""
            <p>Total de concursos: <span style="color:#00ffcc;font-weight:bold;">{num_concursos}</span></p>
            <p>Número mais frequente: <span style="color:#00ffcc;font-weight:bold;">{num_mais_comum}</span></p>
            
            
            """, unsafe_allow_html=True)
        # Métricas adicionais específicas
        if loteria_selecionada == "maismilionaria" and "trevos" in df.columns:
            trevos = df["trevos"].explode()
            trevo_mais_comum = trevos.value_counts().idxmax()
            st.markdown(f"<p>Trevo mais frequente: <span style='color:#00ffcc;font-weight:bold;'>{trevo_mais_comum}</span></p>", unsafe_allow_html=True)
        
        if loteria_selecionada == "timemania" and "time" in df.columns:
            time_mais_comum = df["time"].value_counts().idxmax()
            st.markdown(f"<p>Time mais sorteado: <span style='color:#00ffcc;font-weight:bold;'>{time_mais_comum}</span></p>", unsafe_allow_html=True)
        
        if loteria_selecionada == "diadesorte" and "mes" in df.columns:
            mes_mais_comum = df["mes"].value_counts().idxmax()
            st.markdown(f"<p>Mês mais sorteado: <span style='color:#00ffcc;font-weight:bold;'>{mes_mais_comum}</span></p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Análises estatísticas avançadas
    st.markdown("<h2 style='margin-top:40px;'>📈 Análises Estatísticas Avançadas</h2>", unsafe_allow_html=True)
    
    # Verifica se a loteria tem dezenas para análise
    if "dezenas" in df.columns:
        numeros = df["dezenas"].explode()
        freq_numeros = numeros.value_counts().sort_index()
        
        tabs = st.tabs(["Frequência dos Números", "Mapa de Calor", "Análise Temporal"])
        
        with tabs[0]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            # Gráfico de frequência interativo
            fig_freq = criar_grafico_frequencia(freq_numeros, "Frequência dos Números Sorteados", "Viridis")
            st.plotly_chart(fig_freq, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tabs[1]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            # Definir o número máximo para cada loteria
            max_nums = {
                "maismilionaria": 50, "megasena": 60, "lotofacil": 25, 
                "quina": 80, "lotomania": 100, "timemania": 80, 
                "duplasena": 50, "diadesorte": 31, "supersete": 10
            }
            
            max_num = max_nums.get(loteria_selecionada, 60)
            
            # Mapa de calor de números por posição
            fig_heatmap = criar_mapa_calor(df, "dezenas", "Frequência por Posição do Sorteio", max_num)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tabs[2]:
            # Verificar se temos coluna de data para análise temporal
            if "data" in df.columns and df["data"].notna().any():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                
                # Preparar dados temporais
                df_temporal = df.copy()
                df_temporal["ano_mes"] = df_temporal["data"].dt.strftime("%Y-%m")
                
                # Agrupamento por mês
                contagem_mensal = df_temporal.groupby("ano_mes").size().reset_index(name="contagem")
                contagem_mensal.columns = ["Mês", "Quantidade"]
                
                # Gráfico de tendência
                fig_temporal = px.line(
                    contagem_mensal.tail(24),  # Últimos 24 meses
                    x="Mês",
                    y="Quantidade",
                    markers=True,
                    title="Tendência de Concursos por Mês",
                    line_shape="spline"
                )
                
                fig_temporal.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    title_font={"family": "Orbitron", "size": 24, "color": "#00ccff"},
                    font={"family": "Arial", "size": 14, "color": "#e0e0e0"},
                    title_x=0.5,
                    xaxis_title="Período",
                    yaxis_title="Quantidade de Concursos",
                    xaxis_title_font={"size": 16, "color": "#00ccff"},
                    yaxis_title_font={"size": 16, "color": "#00ccff"},
                    margin=dict(l=40, r=40, t=70, b=40)
                )
                
                # Adiciona efeito de brilho na linha
                fig_temporal.update_traces(
                    line=dict(width=3, color="#00ffcc"),
                    marker=dict(size=8, line=dict(width=2, color="#00ffcc"))
                )
                
                st.plotly_chart(fig_temporal, use_container_width=True)
                
                # Análise de sazonalidade (dias da semana)
                if len(df_temporal) > 30:  # Só faz sentido com dados suficientes
                    st.markdown("<h3>Sazonalidade por Dia da Semana</h3>", unsafe_allow_html=True)
                    
                    df_temporal["dia_semana"] = df_temporal["data"].dt.day_name()
                    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    nomes_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                    
                    # Mapeamento de inglês para português
                    df_temporal["dia_semana"] = df_temporal["dia_semana"].map(dict(zip(ordem_dias, nomes_dias)))
                    
                    # Contagem por dia da semana
                    contagem_dias = df_temporal["dia_semana"].value_counts().reindex(nomes_dias).fillna(0)
                    
                    # Gráfico de barras para dias da semana
                    fig_dias = px.bar(
                        x=contagem_dias.index,
                        y=contagem_dias.values,
                        labels={"x": "Dia da Semana", "y": "Quantidade de Sorteios"},
                        title="Distribuição de Sorteios por Dia da Semana",
                        color=contagem_dias.values,
                        color_continuous_scale="Viridis"
                    )
                    
                    fig_dias.update_layout(
                        template="plotly_dark",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        title_font={"family": "Orbitron", "size": 20, "color": "#00ccff"},
                        font={"family": "Arial", "size": 14, "color": "#e0e0e0"},
                        title_x=0.5,
                        xaxis_title_font={"size": 16, "color": "#00ccff"},
                        yaxis_title_font={"size": 16, "color": "#00ccff"},
                        margin=dict(l=40, r=40, t=70, b=40)
                    )
                    
                    st.plotly_chart(fig_dias, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Dados temporais não disponíveis para esta loteria.")
    
    # Análise específica para +Milionária e outras loterias com elementos adicionais
    if loteria_selecionada == "maismilionaria" and "trevos" in df.columns:
        st.markdown("<h2 style='margin-top:40px;'>🍀 Análise dos Trevos</h2>", unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        trevos = df["trevos"].explode()
        freq_trevos = trevos.value_counts().sort_index()
        
        # Gráfico de frequência dos trevos
        fig_trevos = criar_grafico_frequencia(freq_trevos, "Frequência dos Trevos da Sorte", "Turbo", height=300)
        st.plotly_chart(fig_trevos, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Análise específica para Timemania
    elif loteria_selecionada == "timemania" and "time" in df.columns:
        st.markdown("<h2 style='margin-top:40px;'>⚽ Times do Coração</h2>", unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # Top 10 times mais sorteados
        top_times = df["time"].value_counts().head(10)
        
        fig_times = px.bar(
            x=top_times.index,
            y=top_times.values,
            labels={"x": "Time", "y": "Frequência"},
            title="Top 10 Times do Coração Mais Sorteados",
            color=top_times.values,
            color_continuous_scale="Viridis"
        )
        
        fig_times.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title_font={"family": "Orbitron", "size": 20, "color": "#00ccff"},
            font={"family": "Arial", "size": 14, "color": "#e0e0e0"},
            title_x=0.5,
            xaxis_title_font={"size": 16, "color": "#00ccff"},
            yaxis_title_font={"size": 16, "color": "#00ccff"},
            margin=dict(l=40, r=40, t=70, b=40),
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_times, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Análise específica para Dia de Sorte
    elif loteria_selecionada == "diadesorte" and "mes" in df.columns:
        st.markdown("<h2 style='margin-top:40px;'>🗓️ Meses da Sorte</h2>", unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # Frequência dos meses
        freq_meses = df["mes"].value_counts().sort_index()
        
        # Mapeamento de número para nome do mês
        meses_nomes = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        
        # Garantir que todos os meses estejam presentes
        todos_meses = pd.Series(index=range(1, 13), data=[0]*12)
        freq_meses = freq_meses.add(todos_meses, fill_value=0)
        
        # Substituir índices numéricos pelos nomes dos meses
        freq_meses.index = [meses_nomes.get(m, m) for m in freq_meses.index]
        
        fig_meses = px.bar(
            x=freq_meses.index,
            y=freq_meses.values,
            labels={"x": "Mês", "y": "Frequência"},
            title="Frequência dos Meses da Sorte",
            color=freq_meses.values,
            color_continuous_scale="Viridis"
        )
        
        fig_meses.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title_font={"family": "Orbitron", "size": 20, "color": "#00ccff"},
            font={"family": "Arial", "size": 14, "color": "#e0e0e0"},
            title_x=0.5,
            xaxis_title_font={"size": 16, "color": "#00ccff"},
            yaxis_title_font={"size": 16, "color": "#00ccff"},
            margin=dict(l=40, r=40, t=70, b=40)
        )
        
        st.plotly_chart(fig_meses, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Previsões e combinações inteligentes
    st.markdown("<h2 style='margin-top:40px;'>🔮 Previsões Inteligentes</h2>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Verificar se a loteria atual suporta geração de combinações
    if loteria_selecionada != "federal" and "dezenas" in df.columns:
        # Gerar combinações inteligentes
        combinacoes_resultado = gerar_combinacoes_inteligentes(df, "dezenas", loteria_selecionada, 5)
        
        # Verifica se o resultado é uma tupla (no caso de loterias com trevos)
        if isinstance(combinacoes_resultado, tuple):
            combinacoes = combinacoes_resultado[0]
            trevos_combinacoes = combinacoes_resultado[1]
            
            # Exibir combinações geradas
            st.markdown("<h3>Combinações Sugeridas</h3>", unsafe_allow_html=True)
            
            for i, (comb, trevos) in enumerate(zip(combinacoes, trevos_combinacoes), 1):
                st.markdown(f"<h4>Combinação {i}</h4>", unsafe_allow_html=True)
                st.markdown(exibir_numeros(comb), unsafe_allow_html=True)
                
                if loteria_selecionada == "maismilionaria":
                    st.markdown("<h5>Trevos</h5>", unsafe_allow_html=True)
                    st.markdown(exibir_numeros(trevos), unsafe_allow_html=True)
                
                elif loteria_selecionada == "diadesorte":
                    mes_nome = {
                        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                    }
                    st.markdown(f"<h5>Mês da Sorte: <span style='color:#00ffcc;'>{mes_nome.get(trevos[0], trevos[0])}</span></h5>", unsafe_allow_html=True)
                
                st.markdown("<hr style='border-color:rgba(0,204,255,0.2);margin:20px 0;'>", unsafe_allow_html=True)
        else:
            combinacoes = combinacoes_resultado
            
            # Exibir combinações geradas
            st.markdown("<h3>Combinações Sugeridas</h3>", unsafe_allow_html=True)
            
            for i, comb in enumerate(combinacoes, 1):
                st.markdown(f"<h4>Combinação {i}</h4>", unsafe_allow_html=True)
                st.markdown(exibir_numeros(comb), unsafe_allow_html=True)
                
                st.markdown("<hr style='border-color:rgba(0,204,255,0.2);margin:20px 0;'>", unsafe_allow_html=True)
    
        # Metodologia de geração
        with st.expander("Metodologia de Geração"):
            st.markdown("""
            <p style="color:#e0e0e0;">
                As combinações são geradas usando um algoritmo avançado que considera:
            </p>
            <ul style="color:#e0e0e0;">
                <li>Frequência histórica dos números</li>
                <li>Padrões de sorteios recentes</li>
                <li>Números que não são sorteados há muito tempo</li>
                <li>Balanceamento entre números quentes e frios</li>
                <li>Distribuição de paridade (números pares e ímpares)</li>
            </ul>
            <p style="color:#e0e0e0;font-style:italic;">
                Nota: As previsões são baseadas apenas em análises estatísticas e não garantem resultados.
            </p>
            """, unsafe_allow_html=True)
    else:
        st.info("Geração de combinações não disponível para esta loteria.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Concursos recentes
    st.markdown("<h2 style='margin-top:40px;'>📜 Histórico de Concursos</h2>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Seleção de número de concursos para exibir
    num_concursos = st.slider("Quantidade de concursos para exibir", 5, 20, 10)
    
    # Preparar colunas para exibição
    colunas_exibir = ["concurso"]
    if "data" in df.columns:
        colunas_exibir.append("data")
    if "dezenas" in df.columns:
        colunas_exibir.append("dezenas")
    if loteria_selecionada == "maismilionaria" and "trevos" in df.columns:
        colunas_exibir.append("trevos")
    if loteria_selecionada == "timemania" and "time" in df.columns:
        colunas_exibir.append("time")
    if loteria_selecionada == "diadesorte" and "mes" in df.columns:
        colunas_exibir.append("mes")
    if loteria_selecionada == "duplasena" and "dezenas_2" in df.columns:
        colunas_exibir.append("dezenas_2")
    
    # Exibir tabela com histórico de concursos
    df_exibir = df[colunas_exibir].sort_values(by="concurso", ascending=False).head(num_concursos).reset_index(drop=True)
    
    # Formatação de data, se disponível
    if "data" in df_exibir.columns:
        df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
    
    st.dataframe(df_exibir, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Rodapé com informações adicionais
    st.markdown("""
    <div style="margin-top:50px;padding:20px;text-align:center;background:linear-gradient(145deg,#121928,#0d131e);border-radius:15px;border:1px solid rgba(0,204,255,0.1);">
        <p style="color:#999;font-size:14px;">
            Dados fornecidos pela API Loterias Caixa | Última atualização: {data_atual}
        </p>
        <p style="color:#666;font-size:12px;margin-top:10px;">
            Análise estatística para fins de entretenimento. Não representa promessa ou garantia de resultados.
        </p>
    </div>
    """.format(data_atual=datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

# Executar a aplicação
if __name__ == "__main__":
    main()
