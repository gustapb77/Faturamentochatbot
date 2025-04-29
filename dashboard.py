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
    page_icon="💎",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão 3.0 (Premium)"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
CORES = {
    "START": "#FF6B6B",  # Vermelho vibrante
    "PREMIUM": "#6A5ACD",  # Roxo premium (SlateBlue)
    "EXTREME": "#FFD700",  # Dourado (Gold)
    "BACKGROUND": "#0E1117",  # Fundo escuro
    "CARD": "#1E1E1E",  # Cards
    "TEXT": "#FFFFFF",  # Texto principal
    "DESTAQUE": "#FF66B3"  # Rosa destacante
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
    valor_base = info["preco"]
    
    # 5% de chance de ser uma venda especial
    if random.random() < 0.05:
        valor = valor_base * random.randint(2, 5)  # Venda grande
        mensagem = f"🌟 VENDA ESPECIAL: {fake.name()} - {pacote} (R$ {valor:,.2f})"
        icon = "🚀"
    else:
        valor = valor_base
        mensagem = f"✅ Nova venda: {fake.name()} - {pacote}"
        icon = "🎉"
    
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": valor,
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "Cor": info["cor"],
        "Mensagem": mensagem,
        "Icone": icon
    }

def gerar_historico_faturamento(dias=30):
    """Gera histórico de faturamento fictício"""
    base = FATURAMENTO_MENSAL / 30
    return [base * random.uniform(0.8, 1.2) for _ in range(dias)]

