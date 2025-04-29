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
# CONFIGURAÇÕES INICIAIS (Next.js Style)
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Gold Pepper - Dashboard",
    page_icon="🌶️",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão Premium"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES (Tema Claro/Escuro Dinâmico)
# ======================================
THEMES = {
    "DARK": {
        "bg": "#171717",
        "text": "#FDFDFD",
        "primary": "#3ACAF8",
        "secondary": "#e0c083",
        "card": "#1F1F1F",
        "border": "#474747"
    },
    "LIGHT": {
        "bg": "#F8F9FA",
        "text": "#343a40",
        "primary": "#0152F8",
        "secondary": "#e0c083",
        "card": "#FFFFFF",
        "border": "#DEE1E4"
    }
}

# Carregar imagens em base64 (como no HTML original)
def load_image_base64(url, size=None):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    if size:
        img = img.resize(size)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

LOGO_URL = "https://i.ibb.co/gLGXRBns/18273b-600-x-120-px-2500-x-590-px-400-x-400-px-2.png"
FAVICON_BASE64 = load_image_base64(LOGO_URL, (32, 32))

# ======================================
# COMPONENTES ESTILIZADOS (Next.js Style)
# ======================================
def notification_card(message, value, time, color):
    return f"""
    <div style="
        background: {st.session_state.theme['card']};
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center;">
            <div style="font-weight: bold; flex-grow: 1;">{message}</div>
            <div style="color: {st.session_state.theme['text']}; opacity: 0.7;">{time}</div>
        </div>
        <div style="color: {color}; font-size: 1.2em; margin-top: 4px;">R$ {value:,.2f}</div>
    </div>
    """

def metric_card(title, value, change, color):
    return f"""
    <div style="
        background: {st.session_state.theme['card']};
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {st.session_state.theme['border']};
        text-align: center;
    ">
        <div style="color: {st.session_state.theme['text']}; opacity: 0.8; font-size: 0.9em;">{title}</div>
        <div style="color: {color}; font-size: 1.8em; font-weight: bold; margin: 8px 0;">{value}</div>
        <div style="color: {'#4CAF50' if change >=0 else '#F44336'}; font-size: 0.9em;">
            {'↑' if change >=0 else '↓'} {abs(change)}%
        </div>
    </div>
    """

# ======================================
# LÓGICA DO DASHBOARD
# ======================================
def init_data():
    if 'data' not in st.session_state:
        st.session_state.data = {
            'sales': {
                'BASIC': {'current': 15000, 'target': 18000, 'color': '#828993'},
                'GOLD': {'current': 8500, 'target': 10000, 'color': '#e0c083'},
                'PREMIUM': {'current': 5500, 'target': 6000, 'color': '#18273b'}
            },
            'revenue': 8247358.90,
            'transactions': [],
            'theme': "DARK"
        }
    st.session_state.theme = THEMES[st.session_state.data['theme']]

def generate_sale():
    package = random.choice(list(st.session_state.data['sales'].keys()))
    price = {
        'BASIC': 59.90,
        'GOLD': 129.90,
        'PREMIUM': 249.90
    }[package]
    
    if random.random() < 0.1:  # 10% chance de venda premium
        price *= random.uniform(1.5, 3)
    
    return {
        'customer': fake.name(),
        'package': package,
        'value': price,
        'time': datetime.now().strftime("%H:%M:%S"),
        'city': fake.city(),
        'color': st.session_state.data['sales'][package]['color']
    }

