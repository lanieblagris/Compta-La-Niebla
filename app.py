import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

st.title("🥷 Portail Officiel - La Niebla")
st.markdown("---")

# Connexion au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Création des onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

# FONCTION POUR SAUVEGARDER
def save_report(membre, action, butin=0, drogue="N/A", quantite=0):
    try:
        # On essaie de lire les données, si vide on crée la structure
        existing_data = conn.read(worksheet="Rapports")
    except:
        existing_data = pd.DataFrame(columns=["Date", "Membre", "Action", "Drogue", "Quantite", "Butin"])
    
    new_report = pd.DataFrame([{
        "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Membre": membre,
        "Action": action,
        "Drogue": drogue,
        "Quantite": quantite,
        "Butin": butin
    }])
    
    # Ajout de la nouvelle ligne
    updated_df = pd.concat([existing_data, new_report], ignore_index=True)
    conn.update(worksheet="Rapports", data=updated_df)
    st.success(f"Rapport {action} enregistré !")
    st.balloons()

# --- ATM ---
with tab1:
    with st.form("form_atm"):
        m = st.text_input("Membre", placeholder="Ton pseudo RP")
        b = st.number_input("Butin récolté ($)", min_value=0)
        if st.form_submit_button("Valider ATM"):
            save_report(m, "ATM", butin=b)

# --- SUPERETTE ---
with tab2:
    with st.form("form_superette"):
        m = st.text_input("Membre", placeholder="Ton pseudo RP")
        b = st.number_input("Butin récolté ($)", min_value=0)
        if st.form_submit_button("Valider Supérette"):
            save_report(m, "Supérette", butin=b)

# --- GO FAST ---
with tab3:
    with st.form("form_gofast"):
        m = st.text_input("Membre", placeholder="Ton pseudo RP")
        b = st.number_input("Butin récolté ($)", min_value=0)
        if st.form_submit_button("Valider Go Fast"):
            save_report(m, "Go Fast", butin=b)

# --- CAMBRIOLAGE ---
with tab4:
    with st.form("form_cambriolage"):
        m = st.text_input("Membre", placeholder="Ton pseudo RP")
        if st.form_submit_button("Valider Cambriolage"):
            save_report(m, "Cambriolage")

# --- DROGUE (Saisie libre) ---
with tab5:
    with st.form("form_drogue"):
        m = st.text_input("Membre", placeholder="Ton pseudo RP")
        d = st.text_input("Type de drogue", placeholder="Ex: Weed, Coke, Meth...") # Changé ici
        q = st.number_input("Quantité vendue", min_value=0)
        b = st.number_input("Prix de vente total ($)", min_value=0)
        if st.form_submit_button("Valider Vente"):
            save_report(m, "Drogue", butin=b, drogue=d, quantite=q)
