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
        
# --- 5. HUD DO MONARCA ---

# Título Principal com efeito de brilho
st.markdown(f"<h1>🔱 JANELA DE STATUS: {st.session_state.data.get('name', 'GUH MOTA')}</h1>", unsafe_allow_html=True)

# Container principal para agrupar o HUD
hud_container = st.container()

with hud_container:
    c_hud1, c_hud2, c_hud3 = st.columns([1.2, 1, 1.2]) # Ajuste de proporção para PC
    
    with c_hud1:
        # Recupera o Rank dinamicamente da Parte 4
        lvl = st.session_state.data['lvl']
        rank = get_rank(lvl) # Função definida no bloco anterior
        
        st.markdown(f"### <span class='rank-{rank.lower()}'>RANK {rank}</span> | NÍVEL {lvl}", unsafe_allow_html=True)
        
        # Status de HP (Vida)
        hp_val = st.session_state.data['hp']
        st.markdown(f"<span class='label-hp'>❤️ HP: {hp_val}/100</span>", unsafe_allow_html=True)
        st.progress(hp_val / 100)
        
        # Status de MP (Mana/Energia)
        mp_val = st.session_state.data['mp']
        st.markdown(f"<span class='label-mp'>🔷 MP: {mp_val}/100</span>", unsafe_allow_html=True)
        st.progress(mp_val / 100)

    with c_hud2:
        st.markdown("### RECOMPENSAS")
        
        # Cálculo de XP necessário para exibição
        xp_atual = st.session_state.data['xp']
        xp_needed = int(100 * (lvl ** 1.5))
        percent_xp = min(xp_atual / xp_needed, 1.0)
        
        st.markdown(f"<span class='label-xp'>✨ XP: {xp_atual} / {xp_needed}</span>", unsafe_allow_html=True)
        st.progress(percent_xp)
        
        st.markdown(f"<span class='label-coins'>💰 MOEDAS: {st.session_state.data['coins']}</span>", unsafe_allow_html=True)
        
        # Indicador de salvamento offline para PC
        st.caption("📂 Armazenamento: Local (Offline)")
        st.caption(f"📅 Ciclo Atual: {datetime.date.today().strftime('%d/%m/%Y')}")

    with c_hud3:
        # Preparação dos dados do Radar
        labels = list(st.session_state.data["stats"].keys())
        values = list(st.session_state.data["stats"].values())
        
        # Ajuste dinâmico do limite do gráfico
        max_stat = max(values)
        radar_range = [0, max(50, max_stat + 10)] 

        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name='Atributos',
            line_color='#00d4ff',
            fillcolor='rgba(0, 212, 255, 0.3)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=radar_range, color="#444", gridcolor="#222"),
                angularaxis=dict(color="#888", gridcolor="#222")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=230, # Aumentado para melhor visualização no PC
            margin=dict(t=20, b=20, l=40, r=40)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.divider()

# --- 6. ABAS DO SISTEMA (AÇÃO E ESTRATÉGIA) ---

tab1, tab2, tab3, tab4 = st.tabs(["🗡️ QUESTS DIÁRIAS", "📊 ATRIBUTOS", "🛒 MERCADO", "📜 REGISTROS"])

