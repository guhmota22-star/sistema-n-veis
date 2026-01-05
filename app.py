import streamlit as st
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO & CONEXÃO ---
st.set_page_config(page_title="SISTEMA: MONARCA", page_icon="🔱", layout="wide")

# Conexão com o Registro de Akasha (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(spreadsheet=st.secrets["SHEET_URL"], worksheet="Folha1")
        # Procura os dados do Guh Mota
        data_str = df[df['id'] == 'guh_mota']['data_json'].values[0]
        return json.loads(data_str)
    except:
        return {
            "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0,
            "points": 0, "last_reset": str(datetime.date.today()), "daily_done": False,
            "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
            "history": []
        }

def save(data):
    df = pd.DataFrame([{"id": "guh_mota", "data_json": json.dumps(data)}])
    conn.update(spreadsheet=st.secrets["SHEET_URL"], data=df)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- LÓGICA DE RECOMPENSAS ---
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
    
    st.session_state.data["history"].append(f"{datetime.datetime.now().strftime('%H:%M')} - {reason}")
    save(st.session_state.data)

# --- INTERFACE DARK MODE ---
st.markdown("<style>.stApp { background-color: #0a0a0b; color: #e0e0e0; }</style>", unsafe_allow_html=True)
st.title("🔱 SISTEMA: GUH MOTA")

# [O restante do código de interface (Gráficos e Tabs) permanece igual ao anterior]
# Lembre-se de usar save(st.session_state.data) sempre que houver alteração!

st.info("Conectado ao Registro de Akasha (Google Sheets)")

# Exemplo de botão atualizado:
if st.button("🏃 EXERCÍCIO"):
    if st.session_state.data["mp"] >= 20:
        st.session_state.data["mp"] -= 20
        add_xp(30, 10, "Treino Concluído")
        st.rerun()
