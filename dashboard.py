import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import plotly.express as px
from faker import Faker

# ======================================
# CONFIGURAÇÕES INICIAIS
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Vendas - Paloma Premium",
    page_icon="💎",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão 2.1 (Otimizado)"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
CORES = {
    "START": "#FF6B6B",  # Vermelho
    "PREMIUM": "#4ECDC4",  # Turquesa
    "EXTREME": "#FFBE0B"  # Amarelo
}

FATURAMENTO_MENSAL = 6247358.90  # Valor fixo

PACOTES = {
    "START": {
        "preco": 49.90,
        "meta": 15000,
        "cor": CORES["START"],
        "vendas_iniciais": 12000
    },
    "PREMIUM": {
        "preco": 99.90,
        "meta": 8000,
        "cor": CORES["PREMIUM"],
        "vendas_iniciais": 8000
    },
    "EXTREME": {
        "preco": 199.90,
        "meta": 5000,
        "cor": CORES["EXTREME"],
        "vendas_iniciais": 5000
    }
}

# ======================================
# FUNÇÕES PRINCIPAIS
# ======================================
def gerar_progressao_vendas(valor_atual):
    """Gera um aumento realista baseado no valor atual"""
    if valor_atual == 0:
        return random.randint(1, 5)
    incremento = random.uniform(0.005, 0.015)  # 0.5% a 1.5%
    return int(valor_atual * (1 + incremento))

def gerar_transacao():
    """Gera uma transação fictícia com dados realistas"""
    pacote, info = random.choice(list(PACOTES.items()))
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": info["preco"],
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "Cor": info["cor"]
    }

