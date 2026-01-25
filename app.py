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

# --- 2. GESTÃO DE DADOS E LÓGICA DE RANK (SISTEMA DE AKASHA) ---

# 1. Banco de Dados de Equipamentos
EQUIPMENT_DB = {
    "Assinatura de Banco de Questões": {"slot": "head", "bonus_int": 2, "xp_mult": 0.15, "desc": "+15% XP em Estudos"},
    "Tênis de Plantão": {"slot": "body", "hp_max": 20, "desc": "+20 HP Máximo"},
    "Estetoscóscope de Elite": {"slot": "hands", "bonus_sen": 5, "desc": "+5 Percepção Clínica"},
    "Cinto de LPO / Straps": {"slot": "hands", "bonus_str": 5, "desc": "+5 Força nos Treinos"},
    "Manual de Condutas": {"slot": "accessory", "mp_reduction": 5, "desc": "-5 MP de custo em INT"},
    "Smartwatch Pro": {"slot": "accessory", "coin_mult": 0.10, "desc": "+10% Moedas ganhas"}
}

# 2. Biblioteca de Conquistas e Contratos Reais
ACHIEVEMENTS_DB = {
    "Mestre do Anki": {"req": ("INT", 50), "title": "O Erudito", "desc": "+5% XP em Estudos"},
    "Titã de Diamantina": {"req": ("STR", 50), "title": "O Colosso", "hp_bonus": 5, "desc": "+5 HP Máximo"},
    "Voz do Paciente": {"req": ("CHA", 30), "title": "O Diplomata", "desc": "+10% Moedas em CHA"},
    "Olhar de Lince": {"req": ("SEN", 30), "title": "O Diagnosticador", "desc": "+2 MP por Missão"},
    "Sobrevivente": {"req": ("VIT", 50), "title": "O Veterano", "vit_mult": 1.10, "desc": "+10% Resistência (VIT)"},
    "Disciplina de Ferro": {"streak_req": 7, "title": "O Inabalável", "desc": "Mantenha um Streak de 7 dias"}
}

# Definição Padrão dos Contratos Reais
DEFAULT_REAL_REWARDS = [
    {"id": "rank_c", "name": "Scrub Premium ou Esteto Novo", "type": "lvl", "req": 20, "status": "Bloqueado"},
    {"id": "mestria_int", "name": "Livro/Curso de Residência", "type": "stat", "target": "INT", "req": 50, "status": "Bloqueado"},
    {"id": "forca_str", "name": "Acessório de Elite (Cinto LPO/Straps)", "type": "stat", "target": "STR", "req": 50, "status": "Bloqueado"},
    {"id": "resiliencia", "name": "Final de Semana de Descanso Total", "type": "streak", "req": 21, "status": "Bloqueado"},
    {"id": "tesouro", "name": "Jantar no Restaurante Favorito", "type": "coins", "req": 5000, "status": "Bloqueado"}
]

# 3. Definição das Funções Core
def get_rank_info(level):
    if level < 10: return {"name": "E", "color": "#9e9e9e", "glow": "rgba(158, 158, 158, 0.5)", "title": "Interno Novato"}
    if level < 20: return {"name": "D", "color": "#4caf50", "glow": "rgba(76, 175, 80, 0.5)", "title": "Interno Veterano"}
    if level < 30: return {"name": "C", "color": "#2196f3", "glow": "rgba(33, 150, 243, 0.5)", "title": "Residente Aspirante"}
    if level < 40: return {"name": "B", "color": "#9c27b0", "glow": "rgba(156, 39, 176, 0.5)", "title": "Mestre da Clínica"}
    if level < 50: return {"name": "A", "color": "#ff5722", "glow": "rgba(255, 87, 34, 0.5)", "title": "Monarca Hospitalar"}
    return {"name": "S", "color": "#ffcc00", "glow": "rgba(255, 204, 0, 0.6)", "title": "Soberano da Medicina"}

def get_initial_data():
    return {
        "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0, "points": 0,
        "last_access": str(datetime.date.today()),
        "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
        "inventory": [], "equipped": {"head": None, "body": None, "hands": None, "accessory": None},
        "achievements": [], "active_title": None, "history": [], "streaks": {},
        "real_rewards": DEFAULT_REAL_REWARDS
    }

