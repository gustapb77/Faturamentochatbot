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
import streamlit.components.v1 as components

# ======================================
# CONFIGURAÇÕES INICIAIS
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Gold Pepper - Dashboard Premium",
    page_icon="🌶️",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão Business"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
LOGO_CARD_URL = "https://i.ibb.co/SXmN2qzD/Logo-Card-Golden-Papper-1.png"
LOGO_ICONE_URL = "https://i.ibb.co/gLGXRBns/18273b-600-x-120-px-2500-x-590-px-400-x-400-px-2.png"
FALLBACK_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

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

LOGO_CARD_BASE64 = carregar_imagem_base64(LOGO_CARD_URL, (24, 24))
LOGO_ICONE_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))
FAVICON_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))

# ======================================
# TEMA E CORES
# ======================================
TEMAS = {
    "DARK": {
        "PRIMARIA": "#101728",
        "SECUNDARIA": "#FFFFFF",
        "TERCIARIA": "#D4AF37",
        "TEXTO": "#E0E0E0",
        "FUNDO": "#0A101A",
        "CARDS": "#1A2230",
        "DESTAQUE": "#D4AF37",
        "BORDA": "rgba(212, 175, 55, 0.2)",
        "GRADIENTE": "linear-gradient(135deg, #101728 0%, #1A2230 100%)"
    },
    "LIGHT": {
        "PRIMARIA": "#101728",
        "SECUNDARIA": "#101728",
        "TERCIARIA": "#D4AF37",
        "TEXTO": "#333333",
        "FUNDO": "#F5F5F5",
        "CARDS": "#FFFFFF",
        "DESTAQUE": "#D4AF37",
        "BORDA": "rgba(16, 23, 40, 0.1)",
        "GRADIENTE": "linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%)"
    }
}

# ======================================
# PACOTES
# ======================================
PACOTES = {
    "START": {
        "preco": 49.90,
        "meta": 15000,
        "cor": "#4ECDC4",
        "vendas_iniciais": 12000,
        "comissao": 0.4,
        "icone": "🚀"
    },
    "PREMIUM": {
        "preco": 99.90,
        "meta": 8000,
        "cor": "#FF6B6B",
        "vendas_iniciais": 6500,
        "comissao": 0.5,
        "icone": "💎"
    },
    "EXTREME": {
        "preco": 199.90,
        "meta": 4000,
        "cor": "#D4AF37",
        "vendas_iniciais": 3500,
        "comissao": 0.6,
        "icone": "🔥"
    }
}

FATURAMENTO_MENSAL = 8247358.90

# ======================================
# SISTEMA DE NOTIFICAÇÕES
# ======================================
def show_sale_notification(venda):
    pacote_info = PACOTES[venda['Pacote']]
    
    if venda['Valor'] > pacote_info['preco'] * 1.5:
        estilo = {
            "cor_borda": "#FFD700",
            "icone": "✨",
            "mensagem": "VENDA ESPECIAL!"
        }
    else:
        estilo = {
            "cor_borda": pacote_info['cor'],
            "icone": pacote_info['icone'],
            "mensagem": "Venda realizada!"
        }
    
    notification_html = f"""
    <style>
        @keyframes slideIn {{
            0% {{ transform: translateX(100%); opacity: 0; }}
            100% {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes fadeOut {{
            0% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        .notification-container {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            z-index: 1000;
        }}
        .notification {{
            animation: slideIn 0.3s ease-out, fadeOut 0.5s 5s forwards;
            margin-bottom: 15px;
            background: linear-gradient(145deg, #101728, #1A2230);
            border-left: 4px solid {estilo['cor_borda']};
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }}
        .notification-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
    </style>
    
    <div class="notification-container">
        <div class="notification">
            <div class="notification-header">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">{estilo['icone']}</span>
                    <div>
                        <div style="font-weight: 600; color: {estilo['cor_borda']};">{estilo['mensagem']}</div>
                        <div style="font-size: 12px; opacity: 0.8;">{venda['Hora']}</div>
                    </div>
                </div>
                <div style="font-weight: 700; font-size: 18px;">R${venda['Valor']:,.2f}</div>
            </div>
            <div style="font-size: 14px; margin: 8px 0;">
                <strong>{venda['Pacote']}</strong> • {venda['Nome']}
            </div>
            <div style="font-size: 12px; display: flex; justify-content: space-between;">
                <span>📍 {venda['Local']}</span>
                <span>💳 {venda['MetodoPagamento']}</span>
            </div>
        </div>
    </div>
    """
    
    components.html(notification_html, height=150)