def inicializar_dados():
    """Inicializa os dados no session_state"""
    if 'dados' not in st.session_state:
        vendas_atuais = {pacote: info["vendas_iniciais"] for pacote, info in PACOTES.items()}
        
        # Gráfico 1: Progressão de Vendas
        df1 = pd.DataFrame({
            "Pacote": list(vendas_atuais.keys()),
            "Vendas": list(vendas_atuais.values()),
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
        
        # Gráfico 3: Faturamento Histórico
        datas = [(datetime.now() - timedelta(days=x)).strftime('%d/%m') for x in range(30)][::-1]
        fig3 = px.area(
            pd.DataFrame({
                "Data": datas,
                "Faturamento": gerar_historico_faturamento()
            }),
            x="Data",
            y="Faturamento",
            title="Faturamento dos Últimos 30 Dias",
            color_discrete_sequence=[CORES['PREMIUM']]
        )
        
        st.session_state.dados = {
            'vendas_atuais': vendas_atuais,
            'ultimas_vendas': [],
            'fig1': fig1,
            'fig2': fig2,
            'fig3': fig3,
            'pausado': False,
            'velocidade': 3,
            'vendas_hoje': random.randint(80, 120),
            'ticket_medio': PACOTES["PREMIUM"]["preco"],
            'novos_clientes': random.randint(50, 150)
        }

# ======================================
# INTERFACE PRINCIPAL
# ======================================
def main():
    # Aplicar estilos CSS personalizados
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {CORES['BACKGROUND']};
            color: {CORES['TEXT']};
        }}
        .css-1d391kg {{
            background-color: {CORES['CARD']};
        }}
        .card-transition {{
            transition: all 0.3s ease;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .card-transition:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2) !important;
        }}
        .pulse {{
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        @media (max-width: 768px) {{
            .st-emotion-cache-1y4p8pa {{
                padding: 1rem;
            }}
            .st-emotion-cache-1y4p8pa > div {{
                flex-direction: column;
            }}
            .metric-card {{
                margin-bottom: 1rem;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    inicializar_dados()
    
    # Barra lateral
    with st.sidebar:
        st.image("https://i.ibb.co/ks5CNrDn/IMG-9256.jpg", width=200)
        st.title("Painel de Controle")
        
        # Filtros
        st.markdown("### 🔍 Filtros")
        intervalo = st.select_slider(
            "Período de Análise",
            options=["7 dias", "15 dias", "30 dias", "60 dias"],
            value="30 dias"
        )
        
        # Controle de velocidade
        st.session_state.dados['velocidade'] = st.slider(
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
                st.rerun()
        
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
    
    # Linha superior (Métricas)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Faturamento Mensal",
            value=f"R$ {FATURAMENTO_MENSAL:,.2f}",
            delta="2.8% vs mês anterior"
        )
    with col2:
        st.metric(
            label="Vendas Hoje",
            value=st.session_state.dados['vendas_hoje'],
            delta=f"{random.randint(1, 10)}% vs ontem"
        )
    with col3:
        st.metric(
            label="Ticket Médio",
            value=f"R$ {st.session_state.dados['ticket_medio']:,.2f}",
            delta=f"{random.uniform(-2.5, 2.5):.1f}%"
        )
    with col4:
        st.metric(
            label="Novos Clientes",
            value=st.session_state.dados['novos_clientes'],
            delta=f"{random.randint(5, 20)}%"
        )

    # Gráficos principais
    st.markdown("---")
    chart_col1, chart_col2 = st.columns([3, 2])
    
    # Containers fixos
    chart1_placeholder = chart_col1.empty()
    chart2_placeholder = chart_col2.empty()
    chart3_placeholder = st.empty()
    vendas_placeholder = st.empty()

    # ======================================
    # LOOP DE ATUALIZAÇÃO
    # ======================================
    while True:
        try:
            if not st.session_state.dados['pausado']:
                # Atualizar dados com progressão lógica
                for pacote in st.session_state.dados['vendas_atuais']:
                    st.session_state.dados['vendas_atuais'][pacote] = gerar_progressao_vendas(
                        st.session_state.dados['vendas_atuais'][pacote]
                    )
                
                # Atualizar métricas
                st.session_state.dados['vendas_hoje'] += random.randint(1, 3)
                st.session_state.dados['ticket_medio'] = np.mean([
                    v['Valor'] for v in st.session_state.dados['ultimas_vendas'][-10:] 
                    if st.session_state.dados['ultimas_vendas']
                ] or [PACOTES["PREMIUM"]["preco"]])
                st.session_state.dados['novos_clientes'] += random.randint(0, 2)
                
                # Gerar nova transação
                nova_venda = gerar_transacao()
                st.session_state.dados['ultimas_vendas'].insert(0, nova_venda)
                st.session_state.dados['ultimas_vendas'] = st.session_state.dados['ultimas_vendas'][:8]
                
                # Notificação de nova venda
                st.toast(
                    nova_venda["Mensagem"],
                    icon=nova_venda["Icone"]
                )
            
            # Atualizar gráficos (mesmo quando pausado)
            with chart1_placeholder.container():
                # Atualiza apenas os dados do gráfico 1
                st.session_state.dados['fig1'].data[0].y = list(st.session_state.dados['vendas_atuais'].values())
                st.session_state.dados['fig1'].update_layout(
                    title=f"Progressão de Vendas - {datetime.now().strftime('%H:%M:%S')}",
                    plot_bgcolor=CORES['CARD'],
                    paper_bgcolor=CORES['CARD'],
                    font_color=CORES['TEXT']
                )
                st.plotly_chart(st.session_state.dados['fig1'], use_container_width=True)
            
            with chart2_placeholder.container():
                # Recria o gráfico 2 completamente
                df2 = pd.DataFrame([
                    {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
                ] + [
                    {"Pacote": p, "Tipo": "Realizado", "Valor": st.session_state.dados['vendas_atuais'][p]} for p in PACOTES
                ])
                
                fig2 = px.bar(df2, x="Pacote", y="Valor", color="Pacote",
                             barmode="group", color_discrete_map=CORES,
                             title=f"Metas vs Realizado - {datetime.now().strftime('%H:%M:%S')}")
                fig2.update_layout(
                    showlegend=False,
                    plot_bgcolor=CORES['CARD'],
                    paper_bgcolor=CORES['CARD'],
                    font_color=CORES['TEXT']
                )
                st.session_state.dados['fig2'] = fig2
                st.plotly_chart(fig2, use_container_width=True)
            
            # Gráfico de faturamento histórico
            with chart3_placeholder.container():
                st.session_state.dados['fig3'].update_layout(
                    title=f"Faturamento Histórico - {intervalo}",
                    plot_bgcolor=CORES['CARD'],
                    paper_bgcolor=CORES['CARD'],
                    font_color=CORES['TEXT']
                )
                st.plotly_chart(st.session_state.dados['fig3'], use_container_width=True)
            
            # Últimas Vendas
            with vendas_placeholder.container():
                st.markdown("### 🛒 Últimas Vendas em Tempo Real")
                
                for venda in st.session_state.dados['ultimas_vendas']:
                    st.markdown(f"""
                    <div class="card-transition" style="
                        background: rgba(30, 0, 51, 0.2);
                        padding: 12px;
                        margin: 8px 0;
                        border-left: 4px solid {venda['Cor']};
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