def update_quest_streak(quest_id):
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    if quest_id not in st.session_state.data["streaks"]:
        st.session_state.data["streaks"][quest_id] = {"count": 1, "last_date": str(hoje)}
        return 1
    streak_data = st.session_state.data["streaks"][quest_id]
    last_date = datetime.datetime.strptime(streak_data["last_date"], "%Y-%m-%d").date()
    if last_date == ontem:
        streak_data["count"] += 1; streak_data["last_date"] = str(hoje)
    elif last_date < ontem:
        streak_data["count"] = 1; streak_data["last_date"] = str(hoje)
    return streak_data["count"]

def get_streak_multiplier(quest_id):
    count = st.session_state.data["streaks"].get(quest_id, {}).get("count", 0)
    if count >= 3: return min(0.50, (count - 2) * 0.05)
    return 0.0

def check_achievements():
    novas = []
    data = st.session_state.data
    for nome, info in ACHIEVEMENTS_DB.items():
        if nome not in data["achievements"]:
            if "req" in info:
                attr, meta = info["req"]
                if data["stats"][attr] >= meta:
                    data["achievements"].append(nome); novas.append(nome)
            if "streak_req" in info:
                if any(s.get("count", 0) >= info["streak_req"] for s in data["streaks"].values()):
                    data["achievements"].append(nome); novas.append(nome)
    return novas

def check_real_rewards():
    data = st.session_state.data
    liberados = 0
    for reward in data["real_rewards"]:
        if reward["status"] == "Bloqueado":
            unlocked = False
            if reward["type"] == "lvl" and data["lvl"] >= reward["req"]: unlocked = True
            elif reward["type"] == "coins" and data["coins"] >= reward["req"]: unlocked = True
            elif reward["type"] == "stat" and data["stats"][reward["target"]] >= reward["req"]: unlocked = True
            elif reward["type"] == "streak":
                if any(s.get("count", 0) >= reward["req"] for s in data["streaks"].values()): unlocked = True
            if unlocked:
                reward["status"] = "Liberado"; liberados += 1
    return liberados

def get_total_stats():
    # Bônus de vida por nível
    lvl_bonus_hp = (st.session_state.data["lvl"] - 1) * 5
    base = {s: round(v, 1) for s, v in st.session_state.data["stats"].items()}
    hp_extra = lvl_bonus_hp
    equipped = st.session_state.data["equipped"]
    
    for slot, item_name in equipped.items():
        if item_name in EQUIPMENT_DB:
            item = EQUIPMENT_DB[item_name]
            for stat in base: base[stat] = round(base[stat] + item.get(f"bonus_{stat.lower()}", 0), 1)
            hp_extra += item.get("hp_max", 0)
    
    # MP MAX DINÂMICO: Vinculado à Inteligência (Base 100 + 5 por ponto acima de 10)
    mp_max_calc = round(100 + (base["INT"] - 10) * 5, 1)

    for ach in st.session_state.data["achievements"]:
        if ach in ACHIEVEMENTS_DB:
            hp_extra += ACHIEVEMENTS_DB[ach].get("hp_bonus", 0)
            if "vit_mult" in ACHIEVEMENTS_DB[ach]: 
                base["VIT"] = round(base["VIT"] * ACHIEVEMENTS_DB[ach]["vit_mult"], 1)
    return base, round(hp_extra, 1), mp_max_calc

# 4. Inicialização Segura e Reparo de Save
if 'data' not in st.session_state:
    st.session_state.data = get_initial_data()
else:
    patch = {"achievements": [], "active_title": None, "inventory": [], "equipped": {}, "streaks": {}, "real_rewards": DEFAULT_REAL_REWARDS}
    for key, default in patch.items():
        if key not in st.session_state.data: st.session_state.data[key] = default
    st.session_state.data["inventory"] = [i for i in st.session_state.data["inventory"] if i in EQUIPMENT_DB]
    for slot in st.session_state.data["equipped"]:
        if st.session_state.data["equipped"][slot] not in EQUIPMENT_DB:
            st.session_state.data["equipped"][slot] = None

# 5. Execução da Lógica Core
novas_conquistas = check_achievements()
for ach in novas_conquistas: st.toast(f"🏆 CONQUISTA: {ach}", icon="🌟")

novos_liberados = check_real_rewards()
if novos_liberados > 0: st.toast(f"🎁 {novos_liberados} CONTRATO(S) REAL(IS) LIBERADO(S)!", icon="💎")

rank_info = get_rank_info(st.session_state.data["lvl"])
stats_totais, hp_bonus, mp_max_total = get_total_stats()

