import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILO CSS MEJORADO
st.set_page_config(page_title="Padel Pro Manager", layout="wide")

st.markdown("""
    <style>
    /* Fondo Gris Suave */
    .stApp { background-color: #262730; color: #E0E0E0; }
    
    /* Header con Imagen */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1E1E26;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-bottom: 4px solid #92D050;
    }

    /* Tarjetas de Jugador */
    .player-card {
        background-color: #31333F;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #4A4D58;
    }
    
    .pos-number {
        font-size: 20px;
        font-weight: bold;
        color: #92D050;
        margin-right: 15px;
    }

    /* Banner Próximo Partido */
    .next-match-banner {
        background: linear-gradient(90deg, #92D050 0%, #4D7C1B 100%);
        color: black;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }

    h1, h2, h3 { color: #92D050 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATOS
nombres = ["Fran", "Pepe", "Mauri", "Bruno M", "Bruno C" , "Fer", "Fede B", "Santi"]
avatares = {n: f"https://api.dicebear.com/7.x/avataaars/svg?seed={n}" for n in nombres}
foto_cancha = "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?q=80&w=400&auto=format&fit=crop"

def generar_fixture():
    rondas = [[(0,1,2,3), (4,5,6,7)], [(0,2,4,6), (1,3,5,7)], [(0,3,5,6), (1,2,4,7)],
              [(0,4,1,5), (2,6,3,7)], [(0,5,2,7), (1,4,3,6)], [(0,6,1,7), (2,4,3,5)],
              [(0,7,3,4), (1,6,2,5)], [(0,1,4,5), (2,3,6,7)], [(0,2,1,3), (4,6,5,7)],
              [(0,3,1,2), (5,6,4,7)], [(0,4,2,6), (1,5,3,7)], [(0,5,1,4), (2,7,3,6)],
              [(0,6,2,4), (1,7,3,5)], [(0,7,1,6), (3,4,2,5)]]
    data = []
    pid = 1
    for ri, r in enumerate(rondas):
        for m in r:
            data.append({"ID": pid, "Rd": ri+1, "Pareja_1": f"{nombres[m[0]]} & {nombres[m[1]]}", 
                         "G1": 0, "G2": 0, "Pareja_2": f"{nombres[m[2]]} & {nombres[m[3]]}"})
            pid += 1
    return pd.DataFrame(data)

if 'df' not in st.session_state:
    st.session_state.df = generar_fixture()

# --- HEADER PERSONALIZADO ---
st.markdown(f"""
    <div class="header-container">
        <div>
            <h1 style="margin:0;">PADEL ELITE</h1>
            <p style="margin:0; opacity:0.8;">Torneo Americano Individual</p>
        </div>
        <img src="{foto_cancha}" style="width:150px; border-radius:10px; border: 2px solid #92D050;">
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA PRÓXIMO PARTIDO ---
df_actual = st.session_state.df
proximo = df_actual[(df_actual['G1'] == 0) & (df_actual['G2'] == 0)].head(1)

if not proximo.empty:
    st.markdown(f"""
    <div class="next-match-banner">
        🎾 PRÓXIMO PARTIDO (Ronda {proximo.iloc[0]['Rd']}): <br>
        <span style="font-size:20px;">{proximo.iloc[0]['Pareja_1']} vs {proximo.iloc[0]['Pareja_2']}</span>
    </div>
    """, unsafe_allow_html=True)

tab_pos, tab_fix, tab_admin = st.tabs(["🏆 TABLA", "📅 FIXTURE", "⚙️ CONFIG"])

with tab_fix:
    st.session_state.df = st.data_editor(
        st.session_state.df,
        column_config={
            "G1": st.column_config.NumberColumn("G1", min_value=0, max_value=7),
            "G2": st.column_config.NumberColumn("G2", min_value=0, max_value=7),
        },
        disabled=["ID", "Rd", "Pareja_1", "Pareja_2"],
        hide_index=True, use_container_width=True
    )

with tab_pos:
    stats = {n: {"Pts": 0, "Dif": 0, "PJ": 0, "PG": 0} for n in nombres}
    jugados = st.session_state.df[(st.session_state.df['G1'] > 0) | (st.session_state.df['G2'] > 0)]
    
    for _, r in jugados.iterrows():
        p1, p2 = r['Pareja_1'].split(" & "), r['Pareja_2'].split(" & ")
        for j in p1:
            stats[j]["PJ"] += 1; stats[j]["Pts"] += (3 if r['G1'] > r['G2'] else 1); stats[j]["Dif"] += (r['G1'] - r['G2'])
            if r['G1'] > r['G2']: stats[j]["PG"] += 1
        for j in p2:
            stats[j]["PJ"] += 1; stats[j]["Pts"] += (3 if r['G2'] > r['G1'] else 1); stats[j]["Dif"] += (r['G2'] - r['G1'])
            if r['G2'] > r['G1']: stats[j]["PG"] += 1
    
    ranking = pd.DataFrame.from_dict(stats, orient='index').reset_index().sort_values(["Pts", "Dif"], ascending=False)
    
    # Podio
    top3 = ranking.head(3)
    c_top = st.columns(3)
    for i, (idx, row) in enumerate(top3.iterrows()):
        with c_top[i]:
            st.markdown(f"""<div style="text-align:center; background:#1E1E26; padding:15px; border-radius:15px; border:1px solid #92D050;">
                <img src="{avatares[row['index']]}" width="60"><br>
                <b>#{i+1} {row['index']}</b><br><span style="color:#92D050; font-size:24px;">{row['Pts']}</span> Pts</div>""", unsafe_allow_html=True)

    st.write("")
    # Puestos 4 al 8
    resto = ranking.iloc[3:]
    for i, row in resto.iterrows():
        st.markdown(f"""
        <div class="player-card">
            <div style="display: flex; align-items: center;">
                <span class="pos-number">#{resto.index.get_loc(i) + 4}</span>
                <img src="{avatares[row['index']]}" width="40" style="margin-right:15px;">
                <div style="flex-grow:1;"><b>{row['index']}</b> | Puntos: {row['Pts']}</div>
                <div style="text-align:right; font-size:12px; opacity:0.7;">Dif: {row['Dif']}<br>PJ: {row['PJ']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_admin:
    if st.button("RESET"):
        st.session_state.df = generar_fixture()
        st.rerun()