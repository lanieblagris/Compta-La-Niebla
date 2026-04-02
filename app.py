import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

st.title("🥷 Portail Officiel - La Niebla")
st.markdown("---")

# Connexion
conn = st.connection("gsheets", type=GSheetsConnection)

# Création des onglets
tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

def handle_submit(membre, action, butin=0, drogue="N/A", quantite=0):
    if not membre:
        st.error("Entre ton nom !")
        return

    try:
        # 1. On lit les données
        df = conn.read(worksheet="Rapports", ttl=0)
    except:
        # Si la feuille est vide, on crée les colonnes
        df = pd.DataFrame(columns=["Date", "Membre", "Action", "Drogue", "Quantite", "Butin"])

    # 2. On ajoute la nouvelle ligne
    new_row = pd.DataFrame([{
        "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Membre": membre,
        "Action": action,
        "Drogue": drogue,
        "Quantite": quantite,
        "Butin": butin
    }])
    
    updated_df = pd.concat([df, new_row], ignore_index=True)

    # 3. On met à jour (On utilise la méthode simple)
    conn.update(worksheet="Rapports", data=updated_df)
    st.success(f"Rapport {action} enregistré !")
    st.balloons()

# Formulaires
with tabs[0]: # ATM
    with st.form("atm"):
        m = st.text_input("Membre")
        b = st.number_input("Butin ($)", min_value=0)
        if st.form_submit_button("Valider"):
            handle_submit(m, "ATM", butin=b)

with tabs[1]: # Supérette
    with st.form("sup"):
        m = st.text_input("Membre")
        b = st.number_input("Butin ($)", min_value=0)
        if st.form_submit_button("Valider"):
            handle_submit(m, "Supérette", butin=b)

with tabs[2]: # Go Fast
    with st.form("gf"):
        m = st.text_input("Membre")
        b = st.number_input("Butin ($)", min_value=0)
        if st.form_submit_button("Valider"):
            handle_submit(m, "Go Fast", butin=b)

with tabs[3]: # Cambriolage
    with st.form("cam"):
        m = st.text_input("Membre")
        if st.form_submit_button("Valider"):
            handle_submit(m, "Cambriolage")

with tabs[4]: # Drogue
    with st.form("dr"):
        m = st.text_input("Membre")
        d = st.text_input("Type de drogue")
        q = st.number_input("Quantité", min_value=0)
        b = st.number_input("Prix total ($)", min_value=0)
        if st.form_submit_button("Valider"):
            handle_submit(m, "Drogue", butin=b, drogue=d, quantite=q)