# Estilos e Regeneração
st.markdown(f"<style>h1, h2, h3 {{ color: {rank_info['color']} !important; text-shadow: 0 0 10px {rank_info['glow']} !important; }}</style>", unsafe_allow_html=True)
hoje = str(datetime.date.today())
if st.session_state.data.get("last_access") != hoje:
    st.session_state.data["mp"] = mp_max_total # Restaura para o MP Max Dinâmico
    max_hp_calc = 100 + hp_bonus
    st.session_state.data["hp"] = min(max_hp_calc, st.session_state.data["hp"] + 20)
    st.session_state.data["last_access"] = hoje
    
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
    c_hud1, c_hud2, c_hud3 = st.columns([1.2, 1, 1.3]) # Aumentei levemente a coluna do gráfico
    
    with c_hud1:
        st.markdown(f"### <span style='color:{rank_info['color']}'>RANK {rank_info['name']}</span> | NÍVEL {st.session_state.data['lvl']}", unsafe_allow_html=True)
        
        titulo_exibido = st.session_state.data.get("active_title") or rank_info['title']
        st.caption(f"🛡️ Título: {titulo_exibido}")
        
        hp_max_total = round(100 + hp_bonus, 1)
        hp_atual = round(st.session_state.data['hp'], 1)
        st.markdown(f"<span class='label-hp'>❤️ HP: {hp_atual}/{hp_max_total}</span>", unsafe_allow_html=True)
        st.progress(min(hp_atual / hp_max_total, 1.0))
        
        mp_atual = round(st.session_state.data['mp'], 1)
        st.markdown(f"<span class='label-mp'>🔷 MP: {mp_atual}/{mp_max_total}</span>", unsafe_allow_html=True)
        st.progress(min(mp_atual / mp_max_total, 1.0))

    with c_hud2:
        st.markdown("### RECOMPENSAS")
        xp_atual = round(st.session_state.data['xp'], 1)
        xp_needed = round(100 * (st.session_state.data['lvl'] ** 1.5), 1)
        
        st.markdown(f"<span class='label-xp'>✨ XP: {xp_atual}/{xp_needed}</span>", unsafe_allow_html=True)
        st.progress(min(xp_atual / xp_needed, 1.0))
        
        moedas = round(st.session_state.data['coins'], 1)
        st.markdown(f"<span class='label-coins'>💰 MOEDAS: {moedas}</span>", unsafe_allow_html=True)
        st.caption("Modo Offline: Registro Local")

    with c_hud3:
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
                    range=[0, max(values) + 12], # Aumentei o respiro interno
                    showticklabels=False,
                    gridcolor="rgba(255,255,255,0.1)"
                ),
                angularaxis=dict(
                    gridcolor="rgba(255,255,255,0.1)",
                    linecolor="rgba(255,255,255,0.2)",
                    tickfont=dict(size=10, color="#ddd", family="Courier New"),
                    rotation=90, # Rotacionado para centralizar melhor nomes longos
                    direction="clockwise"
                )
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=320, # Aumentado para dar margem vertical
            # MARGENS EXPANDIDAS: O segredo para não cortar a Vitalidade
            margin=dict(t=60, b=60, l=80, r=80), 
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

if "Mestre do Anki" in unlocked: xp_boost += 0.05
if "Voz de Paciente" in unlocked: coin_boost += 0.10

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗡️ QUESTS", "📊 STATUS", "🎒 ARSENAL", "🏆 CONQUISTAS", "💎 CONTRATOS", "🛒 MERCADO", "📜 LOGS"
])

