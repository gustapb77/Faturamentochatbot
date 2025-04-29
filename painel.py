import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from faker import Faker
from datetime import datetime, timedelta
import time

# Configuração inicial
fake = Faker('pt_BR')
st.set_page_config(layout="wide", page_title="Dashboard de Vendas", page_icon="💸")

# Dados dos pacotes
PACOTES = {
    "START": {"preco": 49.90, "cor": "#FF6B6B", "meta": 15000},
    "PREMIUM": {"preco": 99.90, "cor": "#4ECDC4", "meta": 8000},
    "EXTREME": {"preco": 199.90, "cor": "#FFBE0B", "meta": 5000}
}

# Simulação de dados
def gerar_venda():
    pacote = random.choice(list(PACOTES.keys()))
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": PACOTES[pacote]["preco"],
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Cidade": fake.city()
    }

# Layout do dashboard
st.title("💰 Painel de Vendas em Tempo Real")
st.markdown("### Faturamento Atual: R$ 6.247.358,90")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Vendas Hoje", "248", "+12%")
col2.metric("Faturamento", "R$ 42.560,20", "+8%")
col3.metric("Novos Clientes", "56", "+5%")

# Gráficos
fig1 = px.line(title="Vendas Mensais")
fig2 = px.pie(names=list(PACOTES.keys()), values=[12000, 8000, 5000], title="Distribuição de Pacotes")

col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

# Atualização em tempo real
placeholder = st.empty()
while True:
    nova_venda = gerar_venda()
    with placeholder.container():
        st.json(nova_venda)
    time.sleep(3)