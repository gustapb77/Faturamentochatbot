import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
from faker import Faker
from PIL import Image
import requests
from io import BytesIO
import base64

# ======================================
# CONFIGURAÇÕES INICIAIS COM TRATAMENTO DE ERRO
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Gold Pepper - Dashboard",
    page_icon="🌶️",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão Premium"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
# URLs das imagens (mantendo seus links originais)
LOGO_CARD_URL = "https://i.ibb.co/SXmN2qzD/Logo-Card-Golden-Papper-1.png"
LOGO_ICONE_URL = "https://i.ibb.co/gLGXRBns/18273b-600-x-120-px-2500-x-590-px-400-x-400-px-2.png"

# Imagem de fallback (pixel transparente)
FALLBACK_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# Função com tratamento robusto de erros
def carregar_imagem_base64(url, size=None):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        if size:
            img = img.resize(size)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception:
        return FALLBACK_IMAGE

# Carregar imagens com fallback
try:
    LOGO_CARD_BASE64 = carregar_imagem_base64(LOGO_CARD_URL, (24, 24))
    LOGO_ICONE_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))
    FAVICON_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))
except Exception:
    LOGO_CARD_BASE64 = FALLBACK_IMAGE
    LOGO_ICONE_BASE64 = FALLBACK_IMAGE
    FAVICON_BASE64 = FALLBACK_IMAGE

# ======================================
# TEMA E CONFIGURAÇÕES (o restante permanece igual)
# ======================================
TEMAS = {
    "DARK": {
        "PRIMARIA": "#18273b",
        "SECUNDARIA": "#e0c083",
        "TERCIARIA": "#828993",
        "TEXTO": "#ffffff",
        "FUNDO": "#0e1117",
        "CARDS": "#1a2230",
        "DESTAQUE": "#e0c083",
        "BORDA": "rgba(224, 192, 131, 0.2)"
    },
    "LIGHT": {
        "PRIMARIA": "#18273b",
        "SECUNDARIA": "#e0c083",
        "TERCIARIA": "#6c757d",
        "TEXTO": "#343a40",
        "FUNDO": "#f8f9fa",
        "CARDS": "#ffffff",
        "DESTAQUE": "#e0c083",
        "BORDA": "rgba(24, 39, 59, 0.1)"
    }
}

FATURAMENTO_MENSAL = 8247358.90

PACOTES = {
    "BASIC": {
        "preco": 59.90,
        "meta": 18000,
        "cor": "#828993",
        "vendas_iniciais": 15000,
        "comissao": 0.4
    },
    "GOLD": {
        "preco": 129.90,
        "meta": 10000,
        "cor": "#e0c083",
        "vendas_iniciais": 8500,
        "comissao": 0.5
    },
    "PREMIUM": {
        "preco": 249.90,
        "meta": 6000,
        "cor": "#18273b",
        "vendas_iniciais": 5500,
        "comissao": 0.6
    }
}

# ======================================
# FUNÇÕES PRINCIPAIS (permanecem idênticas)
# ======================================
def gerar_progressao_vendas(valor_atual):
    if valor_atual == 0:
        return random.randint(1, 5)
    incremento = random.uniform(0.005, 0.02)
    return int(valor_atual * (1 + incremento))

def gerar_transacao():
    pacote, info = random.choice(list(PACOTES.items()))
    valor_base = info["preco"]
    comissao = valor_base * info["comissao"]
    
    if random.random() < 0.07:
        valor = valor_base * random.uniform(1.5, 3)
        comissao = valor * info["comissao"]
        mensagem = "🔥 Venda Premium!"
    else:
        valor = valor_base
        mensagem = "✅ Venda Realizada!"
    
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": valor,
        "Comissao": comissao,
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "Cor": info["cor"],
        "Mensagem": mensagem
    }