with tab1:
    st.markdown(f"### ⚔️ QUADRO DE MISSÕES (RANK {rank_info['name']})")
    
    def run_quest(quest_id, mp_cost, hp_cost, str_g, int_g, agi_g, vit_g, cha_g, sen_g, xp, coins, msg):
        final_mp_cost = round(max(0, mp_cost - mp_red) if int_g > 0 else mp_cost, 1)
        
        if st.session_state.data["mp"] >= final_mp_cost and st.session_state.data["hp"] > hp_cost:
            streak_count = update_quest_streak(quest_id)
            s_mult = get_streak_multiplier(quest_id)
            
            st.session_state.data["mp"] -= final_mp_cost
            st.session_state.data["hp"] -= hp_cost
            
            stats = st.session_state.data["stats"]
            stats["STR"] += str_g; stats["INT"] += int_g; stats["AGI"] += agi_g
            stats["VIT"] += vit_g; stats["CHA"] += cha_g; stats["SEN"] += sen_g
            
            total_multiplier = xp_boost + s_mult
            final_xp = int(xp * (1 + total_multiplier))
            final_coins = int(coins * (1 + coin_boost))
            
            feedback = f"{msg} | Streak: 🔥{streak_count}"
            if hp_cost > 0: feedback += f" | ❤️ -{hp_cost} HP"
            
            add_xp(final_xp, final_coins, feedback)
            st.rerun()
        else:
            if st.session_state.data["hp"] <= hp_cost:
                st.error(f"⚠️ EXAUSTÃO EXTREMA! HP Insuficiente.")
            else:
                st.error(f"Mana Insuficiente! Falta {round(final_mp_cost - st.session_state.data['mp'], 1)} MP.")

    def quest_card(quest_id, label, subtext, key, mp_c, hp_c, s_g, i_g, a_g, v_g, c_g, sn_g, xp_b, coin_b, desc):
        streak = st.session_state.data["streaks"].get(quest_id, {}).get("count", 0)
        mult = get_streak_multiplier(quest_id)
        aura_class = "streak-aura" if streak >= 3 else ""
        flame = f" <span style='color:#ff4b4b;'>🔥{streak}</span>" if streak > 0 else ""
        hp_display = f" | ❤️ {hp_c}" if hp_c > 0 else ""
        
        st.markdown(f"""
            <div class='quest-card {aura_class}'>
                <strong>{label}</strong>{flame}<br>
                <small>{subtext}{hp_display}</small>
            </div>
        """, unsafe_allow_html=True)
        if st.button("EXECUTAR", key=key, use_container_width=True):
            run_quest(quest_id, mp_c, hp_c, s_g, i_g, a_g, v_g, c_g, sn_g, xp_b, coin_b, desc)

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1: quest_card("treino", "🏋️ TREINO PESADO", "20 MP", "q1", 20, 10, 0.5, 0, 0, 0, 0, 0, 30, 15, "Treino de Hipertrofia")
    with r1c2: 
        c_int = round(max(0, 15 - mp_red), 1)
        quest_card("estudo", "📖 ESTUDO CASO", f"{c_int} MP", "q2", 15, 0, 0, 0.5, 0, 0, 0, 0, 25, 12, "Estudo de Clínica")
    with r1c3: 
        st.markdown("<div class='quest-card'>💊 SUPLEMENTAÇÃO<br><small>0 MP | ❤️ +15 HP</small></div>", unsafe_allow_html=True)
        if st.button("EXECUTAR", key="q3", use_container_width=True):
            st.session_state.data["hp"] = min(100 + hp_bonus, st.session_state.data["hp"] + 15)
            run_quest("suple", 0, 0, 0, 0, 0, 0.2, 0, 0, 10, 5, "Protocolo de Saúde")

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1: quest_card("base", "🏠 ARRUMAR BASE", "10 MP", "q4", 10, 0, 0, 0, 0.3, 0, 0, 0, 20, 10, "Organização")
    with r2c2: quest_card("comun", "🗣️ COMUNICAÇÃO", "10 MP", "q5", 10, 0, 0, 0, 0, 0, 0.3, 0, 15, 8, "Treino Vocal")
    with r2c3: quest_card("med", "🎓 PLANTÃO/PRÁTICA", "25 MP", "q6", 25, 25, 0, 0, 0, 0, 0, 0.6, 45, 20, "Internato Hospitalar")

    st.divider()

    # ATUALIZAÇÃO: Sono agora respeita o MP Máximo calculado
    if st.button("💤 SONO REPARADOR", use_container_width=True):
        st.session_state.data["hp"] = round(100 + hp_bonus, 1)
        st.session_state.data["mp"] = mp_max_total 
        st.toast(f"Status Restaurados! (MP Máx: {mp_max_total})", icon="🌙")
        st.rerun()

