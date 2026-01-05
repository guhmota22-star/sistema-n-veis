import streamlit as st
import json
import os
import datetime
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DE INTERFACE & CSS (SOLO LEVELING DARK) ---
st.set_page_config(page_title="SISTEMA DE NÍVEIS", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0b; color: #e0e0e0; font-family: 'Orbitron', sans-serif; }
    h1, h2, h3 { color: #00d4ff; text-shadow: 0 0 15px #00d4ff; text-transform: uppercase; }
    .stButton>button { background-color: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; color: #00d4ff; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #00d4ff; color: black; box-shadow: 0 0 20px #00d4ff; }
    
    /* Barras de Status */
    .status-container { border: 1px solid #333; padding: 15px; border-radius: 10px; background: rgba(255,255,255,0.02); margin-bottom: 20px; }
    .label-hp { color: #ff4b4b; font-weight: bold; }
    .label-mp { color: #00d4ff; font-weight: bold; }
    .label-xp { color: #ffaa00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DO SISTEMA ---
SAVE_FILE = "hunter_data.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {
        "lvl": 1, "xp": 0, "hp": 100, "mp": 100,
        "points": 0,
        "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
        "history": []
    }

if 'data' not in st.session_state:
    st.session_state.data = load_data()

def save():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state.data, f)

def add_xp(amount, reason):
    st.session_state.data["xp"] += amount
    xp_needed = 100 * (st.session_state.data["lvl"] ** 1.5)
    
    if st.session_state.data["xp"] >= xp_needed:
        st.session_state.data["lvl"] += 1
        st.session_state.data["xp"] = 0
        st.session_state.data["points"] += 5
        st.balloons()
        st.success(f"🎊 LEVEL UP! VOCÊ AGORA É NÍVEL {st.session_state.data['lvl']}!")
    
    st.session_state.data["history"].append(f"{datetime.datetime.now().strftime('%H:%M')} - {reason}: +{amount} XP")
    save()

# --- 3. INTERFACE (HUD DO CAÇADOR) ---
st.title("🔱 JANELA DE STATUS: GUH MOTA")

# Coluna de Status e Gráfico
col_stats, col_radar = st.columns([1, 1])

with col_stats:
    st.markdown(f"### RANK E | NÍVEL {st.session_state.data['lvl']}")
    
    # Barras Dinâmicas
    xp_needed = int(100 * (st.session_state.data['lvl'] ** 1.5))
    st.markdown(f"<span class='label-hp'>❤️ HP: {st.session_state.data['hp']}/100</span>", unsafe_allow_html=True)
    st.progress(st.session_state.data['hp'] / 100)
    
    st.markdown(f"<span class='label-mp'>🔷 MP: {st.session_state.data['mp']}/100</span>", unsafe_allow_html=True)
    st.progress(st.session_state.data['mp'] / 100)
    
    st.markdown(f"<span class='label-xp'>✨ XP: {st.session_state.data['xp']}/{xp_needed}</span>", unsafe_allow_html=True)
    st.progress(min(st.session_state.data['xp'] / xp_needed, 1.0))

with col_radar:
    # Gráfico de Atributos
    df_radar = pd.DataFrame(dict(
        r=list(st.session_state.data["stats"].values()),
        theta=list(st.session_state.data["stats"].keys())
    ))
    fig = go.Figure(data=go.Scatterpolar(r=df_radar['r'], theta=df_radar['theta'], fill='toself', line_color='#00d4ff'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 50], color="#444")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(t=30, b=30, l=30, r=30)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 4. SISTEMA DE MISSÕES & ATRIBUTOS ---
tab1, tab2, tab3 = st.tabs(["🗡️ MISSÕES DIÁRIAS", "📊 ATRIBUTOS", "🎒 INVENTÁRIO"])

with tab1:
    st.subheader("Daily Quests")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("🏃 EXERCÍCIO (30 MIN)"):
            if st.session_state.data["mp"] >= 20:
                st.session_state.data["mp"] -= 20
                add_xp(30, "Treino de Força")
                st.session_state.data["stats"]["STR"] += 0.5
                st.rerun()
            else: st.error("Mana Insuficiente!")

    with c2:
        if st.button("📖 LER 20 PÁGINAS"):
            if st.session_state.data["mp"] >= 15:
                st.session_state.data["mp"] -= 15
                add_xp(25, "Estudo de Inteligência")
                st.session_state.data["stats"]["INT"] += 0.5
                st.rerun()
            else: st.error("Mana Insuficiente!")

    with c3:
        if st.button("💤 SONO DE QUALIDADE"):
            st.session_state.data["hp"] = 100
            st.session_state.data["mp"] = 100
            st.success("HP e MP Restaurados!")
            save()
            st.rerun()

with tab2:
    st.subheader(f"Pontos Disponíveis: {st.session_state.data['points']}")
    cols = st.columns(3)
    for i, (stat, val) in enumerate(st.session_state.data["stats"].items()):
        with cols[i % 3]:
            st.write(f"**{stat}:** {val}")
            if st.session_state.data["points"] > 0:
                if st.button(f"UP {stat}", key=stat):
                    st.session_state.data["stats"][stat] += 1
                    st.session_state.data["points"] -= 1
                    save()
                    st.rerun()

with tab3:
    st.subheader("Itens e Histórico")
    for log in reversed(st.session_state.data["history"][-5:]):
        st.write(log)