def inicializar_dados():
    """Inicializa os dados no session_state"""
    if 'dados' not in st.session_state:
        vendas_atuais = {pacote: info["vendas_iniciais"] for pacote, info in PACOTES.items()}
        
        # Gráfico 1: Progressão de Vendas
        df1 = pd.DataFrame({
            "Pacote": vendas_atuais.keys(),
            "Vendas": vendas_atuais.values(),
            "Cor": [PACOTES[p]["cor"] for p in vendas_atuais]
        })
        
        fig1 = px.line(df1, x="Pacote", y="Vendas", color="Pacote",
                      color_discrete_map=CORES, markers=True,
                      title="Progressão de Vendas por Pacote")
        fig1.update_traces(line=dict(width=4))
        
        # Gráfico 2: Metas vs Realizado
        df2 = pd.DataFrame([
            {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
        ] + [
            {"Pacote": p, "Tipo": "Realizado", "Valor": vendas_atuais[p]} for p in PACOTES
        ])
        
        fig2 = px.bar(df2, x="Pacote", y="Valor", color="Pacote",
                     barmode="group", color_discrete_map=CORES,
                     title="Metas vs Realizado")
        fig2.update_layout(showlegend=False)
        
        st.session_state.dados = {
            'vendas_atuais': vendas_atuais,
            'ultimas_vendas': [],
            'fig1': fig1,
            'fig2': fig2,
            'pausado': False,
            'velocidade': 3
        }

# ======================================
# INTERFACE PRINCIPAL
# ======================================
def main():
    inicializar_dados()
    
    # Barra lateral
    with st.sidebar:
        st.image("https://i.ibb.co/ks5CNrDn/IMG-9256.jpg", width=200)
        st.title("Painel de Controle")
        
        # Controle de velocidade
        nova_velocidade = st.slider(
            "Velocidade de atualização", 1, 10, 
            st.session_state.dados['velocidade'],
            key='velocidade_slider'
        )
        
        # Botões de controle
        col1, col2 = st.columns(2)
        with col1:
            if st.button('⏸️ Pausar' if not st.session_state.dados['pausado'] else '▶️ Continuar'):
                st.session_state.dados['pausado'] = not st.session_state.dados['pausado']
        with col2:
            if st.button('🔄 Reiniciar'):
                inicializar_dados()
        
        st.markdown("---")
        st.markdown("### Metas Mensais")
        for pacote, info in PACOTES.items():
            st.markdown(
                f"<div style='color:{info['cor']}; font-weight:bold; margin: 5px 0;'>"
                f"◉ {pacote}: {info['meta']} assinaturas"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Exibir conversão atual
        st.markdown("---")
        st.markdown("### Conversão Atual")
        for pacote in PACOTES:
            conversao = (st.session_state.dados['vendas_atuais'][pacote] / PACOTES[pacote]["meta"]) * 100
            cor = "#00FF00" if conversao >= 100 else "#FF0000"
            st.markdown(
                f"<div style='margin: 8px 0;'>"
                f"<span style='font-weight:bold;'>{pacote}:</span> "
                f"<span style='color:{cor}; font-weight:bold;'>{conversao:.1f}%</span> "
                f"({st.session_state.dados['vendas_atuais'][pacote]}/{PACOTES[pacote]['meta']})"
                f"</div>",
                unsafe_allow_html=True
            )

    # Cabeçalho principal
    st.title("📊 Dashboard de Vendas - Paloma Premium")
    
    # Linha superior (Faturamento + Vendas Hoje)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        ">
            <h2 style="color: #ff66b3; margin-top:0;">Faturamento Mensal</h2>
            <h1 style="margin:0; font-size:2.5em;">R$ {FATURAMENTO_MENSAL:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        vendas_hoje = random.randint(80, 120)
        st.markdown(f"""
        <div style="
            background: rgba(30, 0, 51, 0.3);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #ff66b3;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        ">
            <h3 style="margin-top:0; color:#ff66b3;">Vendas Hoje</h3>
            <h1 style="margin:0; color:#ff66b3; font-size:2.5em;">{vendas_hoje}</h1>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos principais
    st.markdown("---")
    chart_col1, chart_col2 = st.columns([3, 2])
    
    # Containers fixos
    chart1_placeholder = chart_col1.empty()
    chart2_placeholder = chart_col2.empty()
    vendas_placeholder = st.empty()

    # ======================================
    # LOOP DE ATUALIZAÇÃO
    # ======================================
    while True:
        try:
            # Atualizar velocidade se mudou
            if nova_velocidade != st.session_state.dados['velocidade']:
                st.session_state.dados['velocidade'] = nova_velocidade
            
            if not st.session_state.dados['pausado']:
                # Atualizar dados com progressão lógica
                for pacote in st.session_state.dados['vendas_atuais']:
                    st.session_state.dados['vendas_atuais'][pacote] = gerar_progressao_vendas(
                        st.session_state.dados['vendas_atuais'][pacote]
                    )
                
                # Gerar nova transação
                nova_venda = gerar_transacao()
                st.session_state.dados['ultimas_vendas'].insert(0, nova_venda)
                st.session_state.dados['ultimas_vendas'] = st.session_state.dados['ultimas_vendas'][:8]
                
                # Notificação de nova venda
                st.toast(
                    f"✅ Nova venda: {nova_venda['Nome']} - {nova_venda['Pacote']}",
                    icon="🎉"
                )
            
            # Atualizar gráficos (mesmo quando pausado)
            with chart1_placeholder.container():
                # Atualiza apenas os dados do gráfico 1
                st.session_state.dados['fig1'].data[0].y = list(st.session_state.dados['vendas_atuais'].values())
                st.session_state.dados['fig1'].update_layout(
                    title=f"Progressão de Vendas - {datetime.now().strftime('%H:%M:%S')}"
                )
                st.plotly_chart(st.session_state.dados['fig1'], use_container_width=True)
            
            with chart2_placeholder.container():
                # Atualiza apenas os dados realizados no gráfico 2
                for i, p in enumerate(PACOTES):
                    st.session_state.dados['fig2'].data[i+len(PACOTES)].y = [st.session_state.dados['vendas_atuais'][p]]
                st.plotly_chart(st.session_state.dados['fig2'], use_container_width=True)
            
            # Últimas Vendas
            with vendas_placeholder.container():
                st.markdown("### 🛒 Últimas Vendas em Tempo Real")
                
                for venda in st.session_state.dados['ultimas_vendas']:
                    st.markdown(f"""
                    <div style="
                        background: rgba(30, 0, 51, 0.2);
                        padding: 12px;
                        border-radius: 8px;
                        margin: 8px 0;
                        border-left: 4px solid {venda['Cor']};
                        transition: all 0.3s;
                    ">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight:bold;">{venda['Nome']}</span>
                            <span style="color: {venda['Cor']}; font-weight:bold;">{venda['Pacote']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top:5px;">
                            <span style="font-size:0.9em;">📍 {venda['Local']}</span>
                            <span style="font-size:0.9em;">⏰ {venda['Hora']}</span>
                            <span style="font-weight:bold;">💵 R$ {venda['Valor']:,.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            time.sleep(st.session_state.dados['velocidade'])
            
        except Exception as e:
            st.error(f"Erro no sistema: {str(e)}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