with tab2:
    st.markdown(f"### 📊 FICHA TÉCNICA (ATRIBUTOS REAIS)")
    attr_map = {
        "STR": ("💪 Força", "Poder físico e hipertrofia"),
        "INT": ("🧠 Inteligência", "Conhecimento médico e estudos"),
        "AGI": ("⚡ Agilidade", "Organização e rapidez de ação"),
        "VIT": ("🩸 Vitalidade", "Resistência, saúde e sono"),
        "CHA": ("🗣️ Carisma", "Comunicação e liderança"),
        "SEN": ("👁️ Percepção", "Sensibilidade e prática clínica")
    }
    col_stats_left, col_stats_right = st.columns(2)
    for i, (stat, (name, desc)) in enumerate(attr_map.items()):
        base_val = round(st.session_state.data["stats"][stat], 1)
        total_val = round(stats_totais[stat], 1)
        bonus = round(total_val - base_val, 1)
        target_col = col_stats_left if i < 3 else col_stats_right
        with target_col:
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid {rank_info['color']}'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-size: 15px; font-weight: bold;'>{name}</span>
                        <span style='font-size: 18px; color: {rank_info['color']}; font-weight: bold;'>{total_val}</span>
                    </div>
                    <div style='font-size: 11px; color: #888;'>{desc}</div>
                    <div style='font-size: 10px; opacity: 0.6;'>
                        Base: {base_val} {f' | <span style="color:{rank_info["color"]}">+{bonus} bônus</span>' if bonus > 0 else ''}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    if st.session_state.data["points"] > 0:
        st.divider()
        st.success(f"✨ PONTOS DISPONÍVEIS: {st.session_state.data['points']}")
        cols_up = st.columns(6)
        for i, stat in enumerate(attr_map.keys()):
            if cols_up[i].button(f"+ {stat}", key=f"up_{stat}"):
                st.session_state.data["stats"][stat] += 1
                st.session_state.data["points"] -= 1
                st.rerun()

with tab3:
    st.markdown("### 🎒 SEU ARSENAL (INVENTÁRIO)")
    if not st.session_state.data["inventory"]:
        st.info("Inventário vazio.")
    else:
        for item in st.session_state.data["inventory"]:
            col1, col2 = st.columns([3, 1])
            slot = EQUIPMENT_DB[item]["slot"]
            is_eq = st.session_state.data["equipped"][slot] == item
            col1.write(f"**{item}** ({EQUIPMENT_DB[item]['desc']})")
            if col2.button("RETIRAR" if is_eq else "EQUIPAR", key=f"inv_{item}"):
                st.session_state.data["equipped"][slot] = None if is_eq else item
                st.rerun()

with tab4:
    st.markdown("### 🏆 GALERIA DE CONQUISTAS")
    for ach, info in ACHIEVEMENTS_DB.items():
        is_unlocked = ach in unlocked
        color = rank_info['color'] if is_unlocked else "#555"
        with st.container():
            st.markdown(f"""
                <div style='border: 1px solid {color}; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin:0; color:{color};'>{'🌟' if is_unlocked else '🔒'} {ach}</h4>
                    <p style='margin:5px 0; font-size: 14px;'>{info['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            if is_unlocked:
                title = info['title']
                if st.session_state.data["active_title"] == title:
                    st.button(f"TÍTULO EQUIPADO: {title}", disabled=True, key=f"title_{ach}")
                else:
                    if st.button(f"EQUIPAR TÍTULO: {title}", key=f"title_{ach}"):
                        st.session_state.data["active_title"] = title
                        st.rerun()

with tab5:
    st.markdown("### 💎 CONTRATOS DE HONRA (RECOMPENSAS REAIS)")
    st.info("Bata as metas no app para liberar prêmios no mundo físico.")
    for reward in st.session_state.data["real_rewards"]:
        status = reward["status"]
        color = rank_info['color'] if status == "Liberado" else ("#27ae60" if status == "Resgatado" else "#555")
        icon = "🔒" if status == "Bloqueado" else ("✅" if status == "Resgatado" else "🎁")
        with st.container():
            st.markdown(f"""
                <div style='border: 1px solid {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px; background: rgba(0,0,0,0.1); border-left: 5px solid {color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-size: 16px; font-weight: bold; color: {color};'>{icon} {reward['name']}</span><br>
                            <small style='opacity: 0.7;'>Requisito: {reward['req']} {reward.get('target', reward['type']).upper()}</small>
                        </div>
                        <span style='font-size: 12px; font-weight: bold; color: {color};'>{status.upper()}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if status == "Liberado":
                if st.button(f"RESGATAR RECOMPENSA REAL", key=f"resgate_{reward['id']}", use_container_width=True):
                    reward["status"] = "Resgatado"
                    st.rerun()

with tab6:
    st.markdown("### 🛒 MERCADO DE INVESTIMENTOS")
    for name, info in EQUIPMENT_DB.items():
        if name not in st.session_state.data["inventory"]:
            st.write(f"**{name}** - {info['desc']}")
            if st.button(f"INVESTIR (200 moedas)", key=f"buy_{name}"):
                if st.session_state.data["coins"] >= 200:
                    st.session_state.data["coins"] -= 200
                    st.session_state.data["inventory"].append(name)
                    st.rerun()
                else: st.error("Moedas insuficientes.")

with tab7:
    st.markdown("### 📜 REGISTROS DE AKASHA")
    for log in reversed(st.session_state.data["history"][-15:]):
        st.write(f"🛡️ {log}")        
