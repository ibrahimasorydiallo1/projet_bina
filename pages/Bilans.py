import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Bilans", layout="wide")
st.title("📊 Tableau des marges, pertes et dépenses")

# --- FONCTION GÉNÉRATION PDF ---
def generate_pdf(df_prod, df_sal, stats):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Titre
    pdf.cell(190, 10, "Rapport de Bilan Journalier", ln=True, align='C')
    pdf.ln(10)
    
    # Section Récapitulative
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "RECAPITULATIF GLOBAL", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"- Total benefice brut : {stats['total_benefice']:,.2f} FG", ln=True)
    pdf.cell(190, 8, f"- Pertes Petits : {stats['pertes_petits']:,.2f} FG", ln=True)
    pdf.cell(190, 8, f"- Pertes Grands : {stats['pertes_grands']:,.2f} FG", ln=True)
    pdf.cell(190, 8, f"- Pertes Biscuits : {stats['pertes_biscuits']:,.2f} FG", ln=True)
    pdf.cell(190, 8, f"- Total depenses : {stats['total_salaries']:,.2f} FG", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 10, f"- BENEFICE NET : {stats['benefice_net']:,.2f} FG", ln=True)
    pdf.ln(10)

    # Note: L'ajout de tableaux complets en PDF via FPDF demande du code ligne par ligne.
    # Pour rester simple, nous listons les totaux ici.
    return pdf.output()

# ===================== Données de base produits =====================
data_produits = {
    "Date de livraison": ["11/09/2025"],
    "Quartier": ["Kipé"],
    "Petits gâteaux": [120],
    "Grands gâteaux": [50],
    "Biscuits": [200],
    "Marge/unité (FG)": [1.0],
    "Pertes (petits)": [0],
    "Pertes (grands)": [0],
    "Pertes (biscuits)": [0],
}

df_produits = pd.DataFrame(data_produits)

# ===================== Tableaux éditables =====================
st.subheader("📅 Données produits")
edited_produits = st.data_editor(df_produits, num_rows="dynamic", use_container_width=True)

st.subheader("💼 Salaires et prélèvements")
data_salaries = {
    "Employé": ["Bangaly", "Amadou", "Thierno", "Actionnaire", "Véhicule"],
    "Salaire (FG)": [1400000, 1150000, 1000000, 1000000, 500000], # Ajout d'une valeur manquante
}
df_salaries = pd.DataFrame(data_salaries)
edited_salaries = st.data_editor(df_salaries, num_rows="dynamic", use_container_width=True)

# ===================== Bouton de mise à jour et PDF =====================
if st.button("🔄 Calculer et préparer le PDF"):

    # Calculs
    edited_produits["Marge totale (FG)"] = (
        (edited_produits["Petits gâteaux"] - edited_produits["Pertes (petits)"])
        + (edited_produits["Grands gâteaux"] - edited_produits["Pertes (grands)"])
        + (edited_produits["Biscuits"] - edited_produits["Pertes (biscuits)"])
    ) * edited_produits["Marge/unité (FG)"]

    stats = {
        "total_benefice": edited_produits["Marge totale (FG)"].sum(),
        "pertes_petits": (edited_produits["Pertes (petits)"] * edited_produits["Marge/unité (FG)"]).sum(),
        "pertes_grands": (edited_produits["Pertes (grands)"] * edited_produits["Marge/unité (FG)"]).sum(),
        "pertes_biscuits": (edited_produits["Pertes (biscuits)"] * edited_produits["Marge/unité (FG)"]).sum(),
        "total_salaries": edited_salaries["Salaire (FG)"].sum()
    }
    stats["benefice_net"] = stats["total_benefice"] - stats["total_salaries"]

    st.success("✅ Calculs mis à jour !")
    
    # Affichage Récapitulatif
    st.markdown(f"### Bénéfice Net : {stats['benefice_net']:.2f} FG")

    # --- GÉNÉRATION DU PDF ---
    pdf_data = generate_pdf(edited_produits, edited_salaries, stats)
    
    st.download_button(
        label="📥 Télécharger le Bilan en PDF",
        data=bytes(pdf_data),
        file_name="bilan_journalier.pdf",
        mime="application/pdf"
    )