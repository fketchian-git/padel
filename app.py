import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILO CSS
st.set_page_config(page_title="Padel Pro Elite", layout="wide")

# Inyección de CSS para diseño personalizado
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #0E1117; color: white; }
    
    /* Estilo de las tarjetas de ranking */
    .player-card {
        background-color: #1E2130;
        border-radius: 15px;
        padding: 20px;
        border-left: 5px solid #92D050;
        margin-bottom: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    /* Títulos en verde padel */
    h1, h2, h3 { color: #92D050 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Estilo para métricas */
    [data-testid="stMetricValue"] { color: #92D050 !important; }
    
    /* Botones personalizados */
    .stButton>button {
        background-color: #92D050;
        color: black;
        border-radius: 20px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATOS
nombres = ["Fran", "Pepe", "Mauri", "Bruno M", "Bruno C" , "Fer", "Fede B", "Santi"]
avatares = {n: f"https://api.dicebear.com/7.x/avataaars/svg?seed={n}" for n in nombres}

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

# --- INTERFAZ ---
st.title("🎾 PADEL ELITE TRACKER")
st.markdown("---")

tab_pos, tab_fix, tab_admin = st.tabs(["🏆 RANKING", "📅 PARTIDOS", "⚙️ GESTIÓN"])

with tab_fix:
    st.subheader("📝 Carga de Resultados")
    st.session_state.df = st.data_editor(
        st.session_state.df,
        column_config={
            "G1": st.column_config.NumberColumn("G1", min_value=0, max_value=7),
            "G2": st.column_config.NumberColumn("G2", min_value=0, max_value=7),
            "Rd": "Ronda"
        },
        disabled=["ID", "Rd", "Pareja_1", "Pareja_2"],
        hide_index=True, use_container_width=True
    )

with tab_pos:
    st.subheader("🥇 Tabla de Posiciones")
    
    # Lógica de puntos
    stats = {n: {"Pts": 0, "Dif": 0, "PJ": 0, "PG": 0} for n in nombres}
    jugados = st.session_state.df[(st.session_state.df['G1'] > 0) | (st.session_state.df['G2'] > 0)]
    
    for _, r in jugados.iterrows():
        p1, p2 = r['Pareja_1'].split(" & "), r['Pareja_2'].split(" & ")
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
    
    ranking = pd.DataFrame.from_dict(stats, orient='index').reset_index()
    ranking.columns = ['Jugador', 'Pts', 'Dif', 'PJ', 'PG']
    ranking = ranking.sort_values(["Pts", "Dif"], ascending=False)

    # Mostrar Top 3 destacado
    top3 = ranking.head(3)
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; border: 2px solid #92D050; border-radius: 20px; padding: 10px;">
                <img src="{avatares[row['Jugador']]}" width="80">
                <h2 style="margin:0;">#{i+1}</h2>
                <p style="font-size: 20px; font-weight: bold;">{row['Jugador']}</p>
                <h1 style="margin:0;">{row['Pts']}</h1>
                <p>Puntos</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Resto del ranking en tarjetas
    for _, row in ranking.iterrows():
        st.markdown(f"""
        <div class="player-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <img src="{avatares[row['Jugador']]}" width="50">
                    <div>
                        <b style="font-size: 18px;">{row['Jugador']}</b><br>
                        <small>PJ: {row['PJ']} | PG: {row['PG']}</small>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 24px; font-weight: bold; color: #92D050;">{row['Pts']} Pts</span><br>
                    <small>Dif: {row['Dif']}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_admin:
    st.subheader("⚙️ Configuración del Torneo")
    if st.button("🚨 REINICIAR TODO"):
        st.session_state.df = generar_fixture()
        st.rerun()