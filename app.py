import streamlit as st
import json
import datetime
import pandas as pd
import plotly.graph_objects as go

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

# --- 2. GESTÃO DE DADOS E LÓGICA DE RANK (SISTEMA DE AKASHA v2.0) ---

# 1. Banco de Dados de Equipamentos
EQUIPMENT_DB = {
    "Assinatura de Banco de Questões": {"slot": "head", "bonus_int": 2, "xp_mult": 0.15, "desc": "+15% XP em Estudos"},
    "Tênis de Plantão": {"slot": "body", "hp_max": 20, "desc": "+20 HP Máximo"},
    "Estetoscóscope de Elite": {"slot": "hands", "bonus_sen": 5, "desc": "+5 Percepção Clínica"},
    "Cinto de LPO / Straps": {"slot": "hands", "bonus_str": 5, "desc": "+5 Força nos Treinos"},
    "Manual de Condutas": {"slot": "accessory", "mp_reduction": 5, "desc": "-5 MP de custo em INT"},
    "Smartwatch Pro": {"slot": "accessory", "coin_mult": 0.10, "desc": "+10% Moedas ganhas"}
}

# 2. Conquistas em Tiers
ACHIEVEMENTS_DB = {
    "Anki I (7 dias)": {"streak_req": 7, "quest_id": "anki", "mp_bonus": 5, "desc": "+5 MP Máximo"},
    "Anki II (21 dias)": {"streak_req": 21, "quest_id": "anki", "mp_bonus": 15, "desc": "+15 MP Máximo"},
    "Anki III (50 dias)": {"streak_req": 50, "quest_id": "anki", "mp_bonus": 30, "desc": "+30 MP e -5% Custo INT"},
    "Dieta I (7 dias)": {"streak_req": 7, "quest_id": "dieta", "hp_bonus": 5, "desc": "+5 HP Máximo"},
    "Dieta II (14 dias)": {"streak_req": 14, "quest_id": "dieta", "hp_bonus": 10, "desc": "+10 HP Máximo"},
    "Dieta III (30 dias)": {"streak_req": 30, "quest_id": "dieta", "hp_bonus": 20, "desc": "+20 HP e -5% Custo Físico"},
    "Disciplina de Ferro": {"streak_req": 7, "title": "O Inabalável", "desc": "Mantenha a Trifeta por 7 dias"}
}

# 3. Contratos Reais
DEFAULT_REAL_REWARDS = [
    {"id": "rank_c", "name": "Scrub Premium ou Esteto Novo", "type": "lvl", "req": 20, "status": "Bloqueado"},
    {"id": "mestria_int", "name": "Livro/Curso de Residência", "type": "stat", "target": "INT", "req": 50, "status": "Bloqueado"},
    {"id": "forca_str", "name": "Acessório de Elite (Cinto LPO/Straps)", "type": "stat", "target": "STR", "req": 50, "status": "Bloqueado"},
    {"id": "resiliencia", "name": "Final de Semana de Descanso Total", "type": "streak", "req": 21, "status": "Bloqueado"},
    {"id": "tesouro", "name": "Jantar no Restaurante Favorito", "type": "coins", "req": 5000, "status": "Bloqueado"}
]

# 4. Funções de Suporte (Rank e XP)
def get_rank_info(level):
    if level < 8: return {"name": "E", "color": "#9e9e9e", "glow": "rgba(158, 158, 158, 0.5)", "title": "Interno Novato"}
    if level < 16: return {"name": "D", "color": "#4caf50", "glow": "rgba(76, 175, 80, 0.5)", "title": "Interno Veterano"}
    if level < 24: return {"name": "C", "color": "#2196f3", "glow": "rgba(33, 150, 243, 0.5)", "title": "Residente Aspirante"}
    if level < 32: return {"name": "B", "color": "#9c27b0", "glow": "rgba(156, 39, 176, 0.5)", "title": "Mestre da Clínica"}
    if level < 40: return {"name": "A", "color": "#ff5722", "glow": "rgba(255, 87, 34, 0.5)", "title": "Monarca Hospitalar"}
    return {"name": "S", "color": "#ffcc00", "glow": "rgba(255, 204, 0, 0.6)", "title": "Soberano do Trauma"}

