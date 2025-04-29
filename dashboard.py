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
    page_title="Dashboard Gold Pepper",
    page_icon="🌶️",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão Premium"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
CORES = {
    "PRIMARIA": "#18273b",       # Azul escuro corporativo
    "SECUNDARIA": "#e0c083",     # Dourado Gold Pepper
    "TERCIARIA": "#828993",      # Cinza metálico
    "TEXTO": "#ffffff",          # Branco para texto
    "FUNDO": "#0e1117",          # Fundo escuro
    "CARDS": "#1a2230",          # Cards escuros
    "DESTAQUE": "#e0c083"        # Dourado para destaques
}

FATURAMENTO_MENSAL = 8247358.90  # Valor atualizado

PACOTES = {
    "BASIC": {
        "preco": 59.90,
        "meta": 18000,
        "cor": CORES["TERCIARIA"],
        "vendas_iniciais": 15000,
        "comissao": 0.4  # 40% de comissão
    },
    "GOLD": {
        "preco": 129.90,
        "meta": 10000,
        "cor": CORES["SECUNDARIA"],
        "vendas_iniciais": 8500,
        "comissao": 0.5  # 50% de comissão
    },
    "PREMIUM": {
        "preco": 249.90,
        "meta": 6000,
        "cor": CORES["PRIMARIA"],
        "vendas_iniciais": 5500,
        "comissao": 0.6  # 60% de comissão
    }
}

# URLs das imagens (substitua pelos seus links do ImgBB)
LOGO_URL = "hthttps://i.ibb.co/gLGXRBns/18273b-600-x-120-px-2500-x-590-px-400-x-400-px-2.png"  # Logo principal (sidebar)
LOGO_MINI_URL = "https://i.ibb.co/SXmN2qzD/Logo-Card-Golden-Papper-1.png"  # Logo pequena (notificações)

# ======================================
# FUNÇÕES PRINCIPAIS
# ======================================
def gerar_progressao_vendas(valor_atual):
    """Gera um aumento realista baseado no valor atual"""
    if valor_atual == 0:
        return random.randint(1, 5)
    incremento = random.uniform(0.005, 0.02)  # 0.5% a 2%
    return int(valor_atual * (1 + incremento))

def gerar_transacao():
    """Gera uma transação fictícia com dados realistas"""
    pacote, info = random.choice(list(PACOTES.items()))
    valor_base = info["preco"]
    comissao = valor_base * info["comissao"]
    
    # 7% de chance de ser uma venda especial (pimenta dourada)
    if random.random() < 0.07:
        valor = valor_base * random.uniform(1.5, 3)  # Venda premium
        comissao = valor * info["comissao"]
        mensagem = "🔥 Venda Premium!"
        icon = "🚀"
    else:
        valor = valor_base
        mensagem = "✅ Venda Realizada!"
        icon = "🛒"
    
    return {
        "Nome": fake.name(),
        "Pacote": pacote,
        "Valor": valor,
        "Comissao": comissao,
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Local": fake.city(),
        "Cor": info["cor"],
        "Mensagem": mensagem,
        "Icone": icon
    }

