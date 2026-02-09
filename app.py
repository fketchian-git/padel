import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# 1. CONFIGURACIÓN Y ESTÉTICA "PRO"
st.set_page_config(page_title="Padel Elite CGC", layout="wide", page_icon="🎾")

st.markdown("""
    <style>
    .stApp { background-color: #1A1C23; color: #F0F2F6; }
    .header-container {
        display: flex; justify-content: space-between; align-items: center;
        background: linear-gradient(135deg, #2D313E 0%, #1A1C23 100%);
        padding: 30px; border-radius: 20px; border-bottom: 5px solid #92D050;
        margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .player-card {
        background: #2D313E; border-radius: 15px; padding: 20px;
        margin-bottom: 15px; border: 1px solid #3E4455;
        transition: transform 0.3s;
    }
    .player-card:hover { transform: scale(1.02); border-color: #92D050; }
    .next-match-banner {
        background: linear-gradient(90deg, #92D050 0%, #4D7C1B 100%);
        color: #1A1C23; padding: 20px; border-radius: 15px;
        text-align: center; font-weight: 900; font-size: 22px;
        margin-bottom: 30px; text-transform: uppercase;
    }
    .podium-card {
        text-align: center; background: #232732; padding: 20px;
        border-radius: 20px; border: 2px solid #92D050;
        position: relative; overflow: hidden;
    }
    .stat-mini { font-size: 0.85rem; color: #92D050; font-weight: bold; }
    h1, h2, h3 { font-family: 'Arial Black', sans-serif; letter-spacing: -1px; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #2D313E; border-radius: 10px; padding: 10px 20px; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #92D050 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONSTANTES
NOMBRES = ["Fran", "Pepe", "Mauri", "Bruno M", "Bruno C" , "Fer", "Fede B", "Santi"]
AVATARES = {n: f"https://api.dicebear.com/7.x/avataaars/svg?seed={n}&backgroundColor=2d313e" for n in NOMBRES}
IMG_CANCHA = "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?q=80&w=400"
FILE_PATH = "data_padel.csv"
REPO = st.secrets["REPO_NAME"]
TOKEN = st.secrets["GITHUB_TOKEN"]

# 3. LÓGICA DE GITHUB
def leer_github():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        decoded = base64.b64decode(data["content"]).decode('utf-8')
        return pd.read_csv(StringIO(decoded)), data["sha"]
    else:
        return inicializar_fixture(), None

def guardar_github(df, sha):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    content = base64.b64encode(df.to_csv(index=False).encode('utf-8')).decode('utf-8')
    payload = {"message": "Update Padel Scores", "content": content, "sha": sha}
    requests.put(url, json=payload, headers=headers)

def inicializar_fixture():
    rondas = [[(0,1,2,3), (4,5,6,7)], [(0,2,4,6), (1,3,5,7)], [(0,3,5,6), (1,2,4,7)],
              [(0,4,1,5), (2,6,3,7)], [(0,5,2,7), (1,4,3,6)], [(0,6,1,7), (2,4,3,5)],
              [(0,7,3,4), (1,6,2,5)], [(0,1,4,5), (2,3,6,7)], [(0,2,1,3), (4,6,5,7)],
              [(0,3,1,2), (5,6,4,7)], [(0,4,2,6), (1,5,3,7)], [(0,5,1,4), (2,7,3,6)],
              [(0,6,2,4), (1,7,3,5)], [(0,7,1,6), (3,4,2,5)]]
    data = []
    pid = 1
    for ri, r in enumerate(rondas):
        for m in r:
            data.append({"ID": pid, "Rd": ri+1, "P_1": f"{NOMBRES[m[0]]} & {NOMBRES[m[1]]}", 
                         "G1": 0, "G2": 0, "P_2": f"{NOMBRES[m[2]]} & {NOMBRES[m[3]]}"})
            pid += 1
    return pd.DataFrame(data)

# --- INICIO DE APP ---
df, sha = leer_github()

st.markdown(f"""
    <div class="header-container">
        <div>
            <h1 style="margin:0; font-size: 45px; color: #92D050;">PADEL ELITE CGC</h1>
            <p style="margin:0; opacity:0.7; font-size: 18px;">Season 2026 | Professional Tracker</p>
        </div>
        <img src="{IMG_CANCHA}" style="width:180px; border-radius:15px; border: 3px solid #92D050; box-shadow: 0 0 20px #92D05055;">
    </div>
    """, unsafe_allow_html=True)

# 4. PRÓXIMO PARTIDO (MAGIA)
proximo = df[(df['G1'] == 0) & (df['G2'] == 0)].head(1)
if not proximo.empty:
    st.markdown(f"""
    <div class="next-match-banner">
        ⚡ PRÓXIMA BATALLA: Ronda {proximo.iloc[0]['Rd']} | {proximo.iloc[0]['P_1']} VS {proximo.iloc[0]['P_2']} ⚡
    </div>
    """, unsafe_allow_html=True)

tab_rank, tab_load, tab_sys = st.tabs(["🏆 LEADERBOARD", "📝 SCOREBOARD", "⚙️ SYSTEM"])

with tab_load:
    st.subheader("Registrar Resultados de Ronda")
    new_df = st.data_editor(
        df,
        column_config={
            "G1": st.column_config.NumberColumn("G1", min_value=0, max_value=7),
            "G2": st.column_config.NumberColumn("G2", min_value=0, max_value=7),
            "ID": None
        },
        disabled=["ID", "Rd", "P_1", "P_2"],
        hide_index=True, use_container_width=True
    )
    if st.button("🚀 SUBIR RESULTADOS A LA NUBE"):
        guardar_github(new_df, sha)
        st.balloons()
        st.success("Sincronización completa.")
        st.rerun()

with tab_rank:
    # Lógica de Puntos
    stats = {n: {"Pts": 0, "Dif": 0, "PJ": 0, "PG": 0} for n in NOMBRES}
    jugados = df[(df['G1'] > 0) | (df['G2'] > 0)]
    for _, r in jugados.iterrows():
        p1, p2 = r['P_1'].split(" & "), r['P_2'].split(" & ")
        for j in p1:
            stats[j]["PJ"] += 1
            stats[j]["Pts"] += (3 if r['G1'] > r['G2'] else 1)
            stats[j]["Dif"] += (r['G1'] - r['G2'])
            if r['G1'] > r['G2']: stats[j]["PG"] += 1
        for j in p2:
            stats[j]["PJ"] += 1
            stats[j]["Pts"] += (3 if r['G2'] > r['G1'] else 1)
            stats[j]["Dif"] += (r['G2'] - r['G1'])
            if r['G2'] > r['G1']: stats[j]["PG"] += 1
    
    ranking = pd.DataFrame.from_dict(stats, orient='index').reset_index().sort_values(["Pts", "Dif"], ascending=False)
    
    # PODIO TOP 3
    top3 = ranking.head(3)
    c_pod = st.columns(3)
    order = [1, 0, 2] # Para que el 1ero quede en el medio visualmente
    for idx, pos in enumerate(order):
        row = top3.iloc[pos]
        with c_pod[idx]:
            st.markdown(f"""
                <div class="podium-card">
                    <img src="{AVATARES[row['index']]}" width="80">
                    <h2 style="margin-bottom:0;">#{pos+1}</h2>
                    <h3 style="color:white !important;">{row['index']}</h3>
                    <h1 style="margin:0; font-size:40px;">{row['Pts']}</h1>
                    <div class="stat-mini">Dif: {row['Dif']} | PJ: {row['PJ']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # RESTO DEL RANKING (4 al 8)
    for i in range(3, 8):
        row = ranking.iloc[i]
        st.markdown(f"""
            <div class="player-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <span style="font-size: 24px; font-weight: 900; color: #92D050;">#{i+1}</span>
                        <img src="{AVATARES[row['index']]}" width="50">
                        <div>
                            <span style="font-size: 20px; font-weight: bold;">{row['index']}</span><br>
                            <span style="opacity:0.6; font-size:12px;">Victorias: {row['PG']}</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 26px; font-weight: 900; color: #92D050;">{row['Pts']} Pts</span><br>
                        <span class="stat-mini">Dif. Games: {row['Dif']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab_sys:
    st.subheader("Control de Mando")
    pwd = st.text_input("Clave Maestra:", type="password")
    if st.button("RESET TOTAL DEL TORNEO"):
        if pwd == "padelCGC":
            new_fixture = inicializar_fixture()
            guardar_github(new_fixture, sha)
            st.warning("Torneo reiniciado. Los datos antiguos han sido borrados.")
            st.rerun()