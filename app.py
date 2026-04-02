import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuration de la page
st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

# Style sombre pour l'immersion (CORRIGÉ : unsafe_allow_html)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥷 Portail Officiel - La Niebla")
st.markdown("---")

# Connexion au Google Sheet via les Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Création des onglets
tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

# --- FONCTION D'ENREGISTREMENT ---
def handle_submit(membre, action, butin=0, drogue="N/A", quantite=0):
    if not membre:
        st.error("L'ombre n'a pas de nom... Entre ton pseudo.")
        return

    try:
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DP_SfWdXadALyqUGW91wkCONK2_8asUBTnGGczmIA20/edit#gid=0"
        
        # Préparation de la ligne de données
        new_row = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Membre": membre,
            "Action": action,
            "Drogue": drogue,
            "Quantite": quantite,
            "Butin": butin
        }])
        
        # Ajout direct dans le Sheets
        conn.create(spreadsheet=spreadsheet_url, worksheet="Rapports", data=new_row)
        
        # Effet visuel "Brouillard"
        st.snow() 
        st.success(f"L'opération {action} a été archivée dans la brume...")
        
    except Exception as e:
        st.error(f"Le brouillard est trop épais, erreur : {e}")

# --- FORMULAIRES ---

with tabs[0]: # ATM
    with st.form("atm"):
        m_atm = st.text_input("Membre", placeholder="Ton pseudo", key="k_atm_m")
        b_atm = st.number_input("Butin récolté ($)", min_value=0, key="k_atm_b")
        if st.form_submit_button("Valider ATM"):
            handle_submit(m_atm, "ATM", butin=b_atm)

with tabs[1]: # SUPERETTE
    with st.form("sup"):
        m_sup = st.text_input("Membre", placeholder="Ton pseudo", key="k_sup_m")
        b_sup = st.number_input("Butin récolté ($)", min_value=0, key="k_sup_b")
        if st.form_submit_button("Valider Supérette"):
            handle_submit(m_sup, "Supérette", butin=b_sup)

with tabs[2]: # GO FAST
    with st.form("gf"):
        m_gf = st.text_input("Membre", placeholder="Ton pseudo", key="k_gf_m")
        b_gf = st.number_input("Butin récolté ($)", min_value=0, key="k_gf_b")
        if st.form_submit_button("Valider Go Fast"):
            handle_submit(m_gf, "Go Fast", butin=b_gf)

with tabs[3]: # CAMBRIOLAGE
    with st.form("cam"):
        m_cam = st.text_input("Membre", placeholder="Ton pseudo", key="k_cam_m")
        if st.form_submit_button("Valider Cambriolage"):
            handle_submit(m_cam, "Cambriolage")

with tabs[4]: # DROGUE
    with st.form("dr"):
        m_dr = st.text_input("Membre", placeholder="Ton pseudo", key="k_dr_m")
        d_dr = st.text_input("Type de produit", placeholder="Ex: Weed, Coke...", key="k_dr_d")
        q_dr = st.number_input("Quantité", min_value=0, key="k_dr_q")
        b_dr = st.number_input("Total vente ($)", min_value=0, key="k_dr_b")
        if st.form_submit_button("Valider Vente"):
            handle_submit(m_dr, "Drogue", butin=b_dr, drogue=d_dr, quantite=q_dr)
