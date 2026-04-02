import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

st.title("🥷 Portail Officiel - La Niebla")
st.markdown("---")

# Connexion forcée via les Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

def handle_submit(membre, action, butin=0, drogue="N/A", quantite=0):
    if not membre:
        st.error("Pseudo manquant !")
        return

    try:
        # ON FORCE L'OUVERTURE AVEC L'URL PRÉCISE POUR ÉVITER LE "NOT FOUND"
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DP_SfWdXadALyqUGW91wkCONK2_8asUBTnGGczmIA20/edit#gid=0"
        
        # Lecture (ttl=0 pour éviter le cache)
        df = conn.read(spreadsheet=spreadsheet_url, worksheet="Rapports", ttl=0)
        
        # Nouveau rapport
        new_row = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Membre": membre,
            "Action": action,
            "Drogue": drogue,
            "Quantite": quantite,
            "Butin": butin
        }])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)

        # Écriture forcée sur l'URL
        conn.update(spreadsheet=spreadsheet_url, worksheet="Rapports", data=updated_df)
        
        st.success(f"Rapport {action} enregistré dans le Sheets !")
        st.balloons()
    except Exception as e:
        st.error(f"Détail de l'erreur : {e}")

# --- FORMULAIRES ---
with tabs[0]:
    with st.form("atm"):
        m = st.text_input("Membre", key="atm_m")
        b = st.number_input("Butin ($)", min_value=0, key="atm_b")
        if st.form_submit_button("Valider ATM"):
            handle_submit(m, "ATM", butin=b)

with tabs[1]:
    with st.form("sup"):
        m = st.text_input("Membre", key="sup_m")
        b = st.number_input("Butin ($)", min_value=0, key="sup_b")
        if st.form_submit_button("Valider Supérette"):
            handle_submit(m, "Supérette", butin=b)

with tabs[2]:
    with st.form("gf"):
        m = st.text_input("Membre", key="gf_m")
        b = st.number_input("Butin ($)", min_value=0, key="gf_b")
        if st.form_submit_button("Valider Go Fast"):
            handle_submit(m, "Go Fast", butin=b)

with tabs[3]:
    with st.form("cam"):
        m = st.text_input("Membre", key="cam_m")
        if st.form_submit_button("Valider Cambriolage"):
            handle_submit(m, "Cambriolage")

with tabs[4]:
    with st.form("dr"):
        m = st.text_input("Membre", key="dr_m")
        d = st.text_input("Type de drogue", key="dr_d")
        q = st.number_input("Quantité", min_value=0, key="dr_q")
        b = st.number_input("Total ($)", min_value=0, key="dr_b")
        if st.form_submit_button("Valider Vente"):
            handle_submit(m, "Drogue", butin=b, drogue=d, quantite=q)
