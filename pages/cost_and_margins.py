import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Calculateur de Marges Gâteaux", layout="wide")
st.title("🍰 Calculateur de Production")

# 1. Données par défaut (Variables corrigées)
petit_chocolat = {

    "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Cacao (unité)",
                "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],

    "Quantité": [1400, 2900, 70, 40, 200, 3400, 80, 700, 130, 130],
    "Prix unitaire en fg": [7.2, 7.5, 1666, 600, 45.3, 24.5, 72, 24, 800, 67.5]
}

grand_chocolat = {
    "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Cacao (unité)",
                "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],

    "Quantité": [1400, 2900, 70, 40, 200, 3400, 80, 700, 70, 70],
    "Prix unitaire en fg": [7.2, 7.5, 1666, 600, 45.3, 24.5, 72, 24, 1100, 67.5]

}

petit_vanille = {
    "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Citron (unité)",
                "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],

    "Quantité": [1600, 2900, 100, 40, 4, 3400, 80, 500, 140, 140],
    "Prix unitaire en fg": [7.2, 7.5, 1666, 600, 1000, 24.5, 72, 24, 800, 67.5]
}

grand_vanille = {
    "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Citron (unité)",
                "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],

    "Quantité": [1600, 2900, 100, 40, 4, 3400, 80, 500, 70, 70],
    "Prix unitaire en fg": [7.2, 7.5, 1666, 600, 1000, 24.5, 72, 24, 1000, 67.5]
} 

# Sélection de la catégorie
choix = st.selectbox("Sélectionnez la catégorie :", ["Petits Vanilles", "Grands Vanilles", "Petits chocolat", "Grands chocolat"])

# Association du choix à la bonne variable
if choix == "Petits chocolat": base_data = petit_chocolat
elif choix == "Grands chocolat": base_data = grand_chocolat
elif choix == "Petits Vanilles": base_data = petit_vanille
else: base_data = grand_vanille

prix_vente = 4200 if "Petits" in choix else 8500

# 2. Interface d'édition
st.subheader(f"Modifier les entrées pour : {choix}")
df_editable = pd.DataFrame(base_data)
# On ajoute la colonne Total pour l'édition initiale
df_editable["Total"] = df_editable["Quantité"] * df_editable["Prix unitaire en fg"]
data_utilisateur = st.data_editor(df_editable, use_container_width=True)

# 3. BOUTON DE CONFIRMATION
if st.button("🚀 Confirmer et Générer les Totaux"):
    
    # Recalcul basé sur les entrées utilisateur
    data_utilisateur["Total"] = data_utilisateur["Quantité"] * data_utilisateur["Prix unitaire en fg"]
    
    total_general = data_utilisateur["Total"].sum()
    # On récupère le nombre de cuillères (unités produites)
    ligne_unite = data_utilisateur[data_utilisateur['Matière'].str.contains('Cuillères|cuillères')]
    nb_unites = ligne_unite['Quantité'].values[0] if not ligne_unite.empty else 1
    
    cout_unitaire = total_general / nb_unites
    marge_unitaire = prix_vente - cout_unitaire

    # Création des lignes de synthèse
    lignes_synthese = pd.DataFrame([
        {"Matière": "TOTAL GÉNÉRAL", "Quantité": "", "Prix unitaire en fg": "", "Total": total_general},
        {"Matière": "COÛT DIRECT P/UNITÉ", "Quantité": "", "Prix unitaire en fg": "", "Total": cout_unitaire},
        {"Matière": "PRIX DE VENTE", "Quantité": "", "Prix unitaire en fg": "", "Total": prix_vente},
        {"Matière": "MARGE BÉNÉFICE P/UNITÉ", "Quantité": "", "Prix unitaire en fg": "", "Total": marge_unitaire}
    ])

    df_final = pd.concat([data_utilisateur, lignes_synthese], ignore_index=True)

    # Fonction de coloration
    def colorer_lignes(row):
        if row["Matière"] == "TOTAL GÉNÉRAL": return ['background-color: #2e7d32; color: white'] * len(row) # Vert foncé
        if row["Matière"] == "COÛT DIRECT P/UNITÉ": return ['background-color: #1565c0; color: white'] * len(row) # Bleu
        if row["Matière"] == "PRIX DE VENTE": return ['background-color: #ef6c00; color: white'] * len(row) # Orange
        if row["Matière"] == "MARGE BÉNÉFICE P/UNITÉ": return ['background-color: #fbc02d; color: black; font-weight: bold'] * len(row) # Jaune
        return [''] * len(row)

    # Affichage du résultat final
    st.subheader("📊 Résultats de l'Analyse")
    st.dataframe(df_final.style.apply(colorer_lignes, axis=1).format(subset=["Total"], precision=2), use_container_width=True)

    # 4. EXPORT EXCEL
    st.divider()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Analyse_Couts')
    
    st.download_button(
        label="📥 Télécharger le rapport Excel",
        data=output.getvalue(),
        file_name=f"Rapport_{choix.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.success(f"Analyse terminée pour {nb_unites} unités !")
else:
    st.info("Modifiez les valeurs ci-dessus si nécessaire, puis cliquez sur le bouton pour générer l'analyse.")