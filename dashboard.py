import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
from faker import Faker

# ======================================
# CONFIGURAÇÕES INICIAIS
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Vendas - Paloma Premium",
    page_icon="💸",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Paloma Premium"
    }
)

fake = Faker('pt_BR')

# ======================================
# DADOS DOS PACOTES (CONFIGURÁVEL)
# ======================================
PACOTES = {
    "START": {
        "preco": 49.90,
        "cor": "#FF6B6B",
        "meta": 15000,
        "desc": "10 fotos + 3 vídeos"
    },
    "PREMIUM": {
        "preco": 99.90,
        "cor": "#4ECDC4",
        "meta": 8000,
        "desc": "20 fotos + 5 vídeos"
    },
    "EXTREME": {
        "preco": 199.90,
        "cor": "#FFBE0B",
        "meta": 5000,
        "desc": "30 fotos + 10 vídeos"
    }
}

# ======================================
# FUNÇÕES PRINCIPAIS (COM CACHE)
# ======================================
@st.cache_data
def generate_historical_data(days=90):
    """Gera dados históricos fictícios com cache para performance"""
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for single_date in (start_date + timedelta(n) for n in range(days)):
        for pacote, info in PACOTES.items():
            vendas = random.randint(5, 30)
            data.append({
                "Data": single_date.strftime("%Y-%m-%d"),
                "Pacote": pacote,
                "Vendas": vendas,
                "Faturamento": vendas * info["preco"],
                "Meta": info["meta"]
            })
    
    return pd.DataFrame(data)

def generate_transaction():
    """Gera uma transação fictícia em tempo real"""
    pacote = random.choice(list(PACOTES.keys()))
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": PACOTES[pacote]["preco"],
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "cor": PACOTES[pacote]["cor"]
    }

# ======================================
# LAYOUT PRINCIPAL
# ======================================
def main():
    # Cabeçalho
    st.title("💰 Painel de Vendas - Paloma Premium")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("⚙️ Controles")
        velocidade = st.slider("Velocidade de atualização (segundos)", 1, 10, 3)
        
        st.markdown("---")
        st.header("📊 Metas Mensais")
        for pacote, info in PACOTES.items():
            st.metric(
                label=f"{pacote} - {info['desc']}",
                value=f"R$ {info['meta']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                delta=f"Meta: {info['meta']} assin."
            )
    
    # Containers FIXOS (fora do loop)
    col1, col2, col3 = st.columns(3)
    chart_col1, chart_col2 = st.columns([3, 2])
    sales_container = st.container()
    
    # Inicializa containers vazios
    kpi1 = col1.empty()
    kpi2 = col2.empty()
    kpi3 = col3.empty()
    chart1_placeholder = chart_col1.empty()
    chart2_placeholder = chart_col2.empty()
    sales_placeholder = sales_container.empty()
    
    # Dados iniciais
    df_historico = generate_historical_data()
    ultimas_vendas = []
    
    # ======================================
    # LOOP PRINCIPAL (ATUALIZAÇÃO EM TEMPO REAL)
    # ======================================
    while True:
        try:
            # Atualizar KPIs
            with kpi1:
                st.metric(
                    label="Vendas Hoje",
                    value=random.randint(80, 120),
                    delta=f"+{random.randint(3, 8)}%"
                )
            
            with kpi2:
                st.metric(
                    label="Faturamento Diário",
                    value=f"R$ {random.randint(15000, 30000):,}".replace(",", "X").replace(".", ",").replace("X", "."),
                    delta=f"+{random.randint(2, 7)}%"
                )
            
            with kpi3:
                st.metric(
                    label="Novos Clientes",
                    value=random.randint(20, 50),
                    delta=f"+{random.randint(1, 5)}%"
                )
            
            # Gráfico 1: Faturamento Mensal
            with chart1_placeholder:
                st.markdown("### 📈 Faturamento Mensal")
                df_mensal = df_historico.copy()
                df_mensal['Data'] = pd.to_datetime(df_mensal['Data'])
                
                fig1 = px.line(
                    df_mensal.groupby([pd.Grouper(key='Data', freq='M'), 'Pacote']).sum().reset_index(),
                    x="Data",
                    y="Faturamento",
                    color="Pacote",
                    color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                    labels={"Faturamento": "Faturamento (R$)", "Data": "Mês"},
                    template="plotly_white"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            # Gráfico 2: Distribuição de Vendas
            with chart2_placeholder:
                st.markdown("### 📊 Distribuição de Vendas")
                df_distribuicao = df_historico.groupby('Pacote').agg({
                    'Vendas': 'sum',
                    'Faturamento': 'sum'
                }).reset_index()
                
                fig2 = px.pie(
                    df_distribuicao,
                    values='Vendas',
                    names='Pacote',
                    hole=0.4,
                    color='Pacote',
                    color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                    hover_data=['Faturamento']
                )
                fig2.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Últimas vendas (Tempo Real)
            with sales_placeholder:
                st.markdown("### 🛒 Últimas Vendas (Tempo Real)")
                
                # Gerar nova venda
                nova_venda = generate_transaction()
                ultimas_vendas.insert(0, nova_venda)
                ultimas_vendas = ultimas_vendas[:10]  # Manter apenas as 10 últimas
                
                for venda in ultimas_vendas:
                    with st.container():
                        cols = st.columns([2, 2, 1, 1])
                        with cols[0]:
                            st.markdown(f"**{venda['Nome']}**")
                        with cols[1]:
                            st.markdown(f"📍 {venda['Local']}")
                        with cols[2]:
                            st.markdown(f"📦 **{venda['Pacote']}**")
                        with cols[3]:
                            st.markdown(f"💵 **R$ {venda['Valor']:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
                        st.markdown(f"<hr style='margin:0.2em 0; border-color: {venda['cor']}'>", unsafe_allow_html=True)
            
            # Notificação de nova venda
            st.toast(
                f"✅ Nova venda: {nova_venda['Nome']} - {nova_venda['Pacote']}",
                icon="🎉"
            )
            
            # Intervalo de atualização
            time.sleep(velocidade)
            
        except Exception as e:
            st.error(f"Erro no sistema: {str(e)}")
            time.sleep(5)  # Espera antes de tentar novamente

# ======================================
# INICIALIZAÇÃO
# ======================================
if __name__ == "__main__":
    # Verificação de dependências
    try:
        import plotly.express
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    main()
