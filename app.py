import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuration de la page
st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

# Style sombre pour l'immersion
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #ffffff; }
    </style>
    """, unsafe_content_label=True)

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
        # URL de ton Sheets (ne pas modifier)
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
        st.error(f"Le brouillard est trop épais, erreur de connexion : {e}")

# --- FORMULAIRES ---

with tabs[0]: # ATM
    with st.form("atm"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="atm_m")
        b = st.number_input("Butin récolté ($)", min_value=0, key="atm_b")
        if st.form_submit_button("Valider ATM"):
            handle_submit(m, "ATM", butin=b)

with tabs[1]: # SUPERETTE
    with st.form("sup"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="sup_m")
        b = st.number_input("Butin récolté ($)", min_value=0, key="sup_b")
        if st.form_submit_button("Valider Supérette"):
            handle_submit(m, "Supérette", butin=b)

with tabs[2]: # GO FAST
    with st.form("gf"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="gf_m")
        b = st.number_input("Butin récolté ($)", min_value=0, key="gf_b")
        if st.form_submit_button("Valider Go Fast"):
            handle_submit(m, "Go Fast", butin=b)

with tabs[3]: # CAMBRIOLAGE
    with st.form("cam"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="cam_m")
        if st.form_submit_button("Valider Cambriolage"):
            handle_submit(m, "Cambriolage")

with tabs[4]: # DROGUE
    with st.form("dr"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="dr_m")
        d = st.text_input("Type de produit", placeholder="Ex: Weed, Coke...",