def gerar_historico_faturamento(dias=30):
    """Gera histórico de faturamento fictício"""
    base = FATURAMENTO_MENSAL / 30
    return [base * random.uniform(0.85, 1.25) for _ in range(dias)]

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
                      color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                      markers=True, title="Progressão de Vendas por Pacote")
        fig1.update_traces(line=dict(width=3))
        
        # Gráfico 2: Metas vs Realizado
        df2 = pd.DataFrame([
            {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
        ] + [
            {"Pacote": p, "Tipo": "Realizado", "Valor": vendas_atuais[p]} for p in PACOTES
        ])
        
        fig2 = px.bar(df2, x="Pacote", y="Valor", color="Pacote",
                     barmode="group", color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
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
            color_discrete_sequence=[CORES["SECUNDARIA"]]
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
            'conversao_total': 78.3
        }

# ======================================
# INTERFACE PRINCIPAL
# ======================================
def main():
    # CSS Personalizado para notificações
    st.markdown(f"""
    <style>
        /* Estilo das notificações */
        .notificacao {{
            background: {CORES['CARDS']} !important;
            border-left: 4px solid {CORES['SECUNDARIA']} !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
        }}
        .notificacao .stToastMessage {{
            padding: 0 !important;
        }}
        .notificacao-header {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        .notificacao-logo {{
            width: 24px;
            height: 24px;
            margin-right: 10px;
        }}
        .notificacao-tempo {{
            margin-left: auto;
            font-size: 0.8em;
            color: {CORES['TERCIARIA']};
        }}
        .notificacao-valor {{
            font-weight: bold;
            color: {CORES['SECUNDARIA']};
            margin: 5px 0;
        }}
        .notificacao-comissao {{
            font-size: 0.9em;
            color: {CORES['TERCIARIA']};
        }}
        
        /* Estilo geral */
        .stApp {{
            background-color: {CORES['FUNDO']};
            color: {CORES['TEXTO']};
        }}
        .css-1d391kg, .st-emotion-cache-1y4p8pa {{
            background-color: {CORES['FUNDO']} !important;
        }}
        .card-goldpepper {{
            background: {CORES['CARDS']};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid {CORES['SECUNDARIA']};
            transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .card-goldpepper:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(224, 192, 131, 0.2);
        }}
        .metric-card {{
            background: linear-gradient(135deg, {CORES['PRIMARIA']}, #1a2a3b);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }}
        .pulse-gold {{
            animation: pulse-gold 2s infinite;
        }}
        @keyframes pulse-gold {{
            0% {{ box-shadow: 0 0 0 0 rgba(224, 192, 131, 0.4); }}
            70% {{ box-shadow: 0 0 0 10px rgba(224, 192, 131, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(224, 192, 131, 0); }}
        }}
        @media (max-width: 768px) {{
            .st-emotion-cache-1y4p8pa {{
                padding: 1rem !important;
            }}
            .metric-card {{
                margin-bottom: 15px;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    inicializar_dados()
    
    # Barra lateral
    with st.sidebar:
        st.image(LOGO_URL, width=200)
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:30px;">
            <h2 style="color:{CORES['SECUNDARIA']}; margin-bottom:0;">Gold Pepper</h2>
            <p style="color:{CORES['TERCIARIA']}; margin-top:0;">Business Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtros
        st.markdown("### 🔍 Filtros")
        intervalo = st.select_slider(
            "Período de Análise",
            options=["7 dias", "15 dias", "30 dias", "60 dias"],
            value="30 dias",
            key="intervalo_filtro"
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
            if st.button('⏸️ Pausar' if not st.session_state.dados['pausado'] else '▶️ Continuar',
                        help="Pausar/Continuar atualizações em tempo real"):
                st.session_state.dados['pausado'] = not st.session_state.dados['pausado']
        with col2:
            if st.button('🔄 Reiniciar', help="Reiniciar todos os dados"):
                inicializar_dados()
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"### 🌶️ Metas Mensais")
        for pacote, info in PACOTES.items():
            st.markdown(
                f"""<div style='color:{info["cor"]}; font-weight:bold; margin: 8px 0; padding: 8px; border-radius: 6px; background-color: rgba(24, 39, 59, 0.3);'>
                    {pacote}: {info['meta']} assinaturas
                   </div>""",
                unsafe_allow_html=True
            )
        
        # Exibir conversão atual
        st.markdown("---")
        st.markdown(f"### 📊 Conversão Atual")
        for pacote in PACOTES:
            conversao = (st.session_state.dados['vendas_atuais'][pacote] / PACOTES[pacote]["meta"]) * 100
            cor = CORES["SECUNDARIA"] if conversao >= 100 else "#FF6B6B"
            st.markdown(
                f"""<div style='margin: 8px 0; padding: 8px; border-radius: 6px; background-color: rgba(24, 39, 59, 0.3);'>
                    <span style='font-weight:bold;'>{pacote}:</span>
                    <span style='color:{cor}; font-weight:bold;'>{conversao:.1f}%</span>
                    <progress value='{conversao}' max='100' style='width:100%; height:6px;'></progress>
                   </div>""",
                unsafe_allow_html=True
            )

    # Cabeçalho principal com logo
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <img src="{LOGO_MINI_URL}" style="height: 28px; margin-right: 10px;">
        <h1 style="margin: 0; color: {CORES['SECUNDARIA']};">Dashboard de Vendas</h1>
        <span style="margin-left: auto; color: {CORES['TERCIARIA']}; font-size: 0.9em;">
            Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Linha superior (Métricas)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card pulse-gold">
            <h3 style="color: {CORES['SECUNDARIA']}; margin-top:0;">Faturamento</h3>
            <h2 style="margin:0;">R$ {FATURAMENTO_MENSAL:,.2f}</h2>
            <p style="margin-bottom:0; color:{CORES['TERCIARIA']};">+5.2% vs anterior</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {CORES['SECUNDARIA']}; margin-top:0;">Vendas Hoje</h3>
            <h2 style="margin:0;">{st.session_state.dados['vendas_hoje']}</h2>
            <p style="margin-bottom:0; color:{CORES['TERCIARIA']};">+{random.randint(3, 8)}% vs ontem</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {CORES['SECUNDARIA']}; margin-top:0;">Ticket Médio</h3>
            <h2 style="margin:0;">R$ {st.session_state.dados['ticket_medio']:,.2f}</h2>
            <p style="margin-bottom:0; color:{CORES['TERCIARIA']};">{random.choice(['+', '-'])}{random.uniform(0.5, 2.5):.1f}% variação</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {CORES['SECUNDARIA']}; margin-top:0;">Conversão</h3>
            <h2 style="margin:0;">{st.session_state.dados['conversao_total']:.1f}%</h2>
            <p style="margin-bottom:0; color:{CORES['TERCIARIA']};">Meta: 85%</p>
        </div>
        """, unsafe_allow_html=True)

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
                st.session_state.dados['vendas_hoje'] += random.randint(1, 4)
                st.session_state.dados['ticket_medio'] = np.mean([
                    v['Valor'] for v in st.session_state.dados['ultimas_vendas'][-10:] 
                    if st.session_state.dados['ultimas_vendas']
                ] or [PACOTES["GOLD"]["preco"]])
                st.session_state.dados['novos_clientes'] += random.randint(0, 3)
                st.session_state.dados['conversao_total'] = min(
                    100, st.session_state.dados['conversao_total'] + random.uniform(-0.2, 0.5))
                
                # Gerar nova transação
                nova_venda = gerar_transacao()
                st.session_state.dados['ultimas_vendas'].insert(0, nova_venda)
                st.session_state.dados['ultimas_vendas'] = st.session_state.dados['ultimas_vendas'][:10]
                
                # Notificação de venda no estilo Kiwify/Kirvano
                st.toast(
                    f"""
                    <div class="notificacao">
                        <div class="notificacao-header">
                            <img src="{LOGO_MINI_URL}" class="notificacao-logo">
                            <span>{nova_venda["Mensagem"]}</span>
                            <span class="notificacao-tempo">agora</span>
                        </div>
                        <div class="notificacao-valor">R$ {nova_venda["Valor"]:,.2f}</div>
                        <div class="notificacao-comissao">Sua comissão: R$ {nova_venda["Comissao"]:,.2f}</div>
                    </div>
                    """,
                    icon=nova_venda["Icone"]
                )
            
            # Atualizar gráficos (mesmo quando pausado)
            with chart1_placeholder.container():
                # Atualiza apenas os dados do gráfico 1
                st.session_state.dados['fig1'].data[0].y = list(st.session_state.dados['vendas_atuais'].values())
                st.session_state.dados['fig1'].update_layout(
                    title=f"Progressão de Vendas - {datetime.now().strftime('%H:%M')}",
                    plot_bgcolor=CORES["CARDS"],
                    paper_bgcolor=CORES["CARDS"],
                    font_color=CORES["TEXTO"],
                    hovermode="x unified"
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
                             barmode="group", color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                             title=f"Metas vs Realizado - {datetime.now().strftime('%H:%M')}")
                fig2.update_layout(
                    showlegend=False,
                    plot_bgcolor=CORES["CARDS"],
                    paper_bgcolor=CORES["CARDS"],
                    font_color=CORES["TEXTO"],
                    hovermode="x unified"
                )
                st.session_state.dados['fig2'] = fig2
                st.plotly_chart(fig2, use_container_width=True)
            
            # Gráfico de faturamento histórico
            with chart3_placeholder.container():
                st.session_state.dados['fig3'].update_layout(
                    title=f"Faturamento Histórico - {st.session_state.get('intervalo_filtro', '30 dias')}",
                    plot_bgcolor=CORES["CARDS"],
                    paper_bgcolor=CORES["CARDS"],
                    font_color=CORES["TEXTO"],
                    hovermode="x unified",
                    xaxis_title="Data",
                    yaxis_title="Faturamento (R$)"
                )
                st.plotly_chart(st.session_state.dados['fig3'], use_container_width=True)
            
            # Últimas Vendas
            with vendas_placeholder.container():
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="color: {CORES['SECUNDARIA']}; margin:0;">🛒 Últimas Vendas em Tempo Real</h3>
                    <span style="color: {CORES['TERCIARIA']}; font-size:0.9em;">Atualizado em: {datetime.now().strftime('%H:%M:%S')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                for venda in st.session_state.dados['ultimas_vendas']:
                    st.markdown(f"""
                    <div class="card-goldpepper">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight:bold; font-size:1.1em;">{venda['Nome']}</span>
                                <span style="color: {CORES['TERCIARIA']}; font-size:0.9em; display:block;">📍 {venda['Local']}</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="color: {venda['Cor']}; font-weight:bold; font-size:1.1em;">{venda['Pacote']}</span>
                                <span style="color: {CORES['TEXTO']}; font-weight:bold; font-size:1.1em; display:block;">💵 R$ {venda['Valor']:,.2f}</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top:8px; color: {CORES['TERCIARIA']};">
                            <span>⏰ {venda['Hora']}</span>
                            <span>ID: {random.randint(10000, 99999)}</span>
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
