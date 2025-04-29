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
# CONFIGURAÇÕES INICIAIS
# ======================================
st.set_page_config(
    layout="wide",
    page_title="Gold Pepper - Dashboard",
    page_icon="🌶️",  # Será substituído pela logo
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão Premium"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
# URLs das imagens
LOGO_CARD_URL = "https://i.ibb.co/SXmN2qzD/Logo-Card-Golden-Papper-1.png"
LOGO_ICONE_URL = "https://i.ibb.co/gLGXRBns/18273b-600-x-120-px-2500-x-590-px-400-x-400-px-2.png"

# Carregar imagens em base64
def carregar_imagem_base64(url, size=None):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    if size:
        img = img.resize(size)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Tamanhos das imagens
LOGO_CARD_BASE64 = carregar_imagem_base64(LOGO_CARD_URL, (24, 24))
LOGO_ICONE_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))
FAVICON_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))

# Cores e temas
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
        "cor": "#828993",  # Usando cores fixas para manter consistência
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
# FUNÇÕES PRINCIPAIS
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
# INTERFACE PRINCIPAL
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
        
        /* Estilo base */
        .stApp {{
            background-color: var(--fundo);
            color: var(--texto);
            transition: all 0.3s ease;
        }}
        
        /* Notificações */
        .notificacao {{
            background: var(--cards) !important;
            border-left: 4px solid var(--secundaria) !important;
            border-radius: 10px !important;
            padding: 14px 18px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            transition: all 0.3s ease;
        }}
        .notificacao:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important;
        }}
        .notificacao .stToastMessage {{
            padding: 0 !important;
        }}
        .notificacao-header {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .notificacao-logo {{
            width: 24px;
            height: 24px;
            margin-right: 12px;
            background-image: url('data:image/png;base64,{LOGO_CARD_BASE64}');
            background-size: contain;
            background-repeat: no-repeat;
        }}
        .notificacao-tempo {{
            margin-left: auto;
            font-size: 0.8em;
            color: var(--terciaria);
            opacity: 0.8;
        }}
        .notificacao-valor {{
            font-weight: bold;
            font-size: 1.1em;
            color: var(--secundaria);
            margin: 8px 0;
        }}
        .notificacao-comissao {{
            font-size: 0.9em;
            color: var(--terciaria);
            opacity: 0.9;
        }}
        
        /* Cards */
        .card {{
            background: var(--cards);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid var(--borda);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--borda);
        }}
        .card-title {{
            color: var(--secundaria);
            font-weight: 600;
            margin: 0;
        }}
        
        /* Métricas */
        .metric-card {{
            background: linear-gradient(135deg, var(--primaria), #1a2a3b);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--borda);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: var(--secundaria);
            margin: 10px 0;
        }}
        .metric-label {{
            color: var(--terciaria);
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        /* Sidebar */
        .sidebar .sidebar-content {{
            background: var(--cards) !important;
            border-right: 1px solid var(--borda);
        }}
        
        /* Toggle de tema */
        .theme-toggle {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 15px 0;
        }}
        .theme-btn {{
            background: var(--cards) !important;
            border: 1px solid var(--borda) !important;
            color: var(--texto) !important;
            padding: 8px 15px !important;
            border-radius: 20px !important;
            font-size: 0.8em !important;
        }}
        .theme-btn.active {{
            background: var(--secundaria) !important;
            color: var(--primaria) !important;
            font-weight: bold !important;
        }}
        
        /* Gráficos */
        .plot-container {{
            background: var(--cards) !important;
            border-radius: 12px !important;
            padding: 15px !important;
            border: 1px solid var(--borda) !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Favicon personalizado
    st.markdown(f"""
    <link rel="shortcut icon" href="data:image/png;base64,{FAVICON_BASE64}">
    """, unsafe_allow_html=True)
    
    # Barra lateral
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:30px;">
            <img src="data:image/png;base64,{LOGO_ICONE_BASE64}" style="width:80%; max-width:200px; margin:0 auto 15px; display:block;">
            <h2 style="color:{cores['SECUNDARIA']}; margin-bottom:5px;">Gold Pepper</h2>
            <p style="color:{cores['TERCIARIA']}; margin-top:0; font-size:0.9em;">Business Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Toggle de tema
        st.markdown("### 🌓 Tema")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Escuro", key="dark_btn", help="Ativar modo escuro"):
                st.session_state.dados['tema'] = "DARK"
                st.rerun()
        with col2:
            if st.button("☀️ Claro", key="light_btn", help="Ativar modo claro"):
                st.session_state.dados['tema'] = "LIGHT"
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔍 Filtros")
        intervalo = st.select_slider(
            "Período de Análise",
            options=["7 dias", "15 dias", "30 dias", "60 dias"],
            value="30 dias",
            key="intervalo_filtro"
        )
        
        st.session_state.dados['velocidade'] = st.slider(
            "Velocidade de atualização", 1, 10, 
            st.session_state.dados['velocidade'],
            key='velocidade_slider'
        )
        
        st.markdown("---")
        st.markdown("### 🎛 Controles")
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
                f"""<div style='color:{info["cor"]}; font-weight:bold; margin: 8px 0; padding: 10px; border-radius: 8px; background-color: rgba(24, 39, 59, 0.1); border-left: 4px solid {info["cor"]}'>
                    {pacote}: {info['meta']} assinaturas
                   </div>""",
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        st.markdown(f"### 📊 Conversão Atual")
        for pacote in PACOTES:
            conversao = (st.session_state.dados['vendas_atuais'][pacote] / PACOTES[pacote]["meta"]) * 100
            cor = cores["SECUNDARIA"] if conversao >= 100 else "#FF6B6B"
            st.markdown(
                f"""<div style='margin: 8px 0; padding: 10px; border-radius: 8px; background-color: rgba(24, 39, 59, 0.1);'>
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style='font-weight:bold;'>{pacote}:</span>
                        <span style='color:{cor}; font-weight:bold;'>{conversao:.1f}%</span>
                    </div>
                    <progress value='{conversao}' max='100' style='width:100%; height:6px; border:none; background:{cores["BORDA"]};'>
                        <div style="width:{conversao}%; height:100%; background:{cor};"></div>
                    </progress>
                   </div>""",
                unsafe_allow_html=True
            )

    # Cabeçalho principal
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid {cores['BORDA']}">
        <img src="data:image/png;base64,{LOGO_ICONE_BASE64}" style="height: 40px; margin-right: 15px;">
        <div>
            <h1 style="margin: 0; color: {cores['SECUNDARIA']};">Dashboard de Vendas</h1>
            <p style="margin: 0; color: {cores['TERCIARIA']}; font-size: 0.9em;">Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Linha superior (Métricas)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Faturamento</h3>
            <div class="metric-value">R$ {FATURAMENTO_MENSAL:,.2f}</div>
            <p class="metric-label">+5.2% vs anterior</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Vendas Hoje</h3>
            <div class="metric-value">{st.session_state.dados['vendas_hoje']}</div>
            <p class="metric-label">+{random.randint(3, 8)}% vs ontem</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Ticket Médio</h3>
            <div class="metric-value">R$ {st.session_state.dados['ticket_medio']:,.2f}</div>
            <p class="metric-label">{random.choice(['+', '-'])}{random.uniform(0.5, 2.5):.1f}% variação</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Conversão</h3>
            <div class="metric-value">{st.session_state.dados['conversao_total']:.1f}%</div>
            <p class="metric-label">Meta: 85%</p>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos principais
    st.markdown("---")
    col1, col2 = st.columns([3, 2])
    
    # Containers fixos
    chart1_placeholder = col1.empty()
    chart2_placeholder = col2.empty()
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
                            <div class="notificacao-logo"></div>
                            <span>{nova_venda["Mensagem"]}</span>
                            <span class="notificacao-tempo">agora</span>
                        </div>
                        <div class="notificacao-valor">R$ {nova_venda["Valor"]:,.2f}</div>
                        <div class="notificacao-comissao">Sua comissão: R$ {nova_venda["Comissao"]:,.2f}</div>
                    </div>
                    """,
                    icon=None
                )
            
            # Atualizar gráficos
            with chart1_placeholder.container():
                st.session_state.dados['fig1'].data[0].y = list(st.session_state.dados['vendas_atuais'].values())
                st.session_state.dados['fig1'].update_layout(
                    title="Progressão de Vendas por Pacote",
                    plot_bgcolor=cores['CARDS'],
                    paper_bgcolor=cores['CARDS'],
                    font_color=cores['TEXTO'],
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(st.session_state.dados['fig1'], use_container_width=True, config={'displayModeBar': False})
            
            with chart2_placeholder.container():
                df2 = pd.DataFrame([
                    {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
                ] + [
                    {"Pacote": p, "Tipo": "Realizado", "Valor": st.session_state.dados['vendas_atuais'][p]} for p in PACOTES
                ])
                
                fig2 = px.bar(df2, x="Pacote", y="Valor", color="Pacote",
                             barmode="group", color_discrete_map={k: v["cor"] for k, v in PACOTES.items()},
                             title="Metas vs Realizado")
                fig2.update_layout(
                    showlegend=False,
                    plot_bgcolor=cores['CARDS'],
                    paper_bgcolor=cores['CARDS'],
                    font_color=cores['TEXTO'],
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.session_state.dados['fig2'] = fig2
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            
            with chart3_placeholder.container():
                st.session_state.dados['fig3'].update_layout(
                    title=f"Faturamento Histórico - {st.session_state.get('intervalo_filtro', '30 dias')}",
                    plot_bgcolor=cores['CARDS'],
                    paper_bgcolor=cores['CARDS'],
                    font_color=cores['TEXTO'],
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Data",
                    yaxis_title="Faturamento (R$)"
                )
                st.plotly_chart(st.session_state.dados['fig3'], use_container_width=True, config={'displayModeBar': False})
            
            with vendas_placeholder.container():
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🛒 Últimas Vendas em Tempo Real</h3>
                        <span style="color: {cores['TERCIARIA']}; font-size:0.9em;">Atualizado em: {datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                for venda in st.session_state.dados['ultimas_vendas']:
                    st.markdown(f"""
                    <div style="padding: 15px; margin: 10px 0; border-radius: 8px; background: rgba(24, 39, 59, 0.05); border-left: 3px solid {venda['Cor']}; transition: all 0.3s;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight:bold; font-size:1.1em; margin-bottom:5px;">{venda['Nome']}</div>
                                <div style="color: {cores['TERCIARIA']}; font-size:0.9em;">📍 {venda['Local']}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: {venda['Cor']}; font-weight:bold; font-size:1.1em;">{venda['Pacote']}</div>
                                <div style="font-weight:bold; font-size:1.1em;">💵 R$ {venda['Valor']:,.2f}</div>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top:8px; color: {cores['TERCIARIA']}; font-size:0.9em;">
                            <span>⏰ {venda['Hora']}</span>
                            <span>ID: {random.randint(10000, 99999)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            time.sleep(st.session_state.dados['velocidade'])
            
        except Exception as e:
            st.error(f"Erro no sistema: {str(e)}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