def gerar_historico_faturamento(dias=30):
    base = FATURAMENTO_MENSAL / 30
    return [base * random.uniform(0.85, 1.25) for _ in range(dias)]

def inicializar_dados():
    if 'dados' not in st.session_state:
        vendas_atuais = {pacote: info["vendas_iniciais"] for pacote, info in PACOTES.items()}
        
        df1 = pd.DataFrame({
            "Pacote": list(vendas_atuais.keys()),
            "Vendas": list(vendas_atuais.values()),
            "Cor": [PACOTES[p]["cor"] for p in vendas_atuais]
        })
        
        fig1 = px.line(df1, x="Pacote", y="Vendas", color="Pacote",
                      color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                      markers=True)
        fig1.update_traces(line=dict(width=3))
        
        df2 = pd.DataFrame([
            {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
        ] + [
            {"Pacote": p, "Tipo": "Realizado", "Valor": vendas_atuais[p]} for p in PACOTES
        ])
        
        fig2 = px.bar(df2, x="Pacote", y="Valor", color="Pacote",
                     barmode="group", color_discrete_map={k: v["cor"] for k, v in PACOTES.items()})
        fig2.update_layout(showlegend=False)
        
        datas = [(datetime.now() - timedelta(days=x)).strftime('%d/%m') for x in range(30)][::-1]
        fig3 = px.area(
            pd.DataFrame({
                "Data": datas,
                "Faturamento": gerar_historico_faturamento()
            }),
            x="Data",
            y="Faturamento",
            color_discrete_sequence=["#e0c083"]
        )
        
        st.session_state.dados = {
            'vendas_atuais': vendas_atuais,
            'ultimas_vendas': [],
            'fig1': fig1,
            'fig2': fig2,
            'fig3': fig3,
            'pausado': False,
            'velocidade': 3,
            'vendas_hoje': random.randint(100, 150),
            'ticket_medio': PACOTES["GOLD"]["preco"],
            'novos_clientes': random.randint(70, 120),
            'conversao_total': 78.3,
            'tema': "DARK"
        }

# ======================================
# INTERFACE PRINCIPAL (com pequenos ajustes)
# ======================================
def main():
    if 'dados' not in st.session_state:
        inicializar_dados()
    
    tema = st.session_state.dados['tema']
    cores = TEMAS[tema]
    
    # CSS Personalizado
    st.markdown(f"""
    <style>
        :root {{
            --primaria: {cores['PRIMARIA']};
            --secundaria: {cores['SECUNDARIA']};
            --terciaria: {cores['TERCIARIA']};
            --texto: {cores['TEXTO']};
            --fundo: {cores['FUNDO']};
            --cards: {cores['CARDS']};
            --destaque: {cores['DESTAQUE']};
            --borda: {cores['BORDA']};
        }}
        
        .stApp {{
            background-color: var(--fundo);
            color: var(--texto);
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, var(--primaria), #1a2a3b);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--borda);
        }}
    </style>
    <link rel="shortcut icon" href="data:image/png;base64,{FAVICON_BASE64}">
    """, unsafe_allow_html=True)

    # Barra lateral
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:30px;">
            <img src="data:image/png;base64,{LOGO_ICONE_BASE64}" style="width:80%; max-width:200px; margin:0 auto 15px; display:block;">
            <h2 style="color:{cores['SECUNDARIA']}; margin-bottom:5px;">Gold Pepper</h2>
            <p style="color:{cores['TERCIARIA']}; margin-top:0;">Business Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ... (restante do sidebar permanece igual)

    # Cabeçalho principal
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:25px;">
        <img src="data:image/png;base64,{LOGO_ICONE_BASE64}" style="height:40px; margin-right:15px;">
        <div>
            <h1 style="margin:0; color:{cores['SECUNDARIA']};">Dashboard de Vendas</h1>
            <p style="margin:0; color:{cores['TERCIARIA']};">Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ... (restante do código permanece idêntico)

if __name__ == "__main__":
    main()
