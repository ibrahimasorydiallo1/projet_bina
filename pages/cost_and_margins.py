import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os

st.set_page_config(page_title="Calculateur Maître Gâteaux", layout="wide")
st.title("🍰 Gestion Globale : Recettes, Prix et Marges")

# --- 1. CONFIGURATION DES FICHIERS ---
PRICES_FILE = "assets/couts_et_marges.csv"

def get_recipe_file(categorie):
    return f"assets/recette_{categorie.replace(' ', '_').lower()}.csv"

# --- 2. LOGIQUE DE SYNCHRONISATION DES PRIX ---
def load_universal_prices():
    if os.path.exists(PRICES_FILE):
        return pd.read_csv(PRICES_FILE)
    return pd.DataFrame(columns=["Matière", "Prix_unitaire_en_fg"])

def save_universal_prices(df_edited):
    df_prices = load_universal_prices()
    for _, row in df_edited.iterrows():
        matiere = row["Matière"]
        prix = row["Prix_unitaire_en_fg"]
        if matiere in df_prices["Matière"].values:
            df_prices.loc[df_prices["Matière"] == matiere, "Prix_unitaire_en_fg"] = prix
        else:
            new_row = pd.DataFrame([{"Matière": matiere, "Prix_unitaire_en_fg": prix}])
            df_prices = pd.concat([df_prices, new_row], ignore_index=True)
    df_prices.to_csv(PRICES_FILE, index=False)

# --- 3. CHARGEMENT DES DONNÉES ---
def load_recipe(categorie):
    file_path = get_recipe_file(categorie)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        # Initialisation par défaut si premier lancement
        defaults = {
            "Matière": ["Farine (gramme)", "Sucre (gramme)", "Œufs (unités)", "Arôme liquide (ml)", "Beurre (gramme)", "Lévure (gramme)", "Huile (ml)", "Tasses (unité)", "Cuillères (unité)"],
            "Quantité": [1000.0] * 9,
            "Prix_unitaire_en_fg": [0.0] * 9
        }
        df = pd.DataFrame(defaults)
    
    # APPLIQUER LES PRIX UNIVERSELS
    df_prices = load_universal_prices()
    if not df_prices.empty:
        price_dict = dict(zip(df_prices["Matière"], df_prices["Prix_unitaire_en_fg"]))
        df["Prix_unitaire_en_fg"] = df["Matière"].map(price_dict).fillna(df["Prix_unitaire_en_fg"])
    
    return df


def refresh_data():
    # On vide la session pour forcer le rechargement au prochain passage
    if "df_pour_affichage" in st.session_state:
        del st.session_state.df_pour_affichage


if "df_pour_affichage" not in st.session_state:
    st.session_state.df_pour_affichage = None

# --- 4. INTERFACE ---
choix = st.selectbox("Catégorie à gérer :",
                     ["Petits Vanilles", "Grands Vanilles", "Petits chocolat", "Grands chocolat"],
                     on_change=refresh_data)
prix_vente = 4200 if "Petits" in choix else 8500

if "df_pour_affichage" not in st.session_state or st.session_state.df_pour_affichage is None:
    # Ici, appelle la fonction load_recipe(choix) habituelle
    df_initial = load_recipe(choix) 
    df_initial["Total"] = df_initial["Quantité"] * df_initial["Prix_unitaire_en_fg"]
    st.session_state.df_pour_affichage = df_initial

st.subheader(f"Édition de la recette : {choix}")
st.info("💡 Modifier un prix ici l'appliquera automatiquement à toutes les autres recettes.")

edited_df = st.data_editor(st.session_state.df_pour_affichage,
                           use_container_width=True,
                           num_rows="fixed",
                           key=f"editor_{choix}")