def get_xp_needed(lvl):
    return 100 + (lvl * 30)

# --- NOVA ADIÇÃO: FUNÇÕES DE STREAK (CORREÇÃO DO NAMEERROR) ---
def update_quest_streak(quest_id):
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    if "streaks" not in st.session_state.data: st.session_state.data["streaks"] = {}
    
    if quest_id not in st.session_state.data["streaks"]:
        st.session_state.data["streaks"][quest_id] = {"count": 1, "last_date": str(hoje)}
        return 1
    
    streak_data = st.session_state.data["streaks"][quest_id]
    last_date = datetime.datetime.strptime(streak_data["last_date"], "%Y-%m-%d").date()
    
    if last_date == ontem:
        streak_data["count"] += 1
        streak_data["last_date"] = str(hoje)
    elif last_date < ontem:
        streak_data["count"] = 1
        streak_data["last_date"] = str(hoje)
    return streak_data["count"]

def get_streak_multiplier(quest_id):
    count = st.session_state.data.get("streaks", {}).get(quest_id, {}).get("count", 0)
    if count >= 3: return min(0.50, (count - 2) * 0.05)
    return 0.0

def get_total_stats():
    hp_extra = (st.session_state.data["lvl"] - 1) * 8
    mp_extra = 0
    base = {s: round(v, 1) for s, v in st.session_state.data["stats"].items()}
    equipped = st.session_state.data["equipped"]
    for slot, item_name in equipped.items():
        if item_name in EQUIPMENT_DB:
            item = EQUIPMENT_DB[item_name]
            for stat in base: base[stat] += item.get(f"bonus_{stat.lower()}", 0)
            hp_extra += item.get("hp_max", 0)
    for ach_name, ach_info in ACHIEVEMENTS_DB.items():
        if ach_name in st.session_state.data.get("achievements", []):
            hp_extra += ach_info.get("hp_bonus", 0)
            mp_extra += ach_info.get("mp_bonus", 0)
    mp_max_calc = round(100 + (base["INT"] - 10) * 5 + mp_extra, 1)
    hp_max_total = round(100 + hp_extra, 1)
    return base, hp_max_total, mp_max_calc

# 5. Inicialização e Reparo
def get_initial_data():
    return {
        "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0, "points": 0,
        "last_access": str(datetime.date.today()),
        "rodizio": "Urgência e Emergência",
        "punishment_counter": 10,
        "daily_trifeta": {"med": False, "phys": False, "log": False},
        "investment_funds": {"Medicina": 0, "Treino": 0, "Ordem": 0},
        "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
        "inventory": [], "equipped": {"head": None, "body": None, "hands": None, "accessory": None},
        "achievements": [], "active_title": None, "history": [], "streaks": {},
        "real_rewards": DEFAULT_REAL_REWARDS
    }

if 'data' not in st.session_state:
    st.session_state.data = get_initial_data()
else:
    patch = {"punishment_counter": 10, "daily_trifeta": {"med": False, "phys": False, "log": False}, 
             "investment_funds": {"Medicina": 0, "Treino": 0, "Ordem": 0}, "real_rewards": DEFAULT_REAL_REWARDS, "streaks": {}}
    for key, val in patch.items():
        if key not in st.session_state.data: st.session_state.data[key] = val

# 6. Virada de Dia
hoje = str(datetime.date.today())
if st.session_state.data["last_access"] != hoje:
    t = st.session_state.data["daily_trifeta"]
    if not (t["med"] and t["phys"] and t["log"]):
        st.session_state.data["punishment_counter"] += 5
    st.session_state.data["daily_trifeta"] = {"med": False, "phys": False, "log": False}
    st.session_state.data["last_access"] = hoje

rank_info = get_rank_info(st.session_state.data["lvl"])
stats_totais, hp_max_total, mp_max_total = get_total_stats()