with tab1:
    st.markdown("### ⚔️ QUADRO DE MISSÕES")
    st.caption("Complete as tarefas para fortalecer sua essência.")

    # Linha 1: Físico e Intelecto
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        st.button("🏋️ TREINO PESADO", help="Aumenta STR (Força) e queima MP.", on_click=lambda: 
            add_xp(30, 15, "Treino Concluído") if st.session_state.data["mp"] >= 20 else st.error("Mana Insuficiente"))
        # Nota: STR aumenta via add_xp ou lógica interna dependendo do seu setup anterior
    with r1c2:
        st.button("📖 LER UM CAPÍTULO", help="Foco em INT (Inteligência).", on_click=lambda: 
            add_xp(25, 10, "Capítulo Estudado") if st.session_state.data["mp"] >= 15 else st.error("Mana Insuficiente"))
    with r1c3:
        st.button("💊 TOMAR REMÉDIO", help="+0.2 VIT (Vitalidade). Sem custo de Mana.", on_click=lambda: 
            add_xp(10, 5, "Medicação Tomada"))

    # Linha 2: Organização e Fono
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        st.button("🏠 ARRUMAR A CASA", help="Aumenta AGI (Agilidade).", on_click=lambda: 
            add_xp(20, 10, "Ambiente Organizado") if st.session_state.data["mp"] >= 10 else st.error("Mana Insuficiente"))
    with r2c2:
        st.button("🗣️ EXERCÍCIO DE FONO", help="Aumenta CHA (Carisma/Comunicação).", on_click=lambda: 
            add_xp(15, 5, "Treino Vocal") if st.session_state.data["mp"] >= 10 else st.error("Mana Insuficiente"))
    with r2c3:
        st.button("🗂️ FLASHCARDS", help="Consolidação de memória médica.", on_click=lambda: 
            add_xp(20, 12, "Revisão Anki") if st.session_state.data["mp"] >= 15 else st.error("Mana Insuficiente"))

    # Linha 3: Alta Performance (Específico para Internato)
    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        st.button("🧠 ESTUDO COMPLEXO", help="Estudo denso para o Internato.", on_click=lambda: 
            add_xp(50, 25, "Foco Profundo (Med)") if st.session_state.data["mp"] >= 35 else st.error("Mana Insuficiente"))
    with r3c2:
        st.button("🎓 ATIVIDADE ACADÊMICA", help="Prática clínica e percepção (SEN).", on_click=lambda: 
            add_xp(40, 20, "Prática Hospitalar") if st.session_state.data["mp"] >= 25 else st.error("Mana Insuficiente"))
    with r3c3:
        if st.button("💤 SONO REPARADOR", help="Restaura todo HP e MP."):
            st.session_state.data["hp"] = 100
            st.session_state.data["mp"] = 100
            st.toast("Energia Restaurada!", icon="💤")
            st.rerun()

    # Masmorra Especial
    st.divider()
    is_weekend = datetime.date.today().weekday() >= 5
    if is_weekend:
        st.warning("🔥 PORTAL DA MASMORRA ABERTO!")
        if st.button("🐉 LIMPAR MASMORRA DE FIM DE SEMANA", use_container_width=True):
            if st.session_state.data["mp"] >= 60:
                st.session_state.data["mp"] -= 60
                add_xp(200, 100, "Masmorra Lendária Limpa")
                st.rerun()
            else: st.error("Você está exausto demais para este desafio!")
    else:
        st.info("🕒 O Portal da Masmorra de Fim de Semana está selado. Continue treinando.")

with tab2:
    st.markdown(f"### 📊 DISTRIBUIÇÃO DE ATRIBUTOS")
    st.write(f"Pontos Disponíveis: **{st.session_state.data['points']}**")
    
    # Dicionário de descrições para imersão
    attr_desc = {
        "STR": "Força física e poder de hipertrofia.",
        "INT": "Capacidade cognitiva e estudo médico.",
        "AGI": "Velocidade de reação e gestão de tempo.",
        "VIT": "Resistência a doenças e fadiga.",
        "CHA": "Eloquência com pacientes e networking.",
        "SEN": "Intuição clínica e percepção hospitalar."
    }

    col_at1, col_at2 = st.columns(2)
    for i, (stat, val) in enumerate(st.session_state.data["stats"].items()):
        target_col = col_at1 if i < 3 else col_at2
        with target_col:
            with st.container():
                st.write(f"**{stat}**: {val}")
                st.caption(attr_desc.get(stat, ""))
                if st.session_state.data["points"] > 0:
                    if st.button(f"Fortalecer {stat}", key=f"up_{stat}"):
                        st.session_state.data["stats"][stat] += 1
                        st.session_state.data["points"] -= 1
                        st.rerun()
            st.write("") # Espaçador

with tab3:
    st.markdown("### 🛒 MERCADO DE ITENS")
    c_shop1, c_shop2 = st.columns(2)
    
    with c_shop1:
        with st.container():
            st.markdown("#### ❤️ Poção de HP")
            st.write("Custo: 50 Moedas")
            if st.button("Consumir (50g)", key="buy_hp"):
                if st.session_state.data["coins"] >= 50:
                    st.session_state.data["coins"] -= 50
                    st.session_state.data["hp"] = min(100, st.session_state.data["hp"] + 30)
                    st.toast("+30 HP Recuperado!", icon="❤️")
                    st.rerun()
    
    with c_shop2:
        with st.container():
            st.markdown("#### 🔷 Poção de Mana")
            st.write("Custo: 50 Moedas")
            if st.button("Consumir (50g)", key="buy_mp"):
                if st.session_state.data["coins"] >= 50:
                    st.session_state.data["coins"] -= 50
                    st.session_state.data["mp"] = min(100, st.session_state.data["mp"] + 30)
                    st.toast("+30 MP Recuperado!", icon="🔷")
                    st.rerun()

with tab4:
    st.markdown("### 📜 REGISTROS DE AKASHA")
    for log in reversed(st.session_state.data["history"][-20:]):
        st.markdown(f"> `{log}`")
