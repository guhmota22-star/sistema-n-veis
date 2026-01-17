import streamlit as st
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
from database import EQUIPMENT_DB, QUESTS_DB, get_rank_info, get_total_stats

# --- 1. CONFIGURAÇÃO DE INTERFACE & ESTILO ---
st.set_page_config(page_title="SISTEMA: MONARCA", page_icon="🔱", layout="wide")

# Importação da fonte Orbitron e Estilo Avançado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap');

    /* 1. Estilo Global e Fundo com Vinheta */
    .stApp { 
        background: radial-gradient(circle, #0f1218 0%, #050505 100%);
        color: #e0e0e0; 
        font-family: 'Orbitron', sans-serif; 
    }

    /* 2. Scrollbar Estilo Neon */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #050505; }
    ::-webkit-scrollbar-thumb { 
        background: #00d4ff; 
        border-radius: 10px;
        box-shadow: 0 0 10px #00d4ff;
    }

    /* 3. Títulos com Brilho Pulsante */
    h1, h2, h3 { 
        color: #00d4ff; 
        text-shadow: 0 0 12px rgba(0, 212, 255, 0.6);
        text-transform: uppercase; 
        letter-spacing: 3px;
        font-weight: 700;
    }

    /* 4. Customização Épica das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 10px 25px;
        border-radius: 5px 5px 0px 0px;
        color: #888;
        transition: all 0.3s;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 212, 255, 0.15) !important;
        border: 1px solid #00d4ff !important;
        color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
    }

    /* 5. Botões de Ação com Micro-Interações */
    .stButton>button { 
        background: linear-gradient(90deg, rgba(0,212,255,0.1) 0%, rgba(0,212,255,0.02) 100%);
        border: 1px solid #00d4ff; 
        color: #00d4ff; 
        border-radius: 4px;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        font-size: 14px;
    }

    .stButton>button:hover { 
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4); 
        transform: translateY(-2px);
        border-color: #ffffff;
    }

    /* 6. Containers de HUD e Atributos */
    .hud-container {
        border-left: 4px solid #00d4ff;
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 15px;
    }

    /* 7. Cores de Status e Ranks */
    .label-hp { color: #ff4b4b; text-shadow: 0 0 8px rgba(255, 75, 75, 0.5); font-weight: bold; }
    .label-mp { color: #00d4ff; text-shadow: 0 0 8px rgba(0, 212, 255, 0.5); font-weight: bold; }
    .label-xp { color: #ffaa00; }
    .label-coins { color: #ffee00; }

    .rank-e { color: #9e9e9e; } .rank-d { color: #4caf50; } 
    .rank-c { color: #2196f3; } .rank-s { color: #ffcc00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
# --- 2. GESTÃO DE DADOS E LÓGICA DE RANK (SISTEMA DE AKASHA) ---

def get_rank_info(level):
    """Define a aura, a cor e o Título do Monarca baseado no nível"""
    if level < 10: 
        return {"name": "E", "color": "#9e9e9e", "glow": "rgba(158, 158, 158, 0.5)", "title": "Interno Novato"}
    if level < 20: 
        return {"name": "D", "color": "#4caf50", "glow": "rgba(76, 175, 80, 0.5)", "title": "Interno Veterano"}
    if level < 30: 
        return {"name": "C", "color": "#2196f3", "glow": "rgba(33, 150, 243, 0.5)", "title": "Residente Aspirante"}
    if level < 40: 
        return {"name": "B", "color": "#9c27b0", "glow": "rgba(156, 39, 176, 0.5)", "title": "Mestre da Clínica"}
    if level < 50: 
        return {"name": "A", "color": "#ff5722", "glow": "rgba(255, 87, 34, 0.5)", "title": "Monarca Hospitalar"}
    return {"name": "S", "color": "#ffcc00", "glow": "rgba(255, 204, 0, 0.6)", "title": "Soberano da Medicina"}

def get_initial_data():
    """Gera o estado inicial de um Caçador Nível 1"""
    return {
        "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0, "points": 0,
        "last_access": str(datetime.date.today()),
        "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
        "history": []
    }

# Inicialização segura no Session State
if 'data' not in st.session_state:
    st.session_state.data = get_initial_data()

# Recupera informações do Rank e Título atual
rank_info = get_rank_info(st.session_state.data["lvl"])

# --- INJEÇÃO DE AURA DINÂMICA (A MÁGICA DAS CORES) ---
# Este bloco substitui as cores do CSS original pela cor do seu Rank atual!
st.markdown(f"""
    <style>
    h1, h2, h3 {{ color: {rank_info['color']} !important; text-shadow: 0 0 10px {rank_info['glow']} !important; }}
    .stButton>button {{ border-color: {rank_info['color']} !important; color: {rank_info['color']} !important; }}
    .stButton>button:hover {{ background-color: {rank_info['color']} !important; color: black !important; box-shadow: 0 0 20px {rank_info['color']} !important; }}
    div[st-ui="stProgress"] > div > div > div {{ background-color: {rank_info['color']} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE REGENERAÇÃO TEMPORAL (EXCLUSIVO PC) ---
hoje = str(datetime.date.today())
if st.session_state.data.get("last_access") != hoje:
    # Restaura 100% de Mana e 20% de HP por novo ciclo em Diamantina
    st.session_state.data["mp"] = 100 
    st.session_state.data["hp"] = min(100, st.session_state.data["hp"] + 20)
    st.session_state.data["last_access"] = hoje
    st.toast(f"☀️ Ciclo Resetado: Mana 100% | HP +20. Bom plantão, {rank_info['title']}!", icon="🔷")
# --- 3. BARRA LATERAL: REGISTRO DE AKASHA & ID ---

with st.sidebar:
    # 1. Cartão de Identidade Visual (Dinâmico por Rank)
    st.markdown(f"""
        <div style="
            border: 2px solid {rank_info['color']};
            padding: 15px;
            border-radius: 10px;
            background-color: rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 0 15px {rank_info['glow']};
        ">
            <h2 style="color: {rank_info['color']}; margin: 0;">RANK {rank_info['name']}</h2>
            <p style="color: #e0e0e0; font-size: 14px; margin: 5px 0;">{rank_info['title']}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h3 style='color: {rank_info['color']};'>💾 MEMORY CARD</h3>", unsafe_allow_html=True)
    st.caption("Salve seu progresso antes de fechar o portal.")
    
    # Exportar Save (Download do JSON identado para PC)
    data_string = json.dumps(st.session_state.data, indent=4)
    st.download_button(
        label="📥 DESCARREGAR SAVE",
        data=data_string,
        file_name=f"monarca_save_{datetime.date.today()}.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.divider()
    
    # Importar Save
    st.markdown("### 📤 RESTAURAR ESSÊNCIA")
    uploaded_file = st.file_uploader("Upload do fragmento .json", type="json")
    
    if uploaded_file is not None:
        try:
            temp_data = json.load(uploaded_file)
            if "lvl" in temp_data and "stats" in temp_data:
                st.session_state.data = temp_data
                st.success("Sincronização Concluída!")
                st.rerun()
            else:
                st.error("Assinatura Inválida!")
        except Exception as e:
            st.error(f"Erro na restauração: {e}")

    # Espaço Inferior Estilizado
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div style="text-align: center; opacity: 0.6; font-size: 12px;">
            SISTEMA OPERACIONAL: MONARCA v2.0<br>
            AURA ATUAL: <span style="color:{rank_info['color']}">{rank_info['name']}</span>
        </div>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE PROGRESSÃO E EVOLUÇÃO ---

def add_xp(amount, coins, reason):
    # 1. Registro inicial de Rank para comparação
    level_inicial = st.session_state.data["lvl"]
    rank_antigo = get_rank_info(level_inicial)
    
    # 2. Adiciona recompensas básicas
    st.session_state.data["xp"] += amount
    st.session_state.data["coins"] += coins
    
    # Notificação discreta de ganho (Discreta para não poluir o PC)
    st.toast(f"✨ +{amount} XP | 💰 +{coins} Moedas", icon="⚔️")
    
    # 3. Processamento de Level Up com Transbordo
    # Fórmula: $XP_{req} = 100 \times Level^{1.5}$
    while True:
        level_atual = st.session_state.data["lvl"]
        xp_necessario = int(100 * (level_atual ** 1.5))
        
        if st.session_state.data["xp"] >= xp_necessario:
            st.session_state.data["xp"] -= xp_necessario
            st.session_state.data["lvl"] += 1
            st.session_state.data["points"] += 5
            
            # Feedback visual de Level Up
            st.balloons()
            st.success(f"🎊 NÍVEL UP! VOCÊ ALCANÇOU O NÍVEL {st.session_state.data['lvl']}!")
        else:
            break
            
    # 4. Verificação de Evolução de Rank e Título
    rank_novo = get_rank_info(st.session_state.data["lvl"])
    
    if rank_novo["name"] != rank_antigo["name"]:
        # Mensagem épica usando a cor do novo Rank
        st.markdown(f"""
            <div style="
                border: 2px solid {rank_novo['color']};
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(0,0,0,0.5);
                text-align: center;
                margin-top: 10px;
                box-shadow: 0 0 15px {rank_novo['glow']};
            ">
                <h3 style="color: {rank_novo['color']}; margin: 0;">⚠️ RANK UP!</h3>
                <p style="margin: 5px 0;">Você agora é um <b>{rank_novo['title']}</b> de <b>RANK {rank_novo['name']}</b></p>
            </div>
        """, unsafe_allow_html=True)
    
    # 5. Registro no Histórico (Limitado para manter o save leve)
    timestamp = datetime.datetime.now().strftime('%d/%m %H:%M')
    st.session_state.data["history"].append(f"{timestamp} - {reason} (+{amount} XP)")
    if len(st.session_state.data["history"]) > 50:
        st.session_state.data["history"].pop(0)
        
# --- 5. HUD DO MONARCA (VISUALIZADOR DE STATUS) ---

# Título com a cor dinâmica do Rank atual
st.markdown(f"""
    <h1 style='color: {rank_info['color']}; text-shadow: 0 0 15px {rank_info['glow']}; text-align: center;'>
        🔱 JANELA DE STATUS: {st.session_state.data.get('name', 'GUH MOTA')}
    </h1>
""", unsafe_allow_html=True)

# Container do HUD
with st.container():
    c_hud1, c_hud2, c_hud3 = st.columns([1.2, 1, 1.2])
    
    with c_hud1:
        # Aqui usamos o rank_info que já foi definido na Parte 2
        st.markdown(f"### <span style='color:{rank_info['color']}'>RANK {rank_info['name']}</span> | NÍVEL {st.session_state.data['lvl']}", unsafe_allow_html=True)
        st.caption(f"🛡️ Título: {rank_info['title']}")
        
        # Status de Vida e Energia
        st.markdown(f"<span class='label-hp'>❤️ HP: {st.session_state.data['hp']}/100</span>", unsafe_allow_html=True)
        st.progress(st.session_state.data['hp'] / 100)
        
        st.markdown(f"<span class='label-mp'>🔷 MP: {st.session_state.data['mp']}/100</span>", unsafe_allow_html=True)
        st.progress(st.session_state.data['mp'] / 100)

    with c_hud2:
        st.markdown("### RECOMPENSAS")
        xp_atual = st.session_state.data['xp']
        xp_needed = int(100 * (st.session_state.data['lvl'] ** 1.5))
        
        st.markdown(f"<span class='label-xp'>✨ XP: {xp_atual}/{xp_needed}</span>", unsafe_allow_html=True)
        st.progress(min(xp_atual / xp_needed, 1.0))
        
        st.markdown(f"<span class='label-coins'>💰 MOEDAS: {st.session_state.data['coins']}</span>", unsafe_allow_html=True)
        st.caption("Modo Offline: Registro Local")

    with c_hud3:
        # Gráfico de Radar Atualizado
        labels = list(st.session_state.data["stats"].keys())
        values = list(st.session_state.data["stats"].values())
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            line_color=rank_info['color'], # Linha na cor do Rank!
            fillcolor=rank_info['glow']     # Preenchimento com brilho do Rank!
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 50])),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=200,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()

# --- 6. ABAS DO SISTEMA (AÇÃO, ESTRATÉGIA E ARSENAL) ---

# 0. Prepara os dados dinâmicos do Monarca
stats_totais, hp_bonus = get_total_stats(st.session_state.data)

# 1. Definição das Abas (Agora com 5 abas para total controle)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗡️ QUESTS", "📊 STATUS", "🎒 INVENTÁRIO", "🛒 MERCADO", "📜 LOG"])

with tab1:
    st.markdown(f"### ⚔️ DAILY QUESTS (RANK {rank_info['name']})")
    
    # LÓGICA DE BÔNUS PASSIVOS
    mp_red = 0; xp_boost = 0; coin_boost = 0
    for slot, item_name in st.session_state.data["equipped"].items():
        if item_name in EQUIPMENT_DB:
            item = EQUIPMENT_DB[item_name]
            mp_red += item.get("mp_reduction", 0)
            xp_boost += item.get("xp_mult", 0)
            coin_boost += item.get("coin_mult", 0)

    # Função de Execução de Missão com suporte a bônus
    def run_quest(cost, str_g, int_g, agi_g, vit_g, cha_g, sen_g, xp, coins, msg):
        final_cost = max(0, cost - mp_red) if int_g > 0 else cost
        if st.session_state.data["mp"] >= final_cost:
            st.session_state.data["mp"] -= final_cost
            # Evolução de Atributos Base
            st.session_state.data["stats"]["STR"] += str_g
            st.session_state.data["stats"]["INT"] += int_g
            st.session_state.data["stats"]["AGI"] += agi_g
            st.session_state.data["stats"]["VIT"] += vit_g
            st.session_state.data["stats"]["CHA"] += cha_g
            st.session_state.data["stats"]["SEN"] += sen_g
            # XP e Coins com bônus de itens
            final_xp = int(xp * (1 + xp_boost))
            final_coins = int(coins * (1 + coin_boost))
            add_xp(final_xp, final_coins, msg)
            st.rerun()
        else:
            st.error(f"Mana Insuficiente! Falta {final_cost - st.session_state.data['mp']} MP.")

    # GRID DE MISSÕES DINÂMICO (3 colunas automáticas)
    cols = st.columns(3)
    for i, quest in enumerate(QUESTS_DB):
        with cols[i % 3]:
            # Exibe o custo real (com desconto se houver)
            custo_real = max(0, quest['cost'] - mp_red) if quest['stats'].get('INT', 0) > 0 else quest['cost']
            st.markdown(f"<div class='quest-card'>{quest['label']}<br><small>{custo_real} MP</small></div>", unsafe_allow_html=True)
            if st.button("EXECUTAR", key=quest['id'], use_container_width=True):
                run_quest(quest['cost'], 
                          quest['stats'].get('STR', 0), quest['stats'].get('INT', 0), 
                          quest['stats'].get('AGI', 0), quest['stats'].get('VIT', 0), 
                          quest['stats'].get('CHA', 0), quest['stats'].get('SEN', 0), 
                          quest['xp'], quest['coins'], quest['msg'])

    st.divider()
    if st.button("💤 SONO REPARADOR", use_container_width=True):
        st.session_state.data["hp"] = 100 + hp_bonus
        st.session_state.data["mp"] = 100
        st.rerun()

with tab2:
    st.markdown("### 📊 STATUS REAIS (BASE + EQUIPAMENTOS)")
    for stat, total_val in stats_totais.items():
        base = st.session_state.data["stats"][stat]
        bonus = total_val - base
        bonus_color = rank_info['color'] if bonus > 0 else "white"
        st.markdown(f"**{stat}**: {base} <span style='color:{bonus_color}'>(+{bonus})</span> → **{total_val}**", unsafe_allow_html=True)
    
    if st.session_state.data["points"] > 0:
        st.info(f"Você tem {st.session_state.data['points']} pontos para distribuir.")

with tab3:
    st.markdown("### 🎒 INVENTÁRIO ATIVO")
    for slot, item_name in st.session_state.data["equipped"].items():
        col1, col2 = st.columns([3, 1])
        status = item_name if item_name else "Vazio"
        col1.write(f"**{slot.upper()}**: {status}")
        if item_name and col2.button("RETIRAR", key=f"uneq_{slot}"):
            st.session_state.data["equipped"][slot] = None
            st.rerun()
    
    st.divider()
    st.markdown("#### Itens Disponíveis")
    for item in st.session_state.data["inventory"]:
        if item not in st.session_state.data["equipped"].values():
            if st.button(f"EQUIPAR {item}", use_container_width=True):
                slot = EQUIPMENT_DB[item]["slot"]
                st.session_state.data["equipped"][slot] = item
                st.rerun()

with tab4:
    st.markdown("### 🛒 INVESTIMENTOS DISPONÍVEIS")
    for name, info in EQUIPMENT_DB.items():
        if name not in st.session_state.data["inventory"]:
            with st.expander(f"📦 {name} (200 moedas)"):
                st.write(info["desc"])
                if st.button(f"ADQUIRIR {name}", key=f"buy_{name}"):
                    if st.session_state.data["coins"] >= 200:
                        st.session_state.data["coins"] -= 200
                        st.session_state.data["inventory"].append(name)
                        st.rerun()
                    else: st.error("Moedas insuficientes.")

with tab5:
    st.markdown("### 📜 REGISTROS DE AKASHA")
    for log in reversed(st.session_state.data["history"][-15:]):
        st.write(f"🛡️ {log}")
