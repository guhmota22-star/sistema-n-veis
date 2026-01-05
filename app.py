import streamlit as st
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE INTERFACE & CSS (SOLO LEVELING DARK) ---
st.set_page_config(page_title="SISTEMA: MONARCA", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0b; color: #e0e0e0; font-family: 'Orbitron', sans-serif; }
    h1, h2, h3 { color: #00d4ff; text-shadow: 0 0 15px #00d4ff; text-transform: uppercase; }
    .stButton>button { background-color: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; color: #00d4ff; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #00d4ff !important; color: black !important; box-shadow: 0 0 20px #00d4ff; }
    .label-hp { color: #ff4b4b; font-weight: bold; }
    .label-mp { color: #00d4ff; font-weight: bold; }
    .label-xp { color: #ffaa00; font-weight: bold; }
    .label-coins { color: #ffee00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO COM O REGISTRO DE AKASHA (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    hoje = str(datetime.date.today())
    try:
        # Tenta ler da Google Sheet (Caminho B)
        df = conn.read(spreadsheet=st.secrets["SHEET_URL"], worksheet="Sheet1")
        data_str = df[df['id'] == 'guh_mota']['data_json'].values[0]
        return json.loads(data_str)
    except Exception:
        # Se falhar (primeira vez), carrega valores base
        return {
            "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0,
            "points": 0, "last_reset": hoje, "daily_done": False,
            "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
            "history": []
        }

def save_to_akasha(data):
    try:
        df = pd.DataFrame([{"id": "guh_mota", "data_json": json.dumps(data)}])
        conn.update(spreadsheet=st.secrets["SHEET_URL"], data=df)
    except:
        st.error("Falha ao sincronizar com o Registro de Akasha.")

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 3. LÓGICA DE TEMPO REAL (PENALIDADE DIÁRIA) ---
hoje_dt = str(datetime.date.today())
if st.session_state.data["last_reset"] != hoje_dt:
    if not st.session_state.data.get("daily_done", False):
        st.session_state.data["hp"] = max(0, st.session_state.data["hp"] - 20)
        st.warning("⚠️ PENALIDADE DETECTADA: Falha em completar missões. -20 HP.")
    st.session_state.data["last_reset"] = hoje_dt
    st.session_state.data["daily_done"] = False
    st.session_state.data["mp"] = min(100, st.session_state.data["mp"] + 30) # Regeneração natural
    save_to_akasha(st.session_state.data)

def add_xp(amount, coins, reason):
    st.session_state.data["xp"] += amount
    st.session_state.data["coins"] += coins
    st.session_state.data["daily_done"] = True
    xp_needed = int(100 * (st.session_state.data["lvl"] ** 1.5))
    
    if st.session_state.data["xp"] >= xp_needed:
        st.session_state.data["lvl"] += 1
        st.session_state.data["xp"] = 0
        st.session_state.data["points"] += 5
        st.balloons()
        st.success(f"LEVEL UP! RANK ATUALIZADO: NÍVEL {st.session_state.data['lvl']}")
    
    st.session_state.data["history"].append(f"{datetime.datetime.now().strftime('%H:%M')} - {reason}")
    save_to_akasha(st.session_state.data)

# --- 4. INTERFACE (HUD DO MONARCA) ---
st.title("🔱 SISTEMA: GUH MOTA")

c_hud1, c_hud2, c_hud3 = st.columns([1, 1, 1])
with c_hud1:
    xp_needed = int(100 * (st.session_state.data['lvl'] ** 1.5))
    st.markdown(f"**NÍVEL {st.session_state.data['lvl']}** | **RANK E**")
    st.markdown(f"<span class='label-hp'>❤️ HP: {st.session_state.data['hp']}/100</span>", unsafe_allow_html=True)
    st.progress(st.session_state.data['hp'] / 100)
    st.markdown(f"<span class='label-mp'>🔷 MP: {st.session_state.data['mp']}/100</span>", unsafe_allow_html=True)
    st.progress(st.session_state.data['mp'] / 100)

with c_hud2:
    st.markdown(f"<span class='label-xp'>✨ XP: {st.session_state.data['xp']}/{xp_needed}</span>", unsafe_allow_html=True)
    st.progress(min(st.session_state.data['xp'] / xp_needed, 1.0))
    st.markdown(f"<span class='label-coins'>💰 MOEDAS: {st.session_state.data['coins']}</span>", unsafe_allow_html=True)
    st.write(f"Registro: Ativo 🟢")

with c_hud3:
    df_radar = pd.DataFrame(dict(r=list(st.session_state.data["stats"].values()), theta=list(st.session_state.data["stats"].keys())))
    fig = go.Figure(data=go.Scatterpolar(r=df_radar['r'], theta=df_radar['theta'], fill='toself', line_color='#00d4ff'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 50])), paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=150, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 5. ABAS DE FUNCIONALIDADES ---
tab1, tab2, tab3, tab4 = st.tabs(["🗡️ QUESTS", "📊 ATRIBUTOS", "🛒 LOJA", "📜 LOG"])

with tab1:
    st.subheader("Daily Quests")
    
    # --- LINHA 1 ---
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏋️ TREINO"):
            if st.session_state.data["mp"] >= 20:
                st.session_state.data["mp"] -= 20
                st.session_state.data["stats"]["STR"] += 0.5
                add_xp(30, 10, "Treino Concluído")
                st.rerun()
            else: st.error("Falta de Mana!")
    with c2:
        if st.button("📖 LER UM CAPÍTULO"):
            if st.session_state.data["mp"] >= 15:
                st.session_state.data["mp"] -= 15
                st.session_state.data["stats"]["INT"] += 0.5
                add_xp(25, 10, "Leitura de Capítulo")
                st.rerun()
            else: st.error("Falta de Mana!")
    with c3:
        if st.button("💊 TOMAR REMÉDIO"):
            st.session_state.data["stats"]["VIT"] += 0.2
            add_xp(10, 5, "Medicação Tomada")
            st.rerun()

    # --- LINHA 2 ---
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🏠 ARRUMAR A CASA"):
            if st.session_state.data["mp"] >= 15:
                st.session_state.data["mp"] -= 15
                st.session_state.data["stats"]["AGI"] += 0.3
                add_xp(20, 10, "Ambiente Organizado")
                st.rerun()
            else: st.error("Falta de Mana!")
    with c5:
        if st.button("🗣️ EXERCÍCIO DE FONO"):
            if st.session_state.data["mp"] >= 10:
                st.session_state.data["mp"] -= 10
                st.session_state.data["stats"]["CHA"] += 0.3
                add_xp(15, 5, "Treino de Fono")
                st.rerun()
            else: st.error("Falta de Mana!")
    with c6:
        if st.button("🗂️ FLASHCARDS"):
            if st.session_state.data["mp"] >= 10:
                st.session_state.data["mp"] -= 10
                st.session_state.data["stats"]["INT"] += 0.3
                add_xp(20, 10, "Revisão Espaçada")
                st.rerun()
            else: st.error("Falta de Mana!")

    # --- LINHA 3 ---
    c7, c8, c9 = st.columns(3)
    with c7:
        if st.button("🧠 ESTUDO COMPLEXO"):
            if st.session_state.data["mp"] >= 30:
                st.session_state.data["mp"] -= 30
                st.session_state.data["stats"]["INT"] += 0.8
                add_xp(50, 20, "Foco Profundo")
                st.rerun()
            else: st.error("Falta de Mana!")
    with c8:
        if st.button("🎓 ATIVIDADE ACADÊMICA"):
            if st.session_state.data["mp"] >= 20:
                st.session_state.data["mp"] -= 20
                st.session_state.data["stats"]["SEN"] += 0.5
                add_xp(40, 15, "Progresso no Internato")
                st.rerun()
            else: st.error("Falta de Mana!")
    with c9:
        if st.button("💤 SONO REPARADOR"):
            st.session_state.data["hp"] = 100
            st.session_state.data["mp"] = 100
            st.session_state.data["daily_done"] = True
            st.success("Recuperação Total!")
            save_to_akasha(st.session_state.data)
            st.rerun()

with tab2:
    st.subheader(f"Pontos de Atributo Disponíveis: {st.session_state.data['points']}")
    cols = st.columns(3)
    for i, (stat, val) in enumerate(st.session_state.data["stats"].items()):
        with cols[i % 3]:
            st.write(f"**{stat}:** {val}")
            if st.session_state.data["points"] > 0:
                if st.button(f"UP {stat}", key=f"btn_{stat}"):
                    st.session_state.data["stats"][stat] += 1
                    st.session_state.data["points"] -= 1
                    save_to_akasha(st.session_state.data)
                    st.rerun()

with tab3:
    st.subheader("Mercado do Sistema")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("**🧪 Poção de HP**")
        if st.button("Comprar (50 Moedas)", key="buy_hp"):
            if st.session_state.data["coins"] >= 50:
                st.session_state.data["coins"] -= 50
                st.session_state.data["hp"] = min(100, st.session_state.data["hp"] + 30)
                save_to_akasha(st.session_state.data); st.rerun()
            else: st.error("Moedas insuficientes!")
    with col_l2:
        st.markdown("**🔷 Poção de Mana**")
        if st.button("Comprar (50 Moedas)", key="buy_mp"):
            if st.session_state.data["coins"] >= 50:
                st.session_state.data["coins"] -= 50
                st.session_state.data["mp"] = min(100, st.session_state.data["mp"] + 30)
                save_to_akasha(st.session_state.data); st.rerun()
            else: st.error("Moedas insuficientes!")

with tab4:
    st.subheader("Histórico de Conquistas")
    for log in reversed(st.session_state.data["history"][-15:]):
        st.write(f"✨ {log}")

st.sidebar.markdown("---")
if st.sidebar.button("♻️ FORÇAR SINCRONIZAÇÃO"):
    save_to_akasha(st.session_state.data)
    st.sidebar.success("Dados enviados ao Akasha!")