# ======================================
# INTERFACE (Next.js Layout)
# ======================================
def main():
    init_data()
    
    # CSS Customizado (Next.js Style)
    st.markdown(f"""
    <style>
        :root {{
            --bg: {st.session_state.theme['bg']};
            --text: {st.session_state.theme['text']};
            --primary: {st.session_state.theme['primary']};
            --secondary: {st.session_state.theme['secondary']};
            --card: {st.session_state.theme['card']};
            --border: {st.session_state.theme['border']};
        }}
        
        .stApp {{
            background: var(--bg);
            color: var(--text);
        }}
        
        .stSidebar {{
            background: var(--card) !important;
            border-right: 1px solid var(--border);
        }}
        
        .plot-container {{
            background: var(--card) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            border: 1px solid var(--border) !important;
        }}
    </style>
    <link rel="shortcut icon" href="data:image/png;base64,{FAVICON_BASE64}">
    """, unsafe_allow_html=True)
    
    # Sidebar (Next.js Style)
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <img src="data:image/png;base64,{load_image_base64(LOGO_URL, (120, 60))}" 
                 style="max-width: 80%; margin-bottom: 16px;">
            <h3 style="color: {st.session_state.theme['secondary']};">Gold Pepper</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Toggle de Tema
        st.markdown("### 🌓 Tema")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Escuro", key="dark"):
                st.session_state.data['theme'] = "DARK"
                st.rerun()
        with col2:
            if st.button("☀️ Claro", key="light"):
                st.session_state.data['theme'] = "LIGHT"
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Metas")
        for pkg, data in st.session_state.data['sales'].items():
            progress = (data['current'] / data['target']) * 100
            st.markdown(f"""
            <div style="margin: 12px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span>{pkg}</span>
                    <span style="font-weight: bold; color: {data['color']}">{data['current']}/{data['target']}</span>
                </div>
                <progress value="{progress}" max="100" style="width: 100%; height: 6px; accent-color: {data['color']};"></progress>
            </div>
            """, unsafe_allow_html=True)
    
    # Main Content (Next.js Grid Layout)
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 24px;">
        <h1 style="color: {st.session_state.theme['primary']}; margin-right: auto;">Dashboard de Vendas</h1>
        <div style="color: {st.session_state.theme['text']}; opacity: 0.7;">
            {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas (Next.js Card Grid)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card(
            "Faturamento", 
            f"R$ {st.session_state.data['revenue']:,.2f}", 
            5.2,
            st.session_state.theme['primary']
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(
            "Vendas Hoje", 
            random.randint(120, 180), 
            random.uniform(2.5, 7.8),
            st.session_state.theme['secondary']
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card(
            "Ticket Médio", 
            f"R$ {random.uniform(110, 160):.2f}", 
            random.uniform(-1.5, 3.2),
            "#21BA78"
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card(
            "Conversão", 
            f"{random.uniform(72, 85):.1f}%", 
            random.uniform(0.5, 4.1),
            "#DA2B59"
        ), unsafe_allow_html=True)
    
    # Gráficos (Plotly com tema Next.js)
    st.markdown("---")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        df = pd.DataFrame({
            'Package': st.session_state.data['sales'].keys(),
            'Sales': [x['current'] for x in st.session_state.data['sales'].values()],
            'Color': [x['color'] for x in st.session_state.data['sales'].values()]
        })
        fig = px.bar(df, x='Package', y='Sales', color='Package',
                     color_discrete_map=dict(zip(df['Package'], df['Color'])),
                     title="Vendas por Pacote")
        fig.update_layout(
            plot_bgcolor=st.session_state.theme['card'],
            paper_bgcolor=st.session_state.theme['card'],
            font_color=st.session_state.theme['text']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔔 Últimas Vendas")
        for _ in range(3):
            sale = generate_sale()
            st.markdown(notification_card(
                f"{sale['customer']} • {sale['package']}",
                sale['value'],
                sale['time'],
                sale['color']
            ), unsafe_allow_html=True)
    
    # Atualização em tempo real (simulação)
    if st.button("🔄 Atualizar Dados"):
        for pkg in st.session_state.data['sales']:
            st.session_state.data['sales'][pkg]['current'] += random.randint(50, 150)
        st.session_state.data['revenue'] *= random.uniform(1.01, 1.05)
        st.rerun()

if __name__ == "__main__":
    main()
