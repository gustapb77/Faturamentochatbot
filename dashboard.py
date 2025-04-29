import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.express as px
from faker import Faker

# ======================================
# CONFIGURAÇÕES INICIAIS
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Vendas - Paloma Premium",
    page_icon="💎"
)

fake = Faker('pt_BR')

# Cores dos pacotes (exatamente como no chatbot original)
CORES = {
    "START": "#FF6B6B",  # Vermelho
    "PREMIUM": "#4ECDC4",  # Turquesa
    "EXTREME": "#FFBE0B"  # Amarelo
}

# ======================================
# DADOS FIXOS (SIMULAÇÃO REALISTA)
# ======================================
FATURAMENTO_MENSAL = 6247358.90  # Valor fixo como solicitado

# Preços e metas dos pacotes
PACOTES = {
    "START": {
        "preco": 49.90,
        "meta": 15000,
        "cor": CORES["START"]
    },
    "PREMIUM": {
        "preco": 99.90,
        "meta": 8000,
        "cor": CORES["PREMIUM"]
    },
    "EXTREME": {
        "preco": 199.90,
        "meta": 5000,
        "cor": CORES["EXTREME"]
    }
}

# ======================================
# FUNÇÕES PRINCIPAIS
# ======================================
def gerar_venda_realista(base_anterior):
    """Gera vendas com progressão lógica (sempre crescente)"""
    incremento = random.uniform(0.8, 1.5)  # Variação controlada
    return base_anterior * incremento

def gerar_transacao():
    """Gera uma transação fictícia com cores temáticas"""
    pacote = random.choice(list(PACOTES.keys()))
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": PACOTES[pacote]["preco"],
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "Cor": PACOTES[pacote]["cor"]
    }

# ======================================
# LAYOUT DO DASHBOARD
# ======================================
def main():
    # Barra lateral com controles
    with st.sidebar:
        st.image("https://i.ibb.co/ks5CNrDn/IMG-9256.jpg", width=200)
        st.title("Controles")
        velocidade = st.slider("Velocidade", 1, 5, 3)
        st.markdown("---")
        st.markdown("**Metas Mensais:**")
        for pacote, info in PACOTES.items():
            st.markdown(f"<span style='color:{info['cor']}; font-weight:bold'>◉ {pacote}:</span> {info['meta']} assinaturas", 
                        unsafe_allow_html=True)

    # Linha superior (Faturamento + Vendas Hoje)
    st.title("📊 Dashboard de Vendas - Paloma Premium")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            padding: 20px;
            border-radius: 10px;
            color: white;
        ">
            <h2 style="color: #ff66b3; margin-top:0;">Faturamento Mensal</h2>
            <h1 style="margin:0;">R$ {FATURAMENTO_MENSAL:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        vendas_hoje = random.randint(80, 120)
        st.markdown(f"""
        <div style="
            background: rgba(255, 102, 179, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #ff66b3;
        ">
            <h3 style="margin-top:0;">Vendas Hoje</h3>
            <h1 style="color: #ff66b3; margin:0;">{vendas_hoje}</h1>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos principais
    st.markdown("---")
    chart_col1, chart_col2 = st.columns([3, 2])
    
    # Dados iniciais
    historico_vendas = {
        "START": 12000,
        "PREMIUM": 8000,
        "EXTREME": 5000
    }
    ultimas_vendas = []

    # Containers fixos
    chart1_placeholder = chart_col1.empty()
    chart2_placeholder = chart_col2.empty()
    vendas_placeholder = st.empty()

    # ======================================
    # LOOP DE ATUALIZAÇÃO
    # ======================================
    while True:
        try:
            # Atualizar dados com progressão lógica
            for pacote in historico_vendas:
                historico_vendas[pacote] = gerar_venda_realista(historico_vendas[pacote])
            
            # Gráfico 1: Distribuição de Vendas
            with chart1_placeholder:
                df = pd.DataFrame({
                    "Pacote": historico_vendas.keys(),
                    "Vendas": historico_vendas.values(),
                    "Cor": [PACOTES[p]["cor"] for p in historico_vendas]
                })
                
                fig = px.bar(
                    df,
                    x="Pacote",
                    y="Vendas",
                    color="Pacote",
                    color_discrete_map=CORES,
                    title="Vendas por Pacote (Progressão Realista)"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico 2: Metas vs Realizado
            with chart2_placeholder:
                df_metas = pd.DataFrame([
                    {
                        "Pacote": p,
                        "Tipo": "Meta",
                        "Valor": PACOTES[p]["meta"],
                        "Cor": PACOTES[p]["cor"]
                    }
                    for p in PACOTES
                ] + [
                    {
                        "Pacote": p,
                        "Tipo": "Realizado",
                        "Valor": historico_vendas[p],
                        "Cor": PACOTES[p]["cor"]
                    }
                    for p in PACOTES
                ])
                
                fig = px.bar(
                    df_metas,
                    x="Pacote",
                    y="Valor",
                    color="Pacote",
                    barmode="group",
                    color_discrete_map=CORES,
                    title="Metas vs Realizado"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Últimas Vendas (Mantido como estava)
            with vendas_placeholder:
                st.markdown("### 🛒 Últimas Vendas")
                
                nova_venda = gerar_transacao()
                ultimas_vendas.insert(0, nova_venda)
                ultimas_vendas = ultimas_vendas[:10]
                
                for venda in ultimas_vendas:
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        padding: 10px;
                        border-radius: 5px;
                        margin: 5px 0;
                        border-left: 3px solid {venda['Cor']};
                    ">
                        <div style="display: flex; justify-content: space-between;">
                            <span><strong>{venda['Nome']}</strong></span>
                            <span style="color: {venda['Cor']}"><strong>{venda['Pacote']}</strong></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
                            <span>📍 {venda['Local']}</span>
                            <span>💵 R$ {venda['Valor']:,.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            time.sleep(velocidade)
            
        except Exception as e:
            st.error(f"Erro: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()
