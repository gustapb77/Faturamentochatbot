import os, subprocess, sys

# Instalação forçada de dependências
if not os.path.exists('/mount'):
    print("Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"], check=True)

# Verificação dos imports
try:
    import plotly.express as px
except ImportError:
    print("Plotly não encontrado - instalando...")
    subprocess.run([sys.executable, "-m", "pip", "install", "plotly==5.15.0"], check=True)
    import plotly.express as pximport streamlit as st
    
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from faker import Faker

# Configurações iniciais
st.set_page_config(layout="wide", page_title="Dashboard de Vendas - Paloma Premium", page_icon="💸")

fake = Faker('pt_BR')

# Dados fictícios
PACOTES = {
    "START": {"preco": 49.90, "cor": "#FF6B6B", "meta": 15000},
    "PREMIUM": {"preco": 99.90, "cor": "#4ECDC4", "meta": 8000},
    "EXTREME": {"preco": 199.90, "cor": "#FFBE0B", "meta": 5000}
}

# Gerar dados históricos
def generate_historical_data():
    data = []
    start_date = datetime.now() - timedelta(days=90)
    
    for single_date in (start_date + timedelta(n) for n in range(90)):
        for pacote in PACOTES:
            vendas = random.randint(5, 30)
            data.append({
                "Data": single_date,
                "Pacote": pacote,
                "Vendas": vendas,
                "Faturamento": vendas * PACOTES[pacote]["preco"]
            })
    
    return pd.DataFrame(data)

# Gerar transação em tempo real
def generate_transaction():
    pacote = random.choice(list(PACOTES.keys()))
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": PACOTES[pacote]["preco"],
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "cor": PACOTES[pacote]["cor"]
    }

# Layout do Dashboard
def main():
    st.title("💰 Painel de Vendas - Paloma Premium")
    st.markdown("### Faturamento Atual: R$ 6.247.358,90")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("Controles")
        velocidade = st.slider("Velocidade de atualização (segundos)", 1, 10, 3)
        st.markdown("---")
        st.markdown("**Meta Mensal:**")
        for pacote, info in PACOTES.items():
            st.markdown(f"🔹 {pacote}: {info['meta']} assinaturas")
    
    # Layout de colunas para os KPI cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kpi1 = st.empty()
    with col2:
        kpi2 = st.empty()
    with col3:
        kpi3 = st.empty()
    
    # Gráficos principais
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
        st.markdown("### 📈 Faturamento Mensal")
        chart1 = st.empty()
    
    with chart_col2:
        st.markdown("### 📊 Distribuição de Vendas")
        chart2 = st.empty()
    
    # Últimas vendas
    st.markdown("### 🛒 Últimas Vendas (Tempo Real)")
    sales_container = st.empty()
    
    # Dados iniciais
    df_historico = generate_historical_data()
    ultimas_vendas = []
    
    # Atualização em tempo real
    while True:
        # Atualizar KPIs
        vendas_hoje = sum(random.randint(5, 20) for _ in range(3))
        faturamento_hoje = sum(random.randint(10000, 50000) for _ in range(3))
        
        with col1:
            with kpi1.container():
                st.metric(label="Vendas Hoje", value=f"{random.randint(80, 120)}", delta=f"+{random.randint(3, 8)}%")
        
        with col2:
            with kpi2.container():
                st.metric(label="Faturamento Diário", value=f"R$ {random.randint(15000, 30000):,}".replace(",", "."), delta=f"+{random.randint(2, 7)}%")
        
        with col3:
            with kpi3.container():
                st.metric(label="Novos Clientes", value=random.randint(20, 50), delta=f"+{random.randint(1, 5)}%")
        
        # Atualizar gráfico 1 (linhas)
        with chart_col1:
            with chart1.container():
                df_mensal = df_historico.groupby([pd.Grouper(key='Data', freq='M'), 'Pacote']).sum().reset_index()
                fig1 = px.line(df_mensal, x="Data", y="Faturamento", color="Pacote", 
                              color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                              title="Faturamento Mensal por Pacote")
                fig1.update_layout(showlegend=True)
                st.plotly_chart(fig1, use_container_width=True)
        
        # Atualizar gráfico 2 (rosquinha)
        with chart_col2:
            with chart2.container():
                df_distribuicao = df_historico.groupby('Pacote').sum().reset_index()
                fig2 = px.pie(df_distribuicao, values='Vendas', names='Pacote', hole=0.4,
                              color='Pacote', color_discrete_map={k: v["cor"] for k, v in PACOTES.items()})
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True)
        
        # Gerar nova venda
        nova_venda = generate_transaction()
        ultimas_vendas.insert(0, nova_venda)
        
        # Manter apenas as últimas 10 vendas
        if len(ultimas_vendas) > 10:
            ultimas_vendas = ultimas_vendas[:10]
        
        # Atualizar container de últimas vendas
        with sales_container.container():
            for venda in ultimas_vendas:
                with st.container():
                    col_v1, col_v2, col_v3 = st.columns([2, 2, 1])
                    with col_v1:
                        st.markdown(f"**{venda['Nome']}**")
                    with col_v2:
                        st.markdown(f"📦 **{venda['Pacote']}**")
                    with col_v3:
                        st.markdown(f"💵 **R$ {venda['Valor']:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
                    st.markdown(f"<hr style='margin:0.2em 0; border-color: {venda['cor']}'>", unsafe_allow_html=True)
        
        # Efeito de nova venda
        st.toast(f"✅ Nova venda: {nova_venda['Nome']} - {nova_venda['Pacote']}", icon="🎉")
        
        # Aguardar antes da próxima atualização
        time.sleep(velocidade)

if __name__ == "__main__":
    main()
