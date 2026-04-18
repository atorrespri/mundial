import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import io

st.set_page_config(layout="wide")
st.title("🏆 Mundial 2026 - Simulación Profesional")

# -------------------------
# BRACKET VISUAL
# -------------------------
def mostrar_bracket_html(r32, r16, r8, r4, final):

    def col(teams):
        return "".join([f"<div class='team'>{t}</div>" for t in teams])

    html = f"""
    <html>
    <style>
    body {{ background:#0f172a; color:white; font-family:Arial; }}
    .container {{ display:flex; justify-content:space-around; }}
    .column {{ display:flex; flex-direction:column; }}
    .team {{ background:#1e293b; margin:5px; padding:6px; border-radius:6px; }}
    h3 {{ text-align:center; }}
    </style>
    <div class="container">
        <div class="column"><h3>16avos</h3>{col(r32)}</div>
        <div class="column"><h3>Octavos</h3>{col(r16)}</div>
        <div class="column"><h3>Cuartos</h3>{col(r8)}</div>
        <div class="column"><h3>Semifinal</h3>{col(r4)}</div>
        <div class="column"><h3>Final</h3>{col(final)}</div>
    </div>
    </html>
    """
    components.html(html, height=700)

# -------------------------
# GRUPOS
# -------------------------
groups = {
    "A": ["México", "Sudáfrica", "Corea del Sur", "Chequia"],
    "B": ["Canadá", "Bosnia y Hezegovina", "Qatar", "Suiza"],
    "C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "I": ["Francia", "Senegal", "Irak", "Noruega"],
    "J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "K": ["Portugal", "R.D. Congo", "Uzbekistán", "Colombia"],
    "L": ["Inglaterra", "Croacia", "Ghana", "Panamá"],
}

# -------------------------
# FUNCIONES
# -------------------------
def init_table(teams):
    return pd.DataFrame({"Equipo": teams, "Pts": 0, "GF": 0, "GC": 0})

def update_table(table, t1, g1, g2, t2):
    table.loc[table.Equipo == t1, ["GF","GC"]] += [g1, g2]
    table.loc[table.Equipo == t2, ["GF","GC"]] += [g2, g1]

    if g1 > g2:
        table.loc[table.Equipo == t1, "Pts"] += 3
    elif g2 > g1:
        table.loc[table.Equipo == t2, "Pts"] += 3
    else:
        table.loc[table.Equipo == t1, "Pts"] += 1
        table.loc[table.Equipo == t2, "Pts"] += 1

    return table

# -------------------------
# FASE DE GRUPOS
# -------------------------
st.header("📊 Fase de grupos")

group_winners, group_seconds, thirds = [], [], []
group_tables = {}

for g, teams in groups.items():
    st.subheader(f"Grupo {g}")
    table = init_table(teams)

    matches = [(0,1),(2,3),(0,2),(1,3),(0,3),(1,2)]

    for i,(a,b) in enumerate(matches):
        t1, t2 = teams[a], teams[b]

        col1,col2,col3 = st.columns(3)
        col1.write(f"{t1} vs {t2}")
        g1 = col2.number_input("", key=f"{g}{i}1", min_value=0)
        g2 = col3.number_input("", key=f"{g}{i}2", min_value=0)

        table = update_table(table, t1, g1, g2, t2)

    table["DG"] = table["GF"] - table["GC"]
    table = table.sort_values(by=["Pts","DG","GF"], ascending=False)

    st.dataframe(table)
    group_tables[g] = table

    group_winners.append(table.iloc[0]["Equipo"])
    group_seconds.append(table.iloc[1]["Equipo"])
    thirds.append(table.iloc[2])

# -------------------------
# MEJORES TERCEROS
# -------------------------
thirds_df = pd.DataFrame(thirds)
best_thirds = thirds_df.sort_values(by=["Pts","DG","GF"], ascending=False).head(8)

qualified = group_winners + group_seconds + list(best_thirds["Equipo"])

# -------------------------
# ELIMINACIÓN CON PENALES
# -------------------------
def play_round(teams, name):
    winners = []
    st.subheader(f"⚔️ {name}")

    for i in range(0, len(teams), 2):
        t1, t2 = teams[i], teams[i+1]

        col1, col2, col3, col4, col5 = st.columns([3,1,1,1,3])

        col1.markdown(f"### {t1}")
        g1 = col2.number_input("", key=f"{name}_{i}_g1", min_value=0)
        col3.markdown("### -")
        g2 = col4.number_input("", key=f"{name}_{i}_g2", min_value=0)
        col5.markdown(f"### {t2}")

        if g1 > g2:
            winners.append(t1)
            st.success(f"{t1} avanza")

        elif g2 > g1:
            winners.append(t2)
            st.success(f"{t2} avanza")

        else:
            st.warning("Empate → definir por penales")

            p1 = st.number_input("Penales equipo 1", key=f"{name}_{i}_p1", min_value=0)
            p2 = st.number_input("Penales equipo 2", key=f"{name}_{i}_p2", min_value=0)

            if p1 > p2:
                winners.append(t1)
                st.success(f"{t1} gana en penales")
            elif p2 > p1:
                winners.append(t2)
                st.success(f"{t2} gana en penales")
            else:
                st.error("No puede haber empate en penales")
                return []

        st.divider()

    return winners

knockout_data = {}

if len(qualified) == 32:

    r32 = play_round(qualified,"16avos")
    if r32:
        r16 = play_round(r32,"Octavos")
    if r32 and r16:
        r8 = play_round(r16,"Cuartos")
    if r32 and r16 and r8:
        r4 = play_round(r8,"Semifinal")
    if r32 and r16 and r8 and r4:
        final = play_round(r4,"Final")

        knockout_data = {
            "16avos":r32,"Octavos":r16,"Cuartos":r8,
            "Semifinal":r4,"Final":final
        }

        st.success(f"🏆 Campeón: {final[0]}")
        mostrar_bracket_html(r32,r16,r8,r4,final)

# -------------------------
# EXPORTAR A EXCEL
# -------------------------
def exportar_excel():
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

        for g,df in group_tables.items():
            df.to_excel(writer, sheet_name=f"Grupo {g}", index=False)

        best_thirds.to_excel(writer, sheet_name="Mejores terceros", index=False)

        pd.DataFrame({"Equipo":qualified}).to_excel(
            writer, sheet_name="Clasificados", index=False
        )

        for k,v in knockout_data.items():
            pd.DataFrame({"Equipos":v}).to_excel(
                writer, sheet_name=k, index=False
            )

    output.seek(0)
    return output

st.download_button(
    "📥 Descargar Excel completo",
    data=exportar_excel(),
    file_name="mundial_pro.xlsx"
)