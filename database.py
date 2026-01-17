import datetime

# --- 1. BANCO DE DADOS DE EQUIPAMENTOS ---
EQUIPMENT_DB = {
    "Assinatura de Banco de Questões": {"slot": "head", "bonus_int": 2, "xp_mult": 0.15, "desc": "+15% XP em Estudos"},
    "Tênis de Plantão": {"slot": "body", "hp_max": 20, "desc": "+20 HP Máximo"},
    "Estetoscópio de Elite": {"slot": "hands", "bonus_sen": 5, "desc": "+5 Percepção Clínica"},
    "Cinto de LPO / Straps": {"slot": "hands", "bonus_str": 5, "desc": "+5 Força nos Treinos"},
    "Manual de Condutas": {"slot": "accessory", "mp_reduction": 5, "desc": "-5 MP de custo em INT"},
    "Smartwatch Pro": {"slot": "accessory", "coin_mult": 0.10, "desc": "+10% Moedas ganhas"},
    "Galão de Hidratação": {"slot": "accessory", "bonus_vit": 3, "desc": "+3 Vitalidade (Hidratação)"}
}

# --- 2. QUADRO DE MISSÕES ---
QUESTS_DB = [
    {"id": "q1", "label": "🏋️ TREINO", "cost": 20, "xp": 30, "coins": 15, "stats": {"STR": 0.5}, "msg": "Treino Concluído"},
    {"id": "q2", "label": "📖 LER CAPÍTULO", "cost": 15, "xp": 25, "coins": 10, "stats": {"INT": 0.5}, "msg": "Leitura Concluída"},
    {"id": "q3", "label": "💊 TOMAR REMÉDIO", "cost": 0, "xp": 10, "coins": 5, "stats": {"VIT": 0.2}, "msg": "Medicação Diária"},
    {"id": "q4", "label": "🏠 ARRUMAR CASA", "cost": 10, "xp": 20, "coins": 10, "stats": {"AGI": 0.3}, "msg": "Ordem no Ambiente"},
    {"id": "q5", "label": "🗣️ EXERCÍCIO FONO", "cost": 10, "xp": 15, "coins": 5, "stats": {"CHA": 0.3}, "msg": "Treino de Fono"},
    {"id": "q6", "label": "🗂️ FLASHCARDS", "cost": 15, "xp": 20, "coins": 10, "stats": {"INT": 0.4}, "msg": "Revisão Anki"},
    {"id": "q7", "label": "🧠 ESTUDO COMPLEXO", "cost": 30, "xp": 50, "coins": 20, "stats": {"INT": 0.8}, "msg": "Foco Profundo (Med)"},
    {"id": "q8", "label": "🎓 ATIV. ACADÊMICA", "cost": 20, "xp": 40, "coins": 15, "stats": {"SEN": 0.5}, "msg": "Prática/Internato"}
]

# --- 3. LÓGICA DE RANK ---
def get_rank_info(level):
    if level < 10: return {"name": "E", "color": "#9e9e9e", "glow": "rgba(158, 158, 158, 0.5)", "title": "Interno Novato"}
    if level < 20: return {"name": "D", "color": "#4caf50", "glow": "rgba(76, 175, 80, 0.5)", "title": "Interno Veterano"}
    if level < 30: return {"name": "C", "color": "#2196f3", "glow": "rgba(33, 150, 243, 0.5)", "title": "Residente Aspirante"}
    if level < 40: return {"name": "B", "color": "#9c27b0", "glow": "rgba(156, 39, 176, 0.5)", "title": "Mestre da Clínica"}
    if level < 50: return {"name": "A", "color": "#ff5722", "glow": "rgba(255, 87, 34, 0.5)", "title": "Monarca Hospitalar"}
    return {"name": "S", "color": "#ffcc00", "glow": "rgba(255, 204, 0, 0.6)", "title": "Soberano da Medicina"}

# --- 4. CÁLCULO DE STATUS COM AUTO-REPARO ---
def get_total_stats(data):
    # Garante que as chaves novas existam (Resolve image_e5675a.png)
    if "stats" not in data: data["stats"] = {"STR": 10, "INT": 10, "AGI": 10, "VIT": 10, "CHA": 10, "SEN": 10}
    if "equipped" not in data: data["equipped"] = {"head": None, "body": None, "hands": None, "accessory": None}
    
    stats_base = data["stats"].copy()
    hp_extra = 0
    for slot, item_name in data["equipped"].items():
        if item_name in EQUIPMENT_DB:
            item = EQUIPMENT_DB[item_name]
            # Soma bônus se existirem no banco
            for stat in stats_base:
                key = f"bonus_{stat.lower()}"
                stats_base[stat] += item.get(key, 0)
            hp_extra += item.get("hp_max", 0)
    return stats_base, hp_extra