# Estilos de Aura
st.markdown(f"<style>h1, h2, h3 {{ color: {rank_info['color']} !important; text-shadow: 0 0 10px {rank_info['glow']} !important; }}</style>", unsafe_allow_html=True)

# --- 3. BARRA LATERAL: REGISTRO DE AKASHA & ID ---

with st.sidebar:
    # 1. Cartão de Identidade Visual (Dinâmico por Rank e Rodízio)
    # Exibe o rodízio atual (Urgência e Emergência) para imersão total
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
            <p style="color: #e0e0e0; font-size: 14px; margin: 5px 0; font-weight: bold;">{rank_info['title']}</p>
            <div style="
                font-size: 10px; 
                text-transform: uppercase; 
                letter-spacing: 1px; 
                color: {rank_info['color']}; 
                margin-top: 8px; 
                border-top: 1px solid rgba(255,255,255,0.1); 
                padding-top: 5px;
            ">
                🌍 {st.session_state.data.get('rodizio', 'Urgência e Emergência')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h3 style='color: {rank_info['color']};'>💾 MEMORY CARD</h3>", unsafe_allow_html=True)
    st.caption("Salve sua essência antes de fechar o portal.")
    
    # Exportar Save (Download do JSON identado para PC)
    # O arquivo agora leva o nome do Monarca v2.0
    data_string = json.dumps(st.session_state.data, indent=4)
    st.download_button(
        label="📥 DESCARREGAR SAVE",
        data=data_string,
        file_name=f"monarca_v2_save_{datetime.date.today()}.json",
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
            # Verificação de integridade mínima
            if "lvl" in temp_data and "stats" in temp_data:
                st.session_state.data = temp_data
                st.success("Sincronização Concluída!")
                st.rerun()
            else:
                st.error("Assinatura de Save Inválida!")
        except Exception as e:
            st.error(f"Erro na restauração: {e}")

    # Espaço Inferior Estilizado com Versão do Sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div style="text-align: center; opacity: 0.6; font-size: 12px;">
            SISTEMA OPERACIONAL: <b>MONARCA v2.0</b><br>
            RODÍZIO: {st.session_state.data.get('rodizio', 'Urgência')}<br>
            AURA ATUAL: <span style="color:{rank_info['color']}">{rank_info['name']}</span>
        </div>
    """, unsafe_allow_html=True)
    
# --- 4. LÓGICA DE PROGRESSÃO E EVOLUÇÃO ---

def add_xp(amount, coins, reason):
    # 1. Registro inicial para comparação de Rank
    level_inicial = st.session_state.data["lvl"]
    rank_antigo = get_rank_info(level_inicial)
    
    # 2. Verificação de Dívida de Sangue (Punição Física)
    # Se o contador for maior que 10, você ganha 50% menos recompensas
    penalty_active = st.session_state.data.get("punishment_counter", 10) > 10
    
    final_amount = int(amount * 0.5) if penalty_active else amount
    final_coins = int(coins * 0.5) if penalty_active else coins
    
    # 3. Adiciona recompensas calibradas
    st.session_state.data["xp"] += final_amount
    st.session_state.data["coins"] += final_coins
    
    # Notificação de ganho com alerta de penalidade
    msg_bonus = " (⚠️ PENALIDADE ATIVA -50%)" if penalty_active else ""
    st.toast(f"✨ +{final_amount} XP | 💰 +{final_coins} Moedas{msg_bonus}", icon="⚔️")
    
    # 4. Processamento de Level Up com Transbordo
    # Agora usa a função get_xp_needed() definida na Parte 2 (Progressão Linear)
    while True:
        level_atual = st.session_state.data["lvl"]
        xp_necessario = get_xp_needed(level_atual)
        
        if st.session_state.data["xp"] >= xp_necessario:
            st.session_state.data["xp"] -= xp_necessario
            st.session_state.data["lvl"] += 1
            st.session_state.data["points"] += 5
            
            # Feedback visual de Level Up
            st.balloons()
            st.success(f"🎊 NÍVEL UP! VOCÊ ALCANÇOU O NÍVEL {st.session_state.data['lvl']}!")
        else:
            break
            
    # 5. Verificação de Evolução de Rank
    rank_novo = get_rank_info(st.session_state.data["lvl"])
    
    if rank_novo["name"] != rank_antigo["name"]:
        st.markdown(f"""
            <div style="
                border: 2px solid {rank_novo['color']};
                padding: 15px;
                border-radius: 10px;
                background-color: rgba(0,0,0,0.6);
                text-align: center;
                margin-top: 15px;
                box-shadow: 0 0 20px {rank_novo['glow']};
            ">
                <h2 style="color: {rank_novo['color']}; margin: 0;">⚠️ RANK UP ABSOLUTO!</h2>
                <p style="margin: 5px 0; font-size: 18px;">
                    Evolução: <b>RANK {rank_antigo['name']}</b> ➔ <b>RANK {rank_novo['name']}</b>
                </p>
                <p style="opacity: 0.8;">{rank_novo['title']} de Urgência e Emergência</p>
            </div>
        """, unsafe_allow_html=True)
    
    # 6. Registro no Histórico de Akasha
    timestamp = datetime.datetime.now().strftime('%d/%m %H:%M')
    log_entry = f"{timestamp} - {reason} (+{final_amount} XP)"
    if penalty_active: log_entry += " [PENALIZADO]"
    
    st.session_state.data["history"].append(log_entry)
    if len(st.session_state.data["history"]) > 50:
        st.session_state.data["history"].pop(0)
        
# --- 5. HUD DO MONARCA (VISUALIZADOR DE STATUS) ---

# Título dinâmico com o Rodízio Atual
st.markdown(f"""
    <h1 style='color: {rank_info['color']}; text-shadow: 0 0 15px {rank_info['glow']}; text-align: center;'>
        🔱 STATUS: {st.session_state.data.get('name', 'GUH MOTA')}
    </h1>
    <p style='text-align: center; opacity: 0.7; font-size: 14px; margin-top: -15px;'>
        INTERNATO: {st.session_state.data.get('rodizio', 'Urgência e Emergência')}
    </p>
""", unsafe_allow_html=True)

# Container do HUD
with st.container():
    c_hud1, c_hud2, c_hud3 = st.columns([1.2, 1, 1.3])
    
    with c_hud1:
        st.markdown(f"### <span style='color:{rank_info['color']}'>RANK {rank_info['name']}</span> | NÍVEL {st.session_state.data['lvl']}", unsafe_allow_html=True)
        
        titulo_exibido = st.session_state.data.get("active_title") or rank_info['title']
        st.caption(f"🛡️ Título: {titulo_exibido}")
        
        # HP Persistente (Calculado na Parte 2)
        hp_atual = round(st.session_state.data['hp'], 1)
        st.markdown(f"<span class='label-hp'>❤️ HP: {hp_atual}/{hp_max_total}</span>", unsafe_allow_html=True)
        st.progress(min(hp_atual / hp_max_total, 1.0))
        
        # MP Persistente (Calculado na Parte 2)
        mp_atual = round(st.session_state.data['mp'], 1)
        st.markdown(f"<span class='label-mp'>🔷 MP: {mp_atual}/{mp_max_total}</span>", unsafe_allow_html=True)
        st.progress(min(mp_atual / mp_max_total, 1.0))

    with c_hud2:
        st.markdown("### PROGRESSÃO")
        
        # XP Linear (Nova Lógica 2.0)
        xp_atual = round(st.session_state.data['xp'], 1)
        xp_needed = get_xp_needed(st.session_state.data['lvl'])
        
        st.markdown(f"<span class='label-xp'>✨ XP: {xp_atual}/{xp_needed}</span>", unsafe_allow_html=True)
        st.progress(min(xp_atual / xp_needed, 1.0))
        
        moedas = round(st.session_state.data['coins'], 1)
        st.markdown(f"<span class='label-coins'>💰 MOEDAS: {moedas}</span>", unsafe_allow_html=True)
        st.caption("Foco: Urgência e Emergência")

    with c_hud3:
        # Radar de Atributos Totais (Com bônus de itens e conquistas)
        attr_nomes = {
            "STR": "FORÇA", "INT": "INTELIGÊNCIA", "AGI": "AGILIDADE", 
            "VIT": "VITALIDADE", "CHA": "CARISMA", "SEN": "PERCEPÇÃO"
        }
        
        labels = [attr_nomes.get(s, s) for s in stats_totais.keys()]
        values = [round(v, 1) for v in stats_totais.values()]
        
        l_plot = labels + [labels[0]]
        v_plot = values + [values[0]]
        
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=v_plot,
            theta=l_plot,
            fill='toself',
            line=dict(color=rank_info['color'], width=3),
            fillcolor=rank_info['glow'],
            marker=dict(color=rank_info['color'], size=8),
            hoverinfo='r+theta'
        ))
        
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, 
                    range=[0, max(values) + 10],
                    showticklabels=False,
                    gridcolor="rgba(255,255,255,0.1)"
                ),
                angularaxis=dict(
                    gridcolor="rgba(255,255,255,0.1)",
                    linecolor="rgba(255,255,255,0.2)",
                    tickfont=dict(size=10, color="#ddd", family="Courier New"),
                    rotation=90,
                    direction="clockwise"
                )
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=320,
            margin=dict(t=50, b=50, l=70, r=70), 
            showlegend=False,
            autosize=True
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()

# --- 6. ABAS DO SISTEMA (AÇÃO, ESTRATÉGIA E GLÓRIA) ---

# 1. Recuperação de Bônus e Arredondamento Tático
mp_red = round(0, 1)
xp_boost = round(0, 1)
coin_boost = round(0, 1)
unlocked = st.session_state.data["achievements"]

for slot, item_name in st.session_state.data["equipped"].items():
    if item_name in EQUIPMENT_DB:
        item = EQUIPMENT_DB[item_name]
        mp_red += item.get("mp_reduction", 0)
        xp_boost += item.get("xp_mult", 0)
        coin_boost += item.get("coin_mult", 0)

# Bônus passivo de Tier (Anki I, II ou III)
if any("Anki" in ach for ach in unlocked): xp_boost += 0.05
if "Voz de Paciente" in unlocked: coin_boost += 0.10

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗡️ QUESTS", "📊 STATUS", "🎒 ARSENAL", "🏆 CONQUISTAS", "💎 CONTRATOS", "💰 INVESTIMENTOS", "📜 LOGS"
])

with tab1:
    # Widget de Monitoramento da Trifeta Diária
    t = st.session_state.data["daily_trifeta"]
    status_color = "#4caf50" if all(t.values()) else "#ff4b4b"
    
    st.markdown(f"""
        <div style='background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; border: 1px solid {status_color}; margin-bottom: 20px;'>
            <h4 style='margin:0; color:{status_color}; text-shadow: 0 0 10px {status_color};'>🛡️ ESTADO DE DISCIPLINA</h4>
            <div style='display: flex; gap: 15px; margin-top: 10px; font-weight: bold;'>
                <span style='color: {"#4caf50" if t["med"] else "#555"}'>{'✅' if t["med"] else '⭕'} Medicina</span>
                <span style='color: {"#4caf50" if t["phys"] else "#555"}'>{'✅' if t["phys"] else '⭕'} Física</span>
                <span style='color: {"#4caf50" if t["log"] else "#555"}'>{'✅' if t["log"] else '⭕'} Logística</span>
            </div>
            <div style='font-size: 13px; margin-top: 12px; color: #888; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px;'>
                <b>Dívida de Sangue Pendente:</b> {st.session_state.data["punishment_counter"]} Repetições / {st.session_state.data["punishment_counter"]} min
                <br><small>(Flexão, Abdominal e Corrida)</small>
            </div>
        </div>
    """, unsafe_allow_html=True)

    def run_quest(quest_id, mp_cost, hp_cost, str_g, int_g, agi_g, vit_g, cha_g, sen_g, xp, coins, msg, category=None):
        final_mp_cost = round(max(0, mp_cost - mp_red) if int_g > 0 else mp_cost, 1)
        is_healing = hp_cost < 0
        
        # Lógica de sobrevivência (HP e MP não resetam mais sozinhos)
        if is_healing:
            can_execute = st.session_state.data["mp"] >= final_mp_cost
        else:
            can_execute = st.session_state.data["mp"] >= final_mp_cost and st.session_state.data["hp"] > hp_cost

        if can_execute:
            streak_count = update_quest_streak(quest_id)
            s_mult = get_streak_multiplier(quest_id)
            
            # Marca progresso na Trifeta se houver categoria
            if category: st.session_state.data["daily_trifeta"][category] = True
            
            st.session_state.data["mp"] -= final_mp_cost
            if is_healing:
                st.session_state.data["hp"] = min(hp_max_total, st.session_state.data["hp"] + abs(hp_cost))
            else:
                st.session_state.data["hp"] -= hp_cost
            
            stats = st.session_state.data["stats"]
            stats["STR"] += str_g; stats["INT"] += int_g; stats["AGI"] += agi_g
            stats["VIT"] += vit_g; stats["CHA"] += cha_g; stats["SEN"] += sen_g
            
            total_multiplier = xp_boost + s_mult
            final_xp = int(xp * (1 + total_multiplier))
            final_coins = int(coins * (1 + coin_boost))
            
            feedback = f"{msg} | Streak: 🔥{streak_count}"
            if hp_cost != 0: feedback += f" | ❤️ {'+' if is_healing else '-'}{abs(hp_cost)} HP"
            
            add_xp(final_xp, final_coins, feedback)
            st.rerun()
        else:
            st.error("HP ou MP Insuficiente! Execute uma missão de cura ou use o Sono Reparador.")

    def quest_card(quest_id, label, subtext, key, mp_c, hp_c, s_g, i_g, a_g, v_g, c_g, sn_g, xp_b, coin_b, desc, cat=None):
        streak = st.session_state.data["streaks"].get(quest_id, {}).get("count", 0)
        aura_class = "streak-aura" if streak >= 3 else ""
        flame = f" <span style='color:#ff4b4b;'>🔥{streak}</span>" if streak > 0 else ""
        hp_icon = "💚" if hp_c < 0 else "❤️"
        hp_display = f" | {hp_icon} {abs(hp_c)}" if hp_c != 0 else ""
        
        st.markdown(f"""
            <div class='quest-card {aura_class}'>
                <strong>{label}</strong>{flame}<br>
                <small>{subtext}{hp_display}</small>
            </div>
        """, unsafe_allow_html=True)
        if st.button("EXECUTAR", key=key, use_container_width=True):
            run_quest(quest_id, mp_c, hp_c, s_g, i_g, a_g, v_g, c_g, sn_g, xp_b, coin_b, desc, cat)

    # --- GRID DE MISSÕES RECALIBRADO ---
    st.write("🚑 **URGÊNCIA & ACADÊMICO**")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1: quest_card("anki", "🧠 ANKI", "10 MP", "q_anki", 10, 0, 0, 0.5, 0, 0, 0, 0, 25, 10, "Cards", "med")
    with r1c2: quest_card("est", "📖 ESTUDO", "15 MP", "q_est", 15, 0, 0, 0.5, 0, 0, 0, 0, 25, 12, "Teoria", "med")
    with r1c3: quest_card("plantao", "🚑 PLANTÃO PS", "30 MP | ❤️ 30", "q_plantao", 30, 30, 0, 0, 0, 0, 0, 0.8, 60, 30, "Emergência", "med")
    with r1c4: quest_card("acad", "🎓 ACADÊMICO", "20 MP | ❤️ 5", "q_acad", 20, 5, 0, 0.7, 0, 0, 0, 0.2, 35, 15, "Aulas", "med")

    st.write("💪 **PROJETO ATLETA**")
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1: quest_card("musc", "🏋️ MUSCULAÇÃO", "20 MP | ❤️ 15", "q_musc", 20, 15, 0.6, 0, 0, 0, 0, 0, 30, 15, "Treino", "phys")
    with r2c2: quest_card("fut", "⚽ FUTEBOL", "20 MP | ❤️ 20", "q_fut", 20, 20, 0.3, 0, 0.5, 0, 0, 0, 40, 20, "Partida", "phys")
    with r2c3: quest_card("dieta", "🥗 DIETA", "0 MP | 💚 10", "q_dieta", 0, -10, 0, 0, 0, 0.3, 0, 0, 20, 10, "Nutrição", "phys")
    with r2c4: quest_card("desc", "🛌 DESCANSO", "0 MP | 💚 15", "q_desc", 0, -15, 0, 0, 0, 0.3, 0, 0, 15, 5, "Rest Day", "phys")

    st.write("🧹 **LOGÍSTICA DIAMANTINA**")
    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1: quest_card("louca", "🍽️ LOUÇA", "5 MP", "q_louca", 5, 0, 0, 0, 0.2, 0, 0, 0, 10, 5, "Cozinha", "log")
    with r3c2: quest_card("limp", "🧹 LIMPEZA", "10 MP", "q_limp", 10, 0, 0, 0, 0.3, 0, 0, 0, 15, 8, "Ambiente", "log")
    with r3c3: quest_card("org", "📋 ORGANIZA.", "5 MP", "q_org", 5, 0, 0, 0, 0.3, 0, 0, 0, 10, 5, "Ordem", "log")
    with r3c4: quest_card("coz", "👨‍🍳 COZINHAR", "10 MP", "q_coz", 10, 0, 0, 0, 0.3, 0, 0, 0.2, 15, 10, "Logística", "log")

    st.write("✨ **AUTOCUIDADO & MENTE**")
    r4c1, r4c2, r4c3, r4c4 = st.columns(4)
    with r4c1: quest_card("medica", "💊 MEDICAÇÃO", "0 MP | 💚 15", "q_medica", 0, -15, 0, 0, 0, 0.2, 0, 0, 10, 5, "Cura")
    with r4c2: quest_card("leit", "📚 LEITURA", "5 MP", "q_leit", 5, 0, 0, 0.2, 0, 0, 0, 0.2, 15, 8, "Hábito")
    with r4c3: quest_card("fono", "🗣️ FONO", "10 MP", "q_fono", 10, 0, 0, 0, 0, 0, 0.5, 0, 20, 10, "Vocal")
    with r4c4: quest_card("xadrez", "♟️ XADREZ", "10 MP", "q_xadrez", 10, 0, 0, 0.4, 0, 0, 0, 0.2, 20, 10, "Estratégia")

    st.divider()
    col_p, col_s = st.columns(2)
    with col_p:
        if st.button("🔴 PAGAR PUNIÇÃO FÍSICA", use_container_width=True):
            st.session_state.data["punishment_counter"] = 10
            st.toast(f"Dívida Paga! Próximo contador: 10.", icon="💪")
            st.rerun()
    with col_s:
        if st.button("💤 SONO REPARADOR (RESET)", use_container_width=True):
            st.session_state.data["hp"] = hp_max_total
            st.session_state.data["mp"] = mp_max_total
            st.toast("Recuperação Total Completa!", icon="🌙")
            st.rerun()

with tab2:
    st.markdown(f"### 📊 FICHA TÉCNICA (RODÍZIO: {st.session_state.data['rodizio']})")
    attr_map = {"STR": "💪 Força", "INT": "🧠 Inteligência", "AGI": "⚡ Agilidade", "VIT": "🩸 Vitalidade", "CHA": "🗣️ Carisma", "SEN": "👁️ Percepção"}
    c1, c2 = st.columns(2)
    for i, (stat, name) in enumerate(attr_map.items()):
        val = stats_totais[stat]
        (c1 if i < 3 else c2).metric(name, f"{val:.1f}")
    if st.session_state.data["points"] > 0:
        st.success(f"✨ PONTOS PARA DISTRIBUIR: {st.session_state.data['points']}")
        cols = st.columns(6)
        for i, stat in enumerate(attr_map.keys()):
            if cols[i].button(f"+{stat}", key=f"up_{stat}"):
                st.session_state.data["stats"][stat] += 1
                st.session_state.data["points"] -= 1
                st.rerun()

with tab3:
    st.markdown("### 🎒 ARSENAL EQUIPADO")
    if not st.session_state.data["inventory"]:
        st.info("Arsenal vazio. Invista no Hub para ganhar equipamentos.")
    else:
        for item in st.session_state.data["inventory"]:
            col1, col2 = st.columns([4, 1])
            slot = EQUIPMENT_DB[item]["slot"]
            is_eq = st.session_state.data["equipped"].get(slot) == item
            col1.write(f"**{item}** | {EQUIPMENT_DB[item]['desc']}")
            if col2.button("EQUIPAR" if not is_eq else "REMOVER", key=f"inv_{item}"):
                st.session_state.data["equipped"][slot] = None if is_eq else item
                st.rerun()

with tab4:
    st.markdown("### 🏆 GALERIA DE CONQUISTAS")
    for ach, info in ACHIEVEMENTS_DB.items():
        is_unlocked = ach in unlocked
        color = rank_info['color'] if is_unlocked else "#444"
        st.markdown(f"""
            <div style='border: 1px solid {color}; padding: 12px; border-radius: 10px; margin-bottom: 10px; background: rgba(255,255,255,0.02);'>
                <h4 style='margin:0; color:{color};'>{'🌟' if is_unlocked else '🔒'} {ach}</h4>
                <p style='margin:5px 0; font-size: 13px; opacity: 0.8;'>{info['desc']}</p>
            </div>
        """, unsafe_allow_html=True)

with tab5:
    st.markdown("### 💎 CONTRATOS DE HONRA (RODÍZIO)")
    st.info("Metas reais baseadas em nível e persistência.")
    for reward in st.session_state.data["real_rewards"]:
        status = reward["status"]
        color = rank_info['color'] if status == "Liberado" else ("#27ae60" if status == "Resgatado" else "#555")
        st.markdown(f"""
            <div style='border-left: 5px solid {color}; padding: 15px; border-radius: 5px; margin-bottom: 10px; background: rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between;'>
                    <b>{reward['name']}</b>
                    <span style='color: {color}; font-size: 11px;'>{status.upper()}</span>
                </div>
                <small>Requisito: {reward['req']} {reward.get('target', reward['type']).upper()}</small>
            </div>
        """, unsafe_allow_html=True)

with tab6:
    st.markdown("### 💰 HUB DE INVESTIMENTOS")
    st.info("Deposite suas moedas aqui para destravar investimentos na sua carreira, corpo e rotina.")
    
    funds = st.session_state.data["investment_funds"]
    total_coins = st.session_state.data["coins"]
    st.write(f"**Seu Tesouro Atual:** 🪙 {total_coins} moedas")
    
    for category, amount in funds.items():
        st.markdown(f"**Fundo de {category}**")
        st.progress(min(1.0, amount/1000)) # Exemplo de barra de progresso para 1000 moedas
        col1, col2 = st.columns([1, 1])
        col1.write(f"🪙 {amount} acumuladas")
        if col2.button(f"INVESTIR 100", key=f"inv_fund_{category}"):
            if total_coins >= 100:
                st.session_state.data["coins"] -= 100
                st.session_state.data["investment_funds"][category] += 100
                st.rerun()
            else: st.error("Moedas insuficientes!")
    st.divider()
    st.write("🛠️ *Ao encher um fundo, peça minha curadoria para o seu próximo upgrade real.*")

with tab7:
    st.markdown("### 📜 REGISTROS DE AKASHA")
    for log in reversed(st.session_state.data["history"][-15:]):
        st.write(f"🛡️ {log}")