# ======================================
# FUNÇÕES PRINCIPAIS
# ======================================
def gerar_transacao():
    pacote, info = random.choice(list(PACOTES.items()))
    valor_base = info["preco"]
    
    if random.random() < 0.1:
        valor = valor_base * random.uniform(1.3, 2.0)
        mensagem = "⭐ Venda com Upsell!"
    else:
        valor = valor_base
        mensagem = "✅ Venda realizada"
    
    metodos = ["Cartão Crédito", "Cartão Débito", "PIX", "Boleto", "Dividido"]
    
    venda = {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": valor,
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "Mensagem": mensagem,
        "MetodoPagamento": random.choice(metodos),
        "Cor": info["cor"],
        "Comissao": valor * info["comissao"],
        "Icone": info["icone"]
    }
    
    show_sale_notification(venda)
    return venda

def inicializar_dados():
    if 'dados' not in st.session_state:
        vendas_atuais = {pacote: info["vendas_iniciais"] for pacote, info in PACOTES.items()}
        
        fig1 = px.line(
            pd.DataFrame({
                "Pacote": list(vendas_atuais.keys()),
                "Vendas": list(vendas_atuais.values()),
                "Cor": [PACOTES[p]["cor"] for p in vendas_atuais]
            }),
            x="Pacote", y="Vendas", color="Pacote",
            color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
            markers=True
        )
        fig1.update_traces(line=dict(width=3))
        
        fig2 = px.bar(
            pd.DataFrame([
                {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
            ] + [
                {"Pacote": p, "Tipo": "Realizado", "Valor": vendas_atuais[p]} for p in PACOTES
            ]),
            x="Pacote", y="Valor", color="Pacote",
            barmode="group", 
            color_discrete_map={k: v["cor"] for k, v in PACOTES.items()}
        )
        fig2.update_layout(showlegend=False)
        
        datas = [(datetime.now() - timedelta(days=x)).strftime('%d/%m') for x in range(30)][::-1]
        fig3 = px.area(
            pd.DataFrame({
                "Data": datas,
                "Faturamento": [FATURAMENTO_MENSAL/30 * random.uniform(0.85,1.25) for _ in range(30)]
            }),
            x="Data",
            y="Faturamento",
            color_discrete_sequence=["#D4AF37"]
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
            'ticket_medio': PACOTES["PREMIUM"]["preco"],
            'novos_clientes': random.randint(70, 120),
            'conversao_total': 78.3,
            'tema': "DARK"
        }

# ======================================
# INTERFACE PRINCIPAL
# ======================================
def aplicar_estilos(cores):
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
            --gradiente: {cores['GRADIENTE']};
        }}
        
        .stApp {{
            background: var(--fundo);
            color: var(--texto);
            font-family: 'Segoe UI', Roboto, sans-serif;
        }}
        
        .metric-card {{
            background: var(--gradiente);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--borda);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            margin-bottom: 16px;
        }}
        
        h1, h2, h3, h4 {{
            color: var(--terciaria);
            font-weight: 600;
            border-bottom: 1px solid var(--borda);
            padding-bottom: 8px;
        }}
        
        [data-testid="stSidebar"] {{
            background: var(--gradiente) !important;
            border-right: 1px solid var(--borda);
        }}
    </style>
    <link rel="shortcut icon" href="data:image/png;base64,{FAVICON_BASE64}">
    """, unsafe_allow_html=True)

def criar_header(cores):
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:25px; border-bottom:2px solid {cores['TERCIARIA']}; padding-bottom:15px;">
        <img src="data:image/png;base64,{LOGO_ICONE_BASE64}" style="height:50px; margin-right:20px;">
        <div style="flex-grow:1;">
            <h1 style="margin:0; color:{cores['TERCIARIA']};">GOLD PEPPER BUSINESS</h1>
            <p style="margin:0; color:{cores['SECUNDARIA']};">Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def criar_sidebar(cores):
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:30px;">
            <img src="data:image/png;base64,{LOGO_ICONE_BASE64}" style="width:80%; max-width:200px; margin:0 auto 15px; display:block;">
            <h2 style="color:{cores['TERCIARIA']};">GOLD PEPPER</h2>
            <p style="color:{cores['SECUNDARIA']};">Business Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Controles")
        novo_tema = st.radio("Tema", ["DARK", "LIGHT"], index=0 if st.session_state.dados['tema'] == "DARK" else 1)
        if novo_tema != st.session_state.dados['tema']:
            st.session_state.dados['tema'] = novo_tema
            st.rerun()
        
        st.session_state.dados['velocidade'] = st.slider("Velocidade", 1, 10, 3)
        
        st.markdown("---")
        st.subheader("Últimas Vendas")
        for venda in st.session_state.dados['ultimas_vendas'][-5:][::-1]:
            st.markdown(f"""
            <div style="border-left: 3px solid {venda['Cor']}; padding-left: 10px; margin: 5px 0;">
                <small>{venda['Hora']}</small><br>
                <strong>{venda['Pacote']} {venda['Icone']}</strong> • R${venda['Valor']:,.2f}
            </div>
            """, unsafe_allow_html=True)

def criar_metric_card(title, value, change, icon="📊"):
    return f"""
    <div class="metric-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h3 style="margin:0; color:var(--terciaria); font-size:1rem;">{title}</h3>
            <span style="font-size:1.2rem;">{icon}</span>
        </div>
        <div style="font-size:1.8rem; font-weight:bold; color:var(--secundaria); margin:8px 0;">{value}</div>
        <div style="font-size:0.9rem; color:{'#4CAF50' if change >=0 else '#F44336'}">
            {'↑' if change >=0 else '↓'} {abs(change)}% vs período anterior
        </div>
    </div>
    """

def main():
    if 'dados' not in st.session_state:
        inicializar_dados()
    
    tema = st.session_state.dados['tema']
    cores = TEMAS[tema]
    
    aplicar_estilos(cores)
    criar_header(cores)
    criar_sidebar(cores)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(criar_metric_card("Faturamento", f"R${FATURAMENTO_MENSAL:,.2f}", 5.2, "💎"), unsafe_allow_html=True)
    with col2:
        st.markdown(criar_metric_card("Vendas Hoje", f"{st.session_state.dados['vendas_hoje']}", 3.8, "🛒"), unsafe_allow_html=True)
    with col3:
        st.markdown(criar_metric_card("Ticket Médio", f"R${st.session_state.dados['ticket_medio']:,.2f}", -1.2, "📊"), unsafe_allow_html=True)
    with col4:
        st.markdown(criar_metric_card("Conversão", f"{st.session_state.dados['conversao_total']}%", 2.1, "📈"), unsafe_allow_html=True)
    
    # Gráficos
    tab1, tab2, tab3 = st.tabs(["📈 Evolução de Vendas", "🎯 Metas vs Realizado", "💰 Histórico Financeiro"])
    
    with tab1:
        st.plotly_chart(st.session_state.dados['fig1'], use_container_width=True)
    
    with tab2:
        st.plotly_chart(st.session_state.dados['fig2'], use_container_width=True)
    
    with tab3:
        st.plotly_chart(st.session_state.dados['fig3'], use_container_width=True)
    
    # Atualização em tempo real
    if not st.session_state.dados['pausado']:
        time.sleep(6 - st.session_state.dados['velocidade'])
        nova_venda = gerar_transacao()
        st.session_state.dados['ultimas_vendas'].append(nova_venda)
        st.session_state.dados['vendas_hoje'] += 1
        st.rerun()

if __name__ == "__main__":
    main()
