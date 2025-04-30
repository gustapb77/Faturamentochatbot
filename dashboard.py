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
    page_icon="🌶️",
    menu_items={
        'About': "Dashboard de vendas em tempo real - Versão Premium"
    }
)

fake = Faker('pt_BR')

# ======================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================
LOGO_CARD_URL = "https://i.ibb.co/SXmN2qzD/Logo-Card-Golden-Papper-1.png"
LOGO_ICONE_URL = "https://i.ibb.co/gLGXRBns/18273b-600-x-120-px-2500-x-590-px-400-x-400-px-2.png"

def carregar_imagem_base64(url, size=None):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    if size:
        img = img.resize(size)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

LOGO_CARD_BASE64 = carregar_imagem_base64(LOGO_CARD_URL, (24, 24))
LOGO_ICONE_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))
FAVICON_BASE64 = carregar_imagem_base64(LOGO_ICONE_URL, (32, 32))

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
        "cor": "#828993",
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
        
        .stApp {{
            background-color: var(--fundo);
            color: var(--texto);
            transition: all 0.3s ease;
        }}
        
        .card {{
            background: var(--cards);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid var(--borda);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, var(--primaria), #1a2a3b);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--borda);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
    </style>
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
        
        st.markdown("### 🌓 Tema")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Escuro", key="dark_btn"):
                st.session_state.dados['tema'] = "DARK"
                st.rerun()
        with col2:
            if st.button("☀️ Claro", key="light_btn"):
                st.session_state.dados['tema'] = "LIGHT"
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔍 Filtros")
        intervalo = st.select_slider(
            "Período de Análise",
            options=["7 dias", "15 dias", "30 dias", "60 dias"],
            value="30 dias"
        )
        
        st.session_state.dados['velocidade'] = st.slider(
            "Velocidade de atualização", 1, 10, 
            st.session_state.dados['velocidade']
        )
        
        st.markdown("---")
        st.markdown("### 🎛 Controles")
        col1, col2 = st.columns(2)
        with col1:
            if st.button('⏸️ Pausar' if not st.session_state.dados['pausado'] else '▶️ Continuar'):
                st.session_state.dados['pausado'] = not st.session_state.dados['pausado']
        with col2:
            if st.button('🔄 Reiniciar'):
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
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Faturamento</h3>
            <div style="font-size: 1.8em; font-weight: bold; color: {cores['SECUNDARIA']}; margin: 10px 0;">R$ {FATURAMENTO_MENSAL:,.2f}</div>
            <p style="color: {cores['TERCIARIA']}; font-size:0.9em;">+5.2% vs anterior</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Vendas Hoje</h3>
            <div style="font-size: 1.8em; font-weight: bold; color: {cores['SECUNDARIA']}; margin: 10px 0;">{st.session_state.dados['vendas_hoje']}</div>
            <p style="color: {cores['TERCIARIA']}; font-size:0.9em;">+{random.randint(3, 8)}% vs ontem</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Ticket Médio</h3>
            <div style="font-size: 1.8em; font-weight: bold; color: {cores['SECUNDARIA']}; margin: 10px 0;">R$ {st.session_state.dados['ticket_medio']:,.2f}</div>
            <p style="color: {cores['TERCIARIA']}; font-size:0.9em;">{random.choice(['+', '-'])}{random.uniform(0.5, 2.5):.1f}% variação</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {cores['TERCIARIA']}; margin-top:0; font-size:1em;">Conversão</h3>
            <div style="font-size: 1.8em; font-weight: bold; color: {cores['SECUNDARIA']}; margin: 10px 0;">{st.session_state.dados['conversao_total']:.1f}%</div>
            <p style="color: {cores['TERCIARIA']}; font-size:0.9em;">Meta: 85%</p>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos
    st.markdown("---")
    col1, col2 = st.columns([3, 2])
    
    chart1_placeholder = col1.empty()
    chart2_placeholder = col2.empty()
    chart3_placeholder = st.empty()
    vendas_placeholder = st.empty()

    # Loop de atualização
    while True:
        try:
            if not st.session_state.dados['pausado']:
                # Atualizar dados
                for pacote in st.session_state.dados['vendas_atuais']:
                    st.session_state.dados['vendas_atuais'][pacote] = gerar_progressao_vendas(
                        st.session_state.dados['vendas_atuais'][pacote]
                    )
                
                st.session_state.dados['vendas_hoje'] += random.randint(1, 4)
                st.session_state.dados['ticket_medio'] = np.mean([
                    v['Valor'] for v in st.session_state.dados['ultimas_vendas'][-10:] 
                    if st.session_state.dados['ultimas_vendas']
                ] or [PACOTES["GOLD"]["preco"]])
                
                # Gerar nova transação
                nova_venda = gerar_transacao()
                st.session_state.dados['ultimas_vendas'].insert(0, nova_venda)
                st.session_state.dados['ultimas_vendas'] = st.session_state.dados['ultimas_vendas'][:10]
                
                # Notificação compatível
                st.toast(
                    f"{nova_venda['Mensagem']}\n"
                    f"**Valor:** R$ {nova_venda['Valor']:,.2f}\n"
                    f"**Comissão:** R$ {nova_venda['Comissao']:,.2f}",
                    icon="🌶️"
                )
            
            # Atualizar gráficos
            with chart1_placeholder.container():
                st.session_state.dados['fig1'].data[0].y = list(st.session_state.dados['vendas_atuais'].values())
                st.plotly_chart(st.session_state.dados['fig1'], use_container_width=True)
            
            with chart2_placeholder.container():
                df2 = pd.DataFrame([
                    {"Pacote": p, "Tipo": "Meta", "Valor": PACOTES[p]["meta"]} for p in PACOTES
                ] + [
                    {"Pacote": p, "Tipo": "Realizado", "Valor": st.session_state.dados['vendas_atuais'][p]} for p in PACOTES
                ])
                fig2 = px.bar(df2, x="Pacote", y="Valor", color="Pacote",
                             barmode="group", color_discrete_map={k: v["cor"] for k, v in PACOTES.items()})
                st.plotly_chart(fig2, use_container_width=True)
            
            with vendas_placeholder.container():
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">
                        <h3 style="color: {cores['SECUNDARIA']}; margin:0;">🛒 Últimas Vendas</h3>
                        <span style="color: {cores['TERCIARIA']};">{datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                for venda in st.session_state.dados['ultimas_vendas']:
                    st.markdown(f"""
                    <div style="padding:15px; margin:10px 0; border-left:3px solid {venda['Cor']}; background:rgba(24,39,59,0.05);">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <strong>{venda['Nome']}</strong>
                                <div style="color:{cores['TERCIARIA']}; font-size:0.9em;">📍 {venda['Local']}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="color:{venda['Cor']}; font-weight:bold;">{venda['Pacote']}</div>
                                <div>💵 R$ {venda['Valor']:,.2f}</div>
                            </div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:8px; color:{cores['TERCIARIA']};">
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

if __name__ == "__main__":
    main()
