import streamlit as st
import json
import datetime
import pandas as pd
import plotly.graph_objects as go

import streamlit as st

# --- 1. CONFIGURAÇÃO DE INTERFACE & ESTILO ---
st.set_page_config(page_title="SISTEMA: MONARCA", page_icon="🔱", layout="wide")

# Importação da fonte Orbitron para o estilo Solo Leveling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* Fundo e Texto Global */
    .stApp { 
        background-color: #0a0a0b; 
        color: #e0e0e0; 
        font-family: 'Orbitron', sans-serif; 
    }

    /* Títulos com efeito de brilho Neon */
    h1, h2, h3 { 
        color: #00d4ff; 
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5), 0 0 20px rgba(0, 212, 255, 0.2);
        text-transform: uppercase; 
        letter-spacing: 2px;
    }

    /* Botões Estilo HUD */
    .stButton>button { 
        background-color: rgba(0, 212, 255, 0.05); 
        border: 1px solid #00d4ff; 
        color: #00d4ff; 
        width: 100%; 
        border-radius: 5px;
        transition: all 0.3s ease-in-out;
        font-weight: bold;
        text-transform: uppercase;
    }

    .stButton>button:hover { 
        background-color: #00d4ff !important; 
        color: #000000 !important; 
        box-shadow: 0 0 15px #00d4ff; 
        transform: scale(1.02);
    }

    /* Classes Dinâmicas de Rank (Preparadas para o futuro) */
    .rank-e { color: #9e9e9e; text-shadow: 0 0 5px #9e9e9e; } /* Cinza */
    .rank-d { color: #4caf50; text-shadow: 0 0 5px #4caf50; } /* Verde */
    .rank-c { color: #2196f3; text-shadow: 0 0 5px #2196f3; } /* Azul */
    .rank-s { color: #ffcc00; text-shadow: 0 0 10px #ffcc00; } /* Dourado */

    /* Cores das Labels de Status */
    .label-hp { color: #ff4b4b; font-weight: bold; text-shadow: 0 0 5px rgba(255, 75, 75, 0.4); }
    .label-mp { color: #00d4ff; font-weight: bold; text-shadow: 0 0 5px rgba(0, 212, 255, 0.4); }
    .label-xp { color: #ffaa00; font-weight: bold; }
    .label-coins { color: #ffee00; font-weight: bold; }

    /* Customização das Barras de Progresso */
    div[st-ui="stProgress"] > div > div > div {
        background-color: #00d4ff; /* Cor padrão, será alterada via código depois */
    }
    
    /* Container para o HUD parecer uma janela flutuante */
    .hud-container {
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 20px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (CAMINHO A: MANUAL) ---
def get_initial_data():
    return {
        "lvl": 1, "xp": 0, "hp": 100, "mp": 100, "coins": 0, "points": 0,
        "stats": {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10},
        "history": []
    }

if 'data' not in st.session_state:
    st.session_state.data = get_initial_data()

# --- 3. BARRA LATERAL: REGISTRO DE AKASHA ---
with st.sidebar:
    st.markdown("### 💾 REGISTRO DE AKASHA")
    st.caption("Guarde sua essência antes de fechar o sistema.")
    
    # Exportar Save
    # 'indent=4' torna o arquivo JSON legível para humanos no PC
    data_string = json.dumps(st.session_state.data, indent=4)
    
    st.download_button(
        label="📥 DESCARREGAR SAVE (JSON)", 
        data=data_string, 
        file_name=f"monarca_save_{datetime.date.today()}.json", 
        mime="application/json",
        use_container_width=True # Otimizado para a barra lateral do PC
    )
    
    st.divider()
    
    # Importar Save
    st.markdown("### 📤 CARREGAR SAVE")
    uploaded_file = st.file_uploader("Upload do fragmento .json", type="json")
    
    if uploaded_file is not None:
        try:
            temp_data = json.load(uploaded_file)
            
            # Validação: Verifica se o arquivo tem os campos essenciais do Sistema
            if "lvl" in temp_data and "stats" in temp_data:
                st.session_state.data = temp_data
                st.success("Sincronização com Akasha Concluída!")
                st.rerun()
            else:
                st.error("Assinatura Inválida! Este fragmento não pertence ao Sistema.")
                
        except Exception as e:
            st.error(f"Erro ao restaurar essência: {e}")

    # Espaço extra para estética no PC
    st.sidebar.markdown("---")
    st.sidebar.info("Status: Sistema de Persistência Manual Ativo.")

# --- 4. LÓGICA DE PROGRESSÃO E RANKING ---

def get_rank(level):
    """Define o Rank do Caçador com base no nível (Solo Leveling Style)"""
    if level < 10: return "E"
    if level < 20: return "D"
    if level < 30: return "C"
    if level < 40: return "B"
    if level < 50: return "A"
    return "S"

def add_xp(amount, coins, reason):
    # 1. Adiciona recompensas básicas
    st.session_state.data["xp"] += amount
    st.session_state.data["coins"] += coins
    
    # Notificação discreta de ganho (Ótimo para PC)
    st.toast(f"✨ +{amount} XP | 💰 +{coins} Moedas", icon="⚔️")
    
    # 2. Processamento de Level Up (com suporte a múltiplos níveis e transbordo)
    # Fórmula: $XP_{req} = 100 \times Lvl^{1.5}$
    while True:
        level = st.session_state.data["lvl"]
        xp_needed = int(100 * (level ** 1.5))
        
        if st.session_state.data["xp"] >= xp_needed:
            # Sobe de nível e desconta o XP gasto
            st.session_state.data["xp"] -= xp_needed
            st.session_state.data["lvl"] += 1
            st.session_state.data["points"] += 5
            
            # Feedback épico de Level Up
            st.balloons()
            st.success(f"🎊 NÍVEL UP! VOCÊ ALCANÇOU O NÍVEL {st.session_state.data['lvl']}!")
            
            # Verifica se o Rank mudou
            novo_rank = get_rank(st.session_state.data["lvl"])
            if novo_rank != get_rank(level):
                st.warning(f"⚠️ EVOLUÇÃO DE RANK: Você agora é um Caçador de Rank {novo_rank}!")
        else:
            break
            
    # 3. Registro no Histórico (Limitado a 50 entradas para eficiência)
    timestamp = datetime.datetime.now().strftime('%d/%m %H:%M')
    log_entry = f"{timestamp} - {reason} (+{amount} XP)"
    
    st.session_state.data["history"].append(log_entry)
    if len(st.session_state.data["history"]) > 50:
        st.session_state.data["history"].pop(0) # Remove o mais antigo
# --- 5. HUD DO MONARCA ---
st.title("🔱 STATUS: GUH MOTA")

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
    st.write("Modo Offline: Armazenamento Local Ativo")

with c_hud3:
    df_radar = pd.DataFrame(dict(r=list(st.session_state.data["stats"].values()), theta=list(st.session_state.data["stats"].keys())))
    fig = go.Figure(data=go.Scatterpolar(r=df_radar['r'], theta=df_radar['theta'], fill='toself', line_color='#00d4ff'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 50])), paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=180, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 6. ABAS DO SISTEMA ---
tab1, tab2, tab3, tab4 = st.tabs(["🗡️ QUESTS", "📊 ATRIBUTOS", "🛒 LOJA", "📜 LOG"])

with tab1:
    st.subheader("Daily Quests")
    
    # Linha 1: Físico e Intelecto
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        if st.button("🏋️ TREINO"):
            if st.session_state.data["mp"] >= 20:
                st.session_state.data["mp"] -= 20
                st.session_state.data["stats"]["STR"] += 0.5
                add_xp(30, 10, "Treino Concluído")
                st.rerun()
            else: st.error("Mana Baixa!")
    with r1c2:
        if st.button("📖 LER UM CAPÍTULO"):
            if st.session_state.data["mp"] >= 15:
                st.session_state.data["mp"] -= 15
                st.session_state.data["stats"]["INT"] += 0.5
                add_xp(25, 10, "Leitura de Capítulo")
                st.rerun()
            else: st.error("Mana Baixa!")
    with r1c3:
        if st.button("💊 TOMAR REMÉDIO"):
            st.session_state.data["stats"]["VIT"] += 0.2
            add_xp(10, 5, "Medicação Diária")
            st.rerun()

    # Linha 2: Organização e Fono
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        if st.button("🏠 ARRUMAR A CASA"):
            if st.session_state.data["mp"] >= 10:
                st.session_state.data["mp"] -= 10
                st.session_state.data["stats"]["AGI"] += 0.3
                add_xp(20, 10, "Ordem no Ambiente")
                st.rerun()
    with r2c2:
        if st.button("🗣️ EXERCÍCIO DE FONO"):
            if st.session_state.data["mp"] >= 10:
                st.session_state.data["mp"] -= 10
                st.session_state.data["stats"]["CHA"] += 0.3
                add_xp(15, 5, "Treino de Comunicação")
                st.rerun()
    with r2c3:
        if st.button("🗂️ FLASHCARDS"):
            if st.session_state.data["mp"] >= 15:
                st.session_state.data["mp"] -= 15
                st.session_state.data["stats"]["INT"] += 0.4
                add_xp(20, 10, "Revisão Anki/Flashcards")
                st.rerun()

    # Linha 3: Alta Performance
    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        if st.button("🧠 ESTUDO COMPLEXO"):
            if st.session_state.data["mp"] >= 30:
                st.session_state.data["mp"] -= 30
                st.session_state.data["stats"]["INT"] += 0.8
                add_xp(50, 20, "Foco Profundo (Medicina)")
                st.rerun()
    with r3c2:
        if st.button("🎓 ATIVIDADE ACADÊMICA"):
            if st.session_state.data["mp"] >= 20:
                st.session_state.data["mp"] -= 20
                st.session_state.data["stats"]["SEN"] += 0.5
                add_xp(40, 15, "Internato / Prática")
                st.rerun()
    with r3c3:
        if st.button("💤 SONO REPARADOR"):
            st.session_state.data["hp"] = 100
            st.session_state.data["mp"] = 100
            st.success("Energia Restaurada!")
            st.rerun()

    # Masmorra de Fim de Semana
    st.divider()
    st.subheader("🏰 MASMORRA ESPECIAL")
    is_weekend = datetime.date.today().weekday() >= 5
    if is_weekend:
        if st.button("🔥 DESAFIO DE FIM DE SEMANA (TRIPLO XP)"):
            if st.session_state.data["mp"] >= 50:
                st.session_state.data["mp"] -= 50
                st.session_state.data["stats"]["VIT"] += 1.0
                add_xp(150, 50, "Masmorra Lendária Limpa")
                st.rerun()
    else:
        st.info("Portal fechado. Abre apenas Sábados e Domingos.")

with tab2:
    st.subheader(f"Pontos Disponíveis: {st.session_state.data['points']}")
    col_at1, col_at2 = st.columns(2)
    for i, (stat, val) in enumerate(st.session_state.data["stats"].items()):
        target_col = col_at1 if i < 3 else col_at2
        with target_col:
            c_s1, c_s2 = st.columns([2,1])
            c_s1.write(f"**{stat}:** {val}")
            if st.session_state.data["points"] > 0:
                if c_s2.button(f"+", key=f"up_{stat}"):
                    st.session_state.data["stats"][stat] += 1
                    st.session_state.data["points"] -= 1
                    st.rerun()

with tab3:
    st.subheader("Loja do Sistema")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("**🧪 POÇÃO DE HP**")
        st.write("Custo: 50 Moedas | Efeito: +30 HP")
        if st.button("Comprar HP", key="buy_hp"):
            if st.session_state.data["coins"] >= 50:
                st.session_state.data["coins"] -= 50
                st.session_state.data["hp"] = min(100, st.session_state.data["hp"] + 30)
                st.rerun()
    with col_l2:
        st.markdown("**🔷 POÇÃO DE MANA**")
        st.write("Custo: 50 Moedas | Efeito: +30 MP")
        if st.button("Comprar Mana", key="buy_mp"):
            if st.session_state.data["coins"] >= 50:
                st.session_state.data["coins"] -= 50
                st.session_state.data["mp"] = min(100, st.session_state.data["mp"] + 30)
                st.rerun()

with tab4:
    st.subheader("Log de Atividade")
    for log in reversed(st.session_state.data["history"][-20:]):
        st.write(f"🛡️ {log}")
