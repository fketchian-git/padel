import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Padel Elite App", layout="wide")

# 2. Datos de Jugadores
nombres = ["Fran“, “Pepe”, “Mauri”, “Bruno M”, “Bruno C” , “Fer”, “Fede B”, “Santi”]
avatares = {n: f"https://api.dicebear.com/7.x/avataaars/svg?seed={n}" for n in nombres}

# 3. Función Fixture
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

# Estado de la sesión
if 'df' not in st.session_state:
    st.session_state.df = generar_fixture()

# --- UI ---
st.title("🎾 Padel Elite App")

tab_pos, tab_fix, tab_admin = st.tabs(["🏆 Posiciones", "📝 Resultados", "⚙️ Admin"])

with tab_fix:
    st.subheader("Cargar Resultados")
    st.session_state.df = st.data_editor(
        st.session_state.df,
        column_config={
            "G1": st.column_config.NumberColumn(min_value=0, max_value=4),
            "G2": st.column_config.NumberColumn(min_value=0, max_value=4),
        },
        disabled=["ID", "Rd", "Pareja_1", "Pareja_2"],
        hide_index=True,
    )

with tab_pos:
    st.subheader("Ranking Actual")
    stats = {n: {"Pts": 0, "Dif": 0, "PJ": 0} for n in nombres}
    df_actual = st.session_state.df
    jugados = df_actual[(df_actual['G1'] > 0) | (df_actual['G2'] > 0)]
    
    for _, r in jugados.iterrows():
        p1, p2 = r['Pareja_1'].split(" & "), r['Pareja_2'].split(" & ")
        for j in p1:
            stats[j]["PJ"] += 1
            stats[j]["Pts"] += (3 if r['G1'] > r['G2'] else 1)
            stats[j]["Dif"] += (r['G1'] - r['G2'])
        for j in p2:
            stats[j]["PJ"] += 1
            stats[j]["Pts"] += (3 if r['G2'] > r['G1'] else 1)
            stats[j]["Dif"] += (r['G2'] - r['G1'])
    
    ranking = pd.DataFrame.from_dict(stats, orient='index').reset_index()
    ranking.columns = ['Jugador', 'Pts', 'Dif', 'PJ']
    ranking = ranking.sort_values(["Pts", "Dif"], ascending=False)
    
    for _, row in ranking.iterrows():
        c1, c2, c3, c4 = st.columns([1,3,2,1])
        c1.image(avatares[row['Jugador']], width=50)
        c2.markdown(f"**{row['Jugador']}**")
        c3.write(f"{row['Pts']} Pts (Dif: {row['Dif']})")
        c4.write(f"PJ: {row['PJ']}")
        st.divider()

with tab_admin:
    if st.button("🚨 Reiniciar Torneo"):
        st.session_state.df = generar_fixture()
        st.rerun()