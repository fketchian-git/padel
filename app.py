{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww19120\viewh14540\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
\
# 1. CONFIGURACI\'d3N E INTERFAZ\
st.set_page_config(page_title="Padel Pro Manager", layout="wide")\
\
st.markdown("""\
    <style>\
    .stMetric \{ background-color: #1e2130; border-radius: 10px; padding: 10px; border: 1px solid #92D050; \}\
    </style>\
    """, unsafe_allow_html=True)\
\
# 2. JUGADORES (C\'e1mbialos aqu\'ed)\
nombres_jugadores = [\'93Fran\'93, \'93Pepe\'94, \'93Mauri\'94, \'93Bruno M\'94, \'93Bruno C\'94 , \'93Fer\'94, \'93Fede B\'94, \'93Santi\'94]\
avatares = \{n: f"https://api.dicebear.com/7.x/avataaars/svg?seed=\{n\}" for n in nombres_jugadores\}\
\
# 3. L\'d3GICA DEL FIXTURE\
def generar_fixture_28():\
    rondas_raw = [\
        [(0,1,2,3), (4,5,6,7)], [(0,2,4,6), (1,3,5,7)], [(0,3,5,6), (1,2,4,7)],\
        [(0,4,1,5), (2,6,3,7)], [(0,5,2,7), (1,4,3,6)], [(0,6,1,7), (2,4,3,5)],\
        [(0,7,3,4), (1,6,2,5)], [(0,1,4,5), (2,3,6,7)], [(0,2,1,3), (4,6,5,7)],\
        [(0,3,1,2), (5,6,4,7)], [(0,4,2,6), (1,5,3,7)], [(0,5,1,4), (2,7,3,6)],\
        [(0,6,2,4), (1,7,3,5)], [(0,7,1,6), (3,4,2,5)]\
    ]\
    data = []\
    partido_n = 1\
    for r_idx, ronda in enumerate(rondas_raw):\
        for m in ronda:\
            data.append(\{\
                "ID": partido_n, "Ronda": r_idx + 1,\
                "P1_A": nombres_jugadores[m[0]], "P1_B": nombres_jugadores[m[1]],\
                "G1": 0, "G2": 0,\
                "P2_A": nombres_jugadores[m[2]], "P2_B": nombres_jugadores[m[3]]\
            \})\
            partido_n += 1\
    return pd.DataFrame(data)\
\
# 4. MANEJO DE ESTADO (REINICIO)\
if 'df_fixture' not in st.session_state:\
    st.session_state.df_fixture = generar_fixture_28()\
\
def reiniciar():\
    st.session_state.df_fixture = generar_fixture_28()\
    st.rerun()\
\
# 5. C\'c1LCULOS\
def calcular_posiciones(df):\
    stats = \{n: \{"PJ": 0, "PG": 0, "PP": 0, "GF": 0, "GC": 0, "Pts": 0\} for n in nombres_jugadores\}\
    partidos_jugados = df[(df['G1'] > 0) | (df['G2'] > 0)]\
    for _, row in partidos_jugados.iterrows():\
        for j in [row['P1_A'], row['P1_B']]:\
            stats[j]["PJ"] += 1; stats[j]["GF"] += row['G1']; stats[j]["GC"] += row['G2']\
            if row['G1'] > row['G2']: stats[j]["PG"] += 1; stats[j]["Pts"] += 3\
            else: stats[j]["PP"] += 1; stats[j]["Pts"] += 1\
        for j in [row['P2_A'], row['P2_B']]:\
            stats[j]["PJ"] += 1; stats[j]["GF"] += row['G2']; stats[j]["GC"] += row['G1']\
            if row['G2'] > row['G1']: stats[j]["PG"] += 1; stats[j]["Pts"] += 3\
            else: stats[j]["PP"] += 1; stats[j]["Pts"] += 1\
    res = pd.DataFrame.from_dict(stats, orient='index').reset_index()\
    res.columns = ['Jugador', 'PJ', 'PG', 'PP', 'GF', 'GC', 'Pts']\
    res['Dif'] = res['GF'] - res['GC']\
    return res.sort_values(by=['Pts', 'Dif'], ascending=False)\
\
# 6. UI PRINCIPAL\
st.title("
\f1 \uc0\u55356 \u57278 
\f0  Padel Pro App")\
\
tab_pos, tab_fix, tab_admin = st.tabs(["
\f1 \uc0\u55356 \u57286 
\f0  Posiciones", "
\f1 \uc0\u55357 \u56517 
\f0  Fixture", "
\f1 \uc0\u9881 \u65039 
\f0  Ajustes"])\
\
with tab_fix:\
    st.session_state.df_fixture = st.data_editor(\
        st.session_state.df_fixture,\
        column_config=\{\
            "G1": st.column_config.NumberColumn("G1", min_value=0, max_value=4),\
            "G2": st.column_config.NumberColumn("G2", min_value=0, max_value=4),\
        \},\
        disabled=["ID", "Ronda", "P1_A", "P1_B", "P2_A", "P2_B"],\
        hide_index=True, use_container_width=True\
    )\
\
with tab_pos:\
    df_ranking = calcular_posiciones(st.session_state.df_fixture)\
    for _, row in df_ranking.iterrows():\
        c1, c2, c3, c4 = st.columns([1, 3, 2, 1])\
        c1.image(avatares[row['Jugador']], width=50)\
        c2.markdown(f"**\{row['Jugador']\}**")\
        c3.write(f"Pts: \{row['Pts']\} | Dif: \{row['Dif']\}")\
        c4.write(f"PJ: \{row['PJ']\}")\
        st.divider()\
\
with tab_admin:\
    st.subheader("Zona de Peligro")\
    if st.button("
\f1 \uc0\u55357 \u57000 
\f0  REINICIAR TODO EL TORNEO"):\
        st.warning("\'bfEst\'e1s seguro? Se borrar\'e1n todos los resultados cargados.")\
        if st.button("S\'cd, REINICIAR"):\
            reiniciar()}