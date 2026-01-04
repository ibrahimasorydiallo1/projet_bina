import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Calculateur de Marges Gâteaux", layout="wide")
st.title("🍰 Calculateur avec Lignes de Synthèse Colorées")

# 1. Données par défaut
data_chocolat = {
    "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Cacao (unité)", 
                "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],
    "Quantité": [1400.0, 2900.0, 70.0, 40.0, 200.0, 3400.0, 80.0, 700.0, 130.0, 130.0],
    "Prix unitaire en fg": [7.2, 7.5, 1666.0, 600.0, 45.3, 24.5, 72.0, 24.0, 800.0, 67.5]
}

data_vanille = {
    "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Citron (unité)", 
                "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],
    "Quantité": [1600.0, 2900.0, 100.0, 40.0, 4.0, 3400.0, 80.0, 500.0, 140.0, 140.0],
    "Prix unitaire en fg": [7.2, 7.5, 1666.0, 600.0, 1000.0, 24.5, 72.0, 24.0, 800.0, 67.5]
}

choix = st.selectbox("Sélectionnez la catégorie :", ["Petits Vanilles", "Grands Vanilles", "Petits chocolat", "Grands chocolat"])

# Logique de base
if "chocolat" in choix.lower():
    df = pd.DataFrame(data_chocolat)
    prix_vente = 4200 if "Petits" in choix else 8500
else:
    df = pd.DataFrame(data_vanille)
    prix_vente = 4200 if "Petits" in choix else 8500

# 2. Calculs
df["Total"] = df["Quantité"] * df["Prix unitaire en fg"]

total_general = df["Total"].sum()
total_cout_direct_u = df["Prix unitaire en fg"].sum()
nb_unites = df.loc[df['Matière'].str.contains('Cuillères|cuillères'), 'Quantité'].values[0]
cout_unitaire = total_general / nb_unites
marge_unitaire = prix_vente - cout_unitaire

# 3. Ajout des lignes de synthèse au DataFrame
lignes_synthese = pd.DataFrame([
    {"Matière": "TOTAL GÉNÉRAL", "Quantité": "", "Prix unitaire en fg": "", "Total": total_general},
    {"Matière": "COÛT DIRECT P/UNITÉ", "Quantité": "", "Prix unitaire en fg": "", "Total": cout_unitaire},
    {"Matière": "PRIX DE VENTE", "Quantité": "", "Prix unitaire en fg": "", "Total": prix_vente},
    {"Matière": "MARGE BÉNÉFICE P/UNITÉ", "Quantité": "", "Prix unitaire en fg": "", "Total": marge_unitaire}
])

df_final = pd.concat([df, lignes_synthese], ignore_index=True)

# 4. Fonction de coloration
def colorer_lignes(row):
    # On définit les couleurs selon le texte de la colonne 'Matière'
    if row["Matière"] == "TOTAL GÉNÉRAL":
        return ['background-color: green'] * len(row)  # Bleu clair
    elif row["Matière"] == "COÛT DIRECT P/UNITÉ":
        return ['background-color: blue'] * len(row)  # Jaune/Orange
    elif row["Matière"] == "PRIX DE VENTE":
        return ['background-color: orange'] * len(row)  # Rouge clair
    elif row["Matière"] == "MARGE BÉNÉFICE P/UNITÉ":
        return ['background-color: yellow; font-weight: bold'] * len(row)  # Vert
    return [''] * len(row)

# 5. Affichage avec Style
st.subheader("Détails et synthèses:")
st.dataframe(df_final.style.apply(colorer_lignes, axis=1).format(subset=["Total"], precision=2))

# --- BLOC EXPORT EXCEL ---
st.divider()
st.subheader("Exporter les données")

# 1. Préparation du fichier Excel en mémoire
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    # On exporte le DataFrame final (celui qui contient les lignes de calculs)
    df_final.to_excel(writer, index=False, sheet_name='Analyse_Couts')

# 2. Bouton de téléchargement Streamlit
st.download_button(
    label="📥 Télécharger le rapport (Excel)",
    data=output.getvalue(),
    file_name=f"Rapport_Couts_{choix.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.info(f"Le calcul est basé sur une production de {nb_unites} unités.")