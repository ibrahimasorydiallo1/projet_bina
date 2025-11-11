import streamlit as st
import pandas as pd
import datetime

st.title("📊 Tableau des marges, pertes et dépenses par quartier et produit")

# ===================== Données de base produits =====================
quartiers = [
    "Centre", "Ouest", "Nord", "Sud", "Est",
    "Nord-Ouest", "Nord-Est", "Sud-Ouest", "Sud-Est", "Périphérie"
]

dates_livraison = ["08 sept"] * len(quartiers)

data_produits = {
    "Mois": ["20250921"] * len(quartiers),  # colonne Mois conservée
    "Date de livraison": dates_livraison,
    "Quartier": quartiers,
    "Petits gâteaux": [120, 80, 100, 75, 95, 90, 60, 110, 70, 50],
    "Grands gâteaux": [50, 40, 60, 30, 45, 55, 35, 65, 25, 20],
    "Biscuits": [200, 180, 220, 150, 170, 160, 140, 210, 130, 100],
    "Marge/unité (€)": [1.0] * len(quartiers),
    "Pertes (petits)": [0] * len(quartiers),
    "Pertes (grands)": [0] * len(quartiers),
    "Pertes (biscuits)": [0] * len(quartiers),
}

df_produits = pd.DataFrame(data_produits)

# Calcul marge totale
df_produits["Marge totale (€)"] = (
    (df_produits["Petits gâteaux"] - df_produits["Pertes (petits)"])
    + (df_produits["Grands gâteaux"] - df_produits["Pertes (grands)"])
    + (df_produits["Biscuits"] - df_produits["Pertes (biscuits)"])
) * df_produits["Marge/unité (€)"]

# ===================== Filtres Mois et Année =====================
st.sidebar.header("🗓️ Filtres")

current_year = datetime.datetime.now().year
annees = [str(y) for y in range(2020, current_year + 1)]
mois = [f"{m:02d}" for m in range(1, 13)]

annee_sel = st.sidebar.selectbox("Choisir l'année", annees, index=len(annees)-1)
mois_sel = st.sidebar.selectbox("Choisir le mois", mois, index=8)

# Filtrage via la colonne Mois (AAAAMMJJ)
filtered_produits = df_produits[df_produits["Mois"].str.startswith(annee_sel + mois_sel)].copy()

# Filtre quartier
quartier_sel = st.sidebar.multiselect(
    "Filtrer par quartier",
    options=quartiers,
    default=quartiers
)
filtered_produits = filtered_produits[filtered_produits["Quartier"].isin(quartier_sel)]

# ===================== Tableau éditable produits =====================
st.subheader(f"📅 Données produits")
edited_produits = st.data_editor(filtered_produits, num_rows="fixed", use_container_width=True)

# ===================== Tableau salaires et prélèvements =====================
st.subheader("💼 Salaires et prélèvements des employés")

data_salaries = {
    "Employé": ["Alice", "Bob", "Charlie", "David", "Eva"],
    "Salaire (€)": [2000, 2200, 1800, 2100, 1900],
    "Farine (€)": [100, 120, 90, 110, 95],
    "Œufs (€)": [50, 60, 45, 55, 50],
    "Autres intrants (€)": [30, 40, 25, 35, 30]
}
df_salaries = pd.DataFrame(data_salaries)

edited_salaries = st.data_editor(df_salaries, num_rows="fixed", use_container_width=True)

# ===================== Bouton de mise à jour =====================
if st.button("🔄 Mettre à jour marges, pertes et dépenses"):

    # Recalcul marge totale produits
    edited_produits["Marge totale (€)"] = (
        (edited_produits["Petits gâteaux"] - edited_produits["Pertes (petits)"])
        + (edited_produits["Grands gâteaux"] - edited_produits["Pertes (grands)"])
        + (edited_produits["Biscuits"] - edited_produits["Pertes (biscuits)"])
    ) * edited_produits["Marge/unité (€)"]

    # Totaux produits
    total_benefice = edited_produits["Marge totale (€)"].sum()
    pertes_petits = (edited_produits["Pertes (petits)"] * edited_produits["Marge/unité (€)"]).sum()
    pertes_grands = (edited_produits["Pertes (grands)"] * edited_produits["Marge/unité (€)"]).sum()
    pertes_biscuits = (edited_produits["Pertes (biscuits)"] * edited_produits["Marge/unité (€)"]).sum()

    # Totaux salaires et prélèvements
    total_salaries = edited_salaries["Salaire (€)"].sum()
    total_farine = edited_salaries["Farine (€)"].sum()
    total_oeufs = edited_salaries["Œufs (€)"].sum()
    total_autres = edited_salaries["Autres intrants (€)"].sum()
    total_prelevements = total_salaries + total_farine + total_oeufs + total_autres

    # Bénéfice net après salaires et prélèvements
    benefice_net = total_benefice - total_prelevements

    st.success("✅ Données mises à jour avec succès !")
    st.dataframe(edited_produits, use_container_width=True)
    st.dataframe(edited_salaries, use_container_width=True)

    st.subheader("💰 Récapitulatif global")
    st.markdown(f"""
    - **Total bénéfice brut :** {total_benefice:.2f} €  
    - **Pertes :**
        - Petits gâteaux : {pertes_petits:.2f} €  
        - Grands gâteaux : {pertes_grands:.2f} €  
        - Biscuits : {pertes_biscuits:.2f} €  
    - **Dépenses :**
        - Total salaires : {total_salaries:.2f} €  
        - Farine : {total_farine:.2f} €  
        - Œufs : {total_oeufs:.2f} €  
        - Autres intrants : {total_autres:.2f} €  
    - **Bénéfice net (après salaires et prélèvements) :** {benefice_net:.2f} €
    """)
else:
    st.info("Modifie les valeurs dans les tableaux ci-dessus, puis clique sur le bouton pour recalculer marges, pertes et dépenses.")