if st.checkbox("🔍 Faire un calcul prévisionnel", key="activer_prevision"):
    prevision_input = st.text_input("Saisir la prévision de vente :", placeholder="1000", key="prevision_vente")

    # Traitement de la prévision
    if st.button("Calculer la prévision", key="calculer_prevision", type="primary"):
        try:
            prevision = int(prevision_input)
            
            if prevision > 0:
                # Calcul du multiplicateur
                ligne_unite = edited_df[edited_df['Matière'].str.contains('Cuillères|cuillères', case=False)]
                nb_unites = ligne_unite['Quantité'].values[0] if not ligne_unite.empty and ligne_unite['Quantité'].values[0] != 0 else 1
                # On multiplie par (Prévision / nb_unites)
                ratio = prevision / nb_unites

                # Création du tableau prévisionnel
                df_prevision = edited_df.copy()
                df_prevision["Quantité"] = round(df_prevision["Quantité"] * ratio)
                df_prevision["Total"] = df_prevision["Quantité"] * df_prevision["Prix_unitaire_en_fg"]

                st.write(f"### 📈 Estimation pour {prevision} unités")
                st.dataframe(df_prevision.style.format(subset=["Quantité", "Total"], precision=2), use_container_width=True)
                
                total_prevu = df_prevision["Total"].sum()
                st.info(f"Coût total estimé des matières : **{total_prevu:,.0f} FG**")
                # bénéfice estimé
                benefice_prevu = (prix_vente * prevision) - total_prevu
                st.info(f"Bénéfice estimé : **{benefice_prevu:,.0f} FG**")

                # EXCEL
                output_ex = BytesIO()
                with pd.ExcelWriter(output_ex, engine='openpyxl') as writer:
                    df_prevision.to_excel(writer, index=False, sheet_name='Prévision')
                st.download_button("📥 Télécharger Excel", output_ex.getvalue(), f"Prévision_{choix}.xlsx")

        except ValueError:
            st.warning("Veuillez entrer un nombre entier valide.") 


# --- CALCULS ET SAUVEGARDE ---
if st.button("🚀 Enregistrer et Générer le Bilan", type="primary"):
    # 1. Sauvegarde des prix et de la recette
    save_universal_prices(edited_df)
    edited_df[["Matière", "Quantité", "Prix_unitaire_en_fg", "Total"]].to_csv(get_recipe_file(choix), index=False)
    
    # 2. CALCUL IMMÉDIAT DU TOTAL
    # On s'assure que le calcul utilise bien les valeurs que tu viens de taper
    edited_df["Total"] = edited_df["Quantité"] * edited_df["Prix_unitaire_en_fg"]
    
    # On met à jour le dictionnaire de session pour que l'affichage suive
    st.session_state.df_pour_affichage = edited_df

    # 3. CALCULS DE SYNTHÈSE
    total_general = edited_df["Total"].sum()
    
    ligne_unite = edited_df[edited_df['Matière'].str.contains('Cuillères|cuillères', case=False)]
    nb_unites = ligne_unite['Quantité'].values[0] if not ligne_unite.empty and ligne_unite['Quantité'].values[0] != 0 else 1
    
    cout_unitaire = total_general / nb_unites
    marge_unitaire = prix_vente - cout_unitaire

    # DataFrame final pour affichage
    lignes_synthese = pd.DataFrame([
        {"Matière": "TOTAL GÉNÉRAL", "Quantité": "", "Prix_unitaire_en_fg": "", "Total": total_general},
        {"Matière": "COÛT DIRECT P/UNITÉ", "Quantité": "", "Prix_unitaire_en_fg": "", "Total": cout_unitaire},
        {"Matière": "PRIX DE VENTE", "Quantité": "", "Prix_unitaire_en_fg": "", "Total": prix_vente},
        {"Matière": "MARGE BÉNÉFICE P/UNITÉ", "Quantité": "", "Prix_unitaire_en_fg": "", "Total": marge_unitaire}
    ])
    df_final = pd.concat([edited_df, lignes_synthese], ignore_index=True)

    # Style
    def style_rows(row):
        if row["Matière"] == "MARGE BÉNÉFICE P/UNITÉ": return ['background-color: #fbc02d; font-weight: bold'] * len(row)
        if "TOTAL" in str(row["Matière"]): return ['background-color: blue'] * len(row)
        return [''] * len(row)

    st.success("Données sauvegardées et prix synchronisés !")
    st.dataframe(df_final.style.apply(style_rows, axis=1).format(subset=["Total"], precision=1), use_container_width=True)

    # EXCEL
    output_ex = BytesIO()
    with pd.ExcelWriter(output_ex, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Bilan')
    st.download_button("📥 Télécharger Excel", output_ex.getvalue(), f"Bilan_{choix}.xlsx")
            
else:
    st.info("Cliquez sur le bouton pour valider vos changements et activer la synchronisation des prix.")