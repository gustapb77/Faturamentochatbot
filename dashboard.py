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
    "PRIMARIA": "#18273b",
    "SECUNDARIA": "#e0c083",
    "TERCIARIA": "#828993",
    "TEXTO": "#ffffff",
    "FUNDO": "#0e1117",
    "CARDS": "#1a2230",
    "DESTAQUE": "#e0c083"
}

FATURAMENTO_MENSAL = 8247358.90

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
LOGO_URL = "https://i.ibb.co/0jQ4Z8T/gold-pepper-logo.png"
LOGO_MINI_URL = "https://i.ibb.co/4Y8LZ9T/gold-pepper-mini.png"  # Logo pequena para notificações

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
    
    if random.random() < 0.07:  # 7% de chance de venda premium
        valor = valor_base * random.uniform(1.5, 3)
        comissao = valor * info["comissao"]
        mensagem = f"Venda Premium!"
        icon = "🚀"
    else:
        valor = valor_base
        mensagem = "Venda Realizada!"
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

# ... (mantenha as outras funções como estão)

# ======================================
# INTERFACE PRINCIPAL
# ======================================
def main():
    # CSS Personalizado
    st.markdown(f"""
    <style>
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
    </style>
    """, unsafe_allow_html=True)
    
    inicializar_dados()
    
    # Barra lateral (mantenha como está)
    
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
    
    # ... (restante do código mantido)

    # ======================================
    # LOOP DE ATUALIZAÇÃO
    # ======================================
    while True:
        try:
            if not st.session_state.dados['pausado']:
                # ... (código de atualização mantido)
                
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
            
            # ... (restante do loop mantido)

if __name__ == "__main__":
    main()
