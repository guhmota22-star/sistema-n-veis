import streamlit as st
import json
import datetime
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(page_title="SISTEMA: MONARCA", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0b; color: #e0e0e0; font-family: 'Orbitron', sans-serif; }
    h1, h2, h3 { color: #00d4ff; text-shadow: 0 0 15px #00d4ff; text-transform: uppercase; }
    .stButton>button { background-color: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; color: #00d4ff; width: 100%; }
    .label-hp { color: #ff4b4b; font-weight: bold; }
    .label-mp { color: #00d4ff; font-weight: bold; }
    .label-xp { color: #ffaa00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (SAVE MANUAL) ---
def get_initial_data():
    return {
        "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0, "points": 0,
        "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
        "history": []
    }

if 'data' not in st.session_state:
    st.session_state.data = get_initial_data()

# --- 3. BARRA LATERAL: O "MEMORY CARD" ---
with st.sidebar:
    st.header("💾 MEMORY CARD")
    
    # Exportar Dados
    data_string = json.dumps(st.session_state.data)
    st.download_button(label="📥 DESCARREGAR SAVE", data=data_string, file_name="monarca_save.json", mime="application/json")
    
    st.divider()
    
    # Importar Dados
    st.subheader("📤 CARREGAR SAVE")
    uploaded_file = st.file_uploader("Suba o seu ficheiro .json", type="json")
    if uploaded_file is not None:
        st.session_state.data = json.load(uploaded_file)
        st.success("Progresso Carregado!")

# --- 4. LÓGICA DE JOGO ---
def add_xp(amount, coins, reason):
    st.session_state.data["xp"] += amount
    st.session_state.data["coins"] += coins
    # Cálculo LaTeX para XP: $XP_{necessário} = 100 \times Lvl^{1.5}$
    xp_needed = int(100 * (st.session_state.data["lvl"] ** 1.5))
    
    if st.session_state.data["xp"] >= xp_needed:
        st.session_state.data["lvl"] += 1
        st.session_state.data["xp"] = 0
        st.session_state.data["points"] += 5
        st.balloons()
    
    st.session_state.data["history"].append(f"{datetime.datetime.now().strftime('%H:%M')} - {reason}")

# --- 5. INTERFACE HUD ---
st.title("🔱 STATUS: GUH MOTA")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"**NÍVEL {st.session_state.data['lvl']}**")
    st.markdown(f"<span class='label-hp'>❤️ HP: {st.session_state.data['hp']}/100</span>", unsafe_allow_html=True)
    st.progress(st.session_state.data['hp'] / 100)
with c2:
    st.markdown(f"<span class='label-mp'>🔷 MP: {st.session_state.data['mp']}/100</span>", unsafe_allow_html=True)
    st.progress(st.session_state.data['mp'] / 100)
with c3:
    st.markdown(f"💰 MOEDAS: {st.session_state.data['coins']}")

st.divider()

# --- 6. MISSÕES ---
tab1, tab2 = st.tabs(["🗡️ QUESTS", "📊 ATRIBUTOS"])

with tab1:
    st.subheader("Daily Quests")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("🏋️ TREINO"):
            if st.session_state.data["mp"] >= 20:
                st.session_state.data["mp"] -= 20
                add_xp(30, 10, "Treino")
                st.rerun()
        if st.button("💊 REMÉDIO"):
            add_xp(10, 5, "Medicação")
            st.rerun()
        if st.button("🗣️ FONO"):
            add_xp(20, 10, "Fono")
            st.rerun()
    with col_q2:
        if st.button("🧠 ESTUDO COMPLEXO"):
            if st.session_state.data["mp"] >= 30:
                st.session_state.data["mp"] -= 30
                add_xp(50, 20, "Estudo")
                st.rerun()
        if st.button("🗂️ FLASHCARDS"):
            add_xp(20, 10, "Revisão")
            st.rerun()
        if st.button("💤 SONO REPARADOR"):
            st.session_state.data["hp"] = 100
            st.session_state.data["mp"] = 100
            st.success("Sistema Restaurado!")
            st.rerun()

with tab2:
    st.write(f"Pontos para distribuir: {st.session_state.data['points']}")
    for s, v in st.session_state.data["stats"].items():
        st.write(f"**{s}:** {v}")
