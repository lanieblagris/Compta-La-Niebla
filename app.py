import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuration de la page
st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

# Style sombre
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥷 Portail Officiel - La Niebla")
st.markdown("---")

# Connexion (elle va chercher l'url dans tes secrets automatiquement)
conn = st.connection("gsheets", type=GSheetsConnection)

tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

def handle_submit(membre, action, butin=0, drogue="N/A", quantite=0):
    if not membre:
        st.error("L'ombre n'a pas de nom... Entre ton pseudo.")
        return

    try:
        # Préparation de la ligne
        new_row = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Membre": membre,
            "Action": action,
            "Drogue": drogue,
            "Quantite": quantite,
            "Butin": butin
        }])
        
        # LECTURE PUIS AJOUT (Plus stable pour cette bibliothèque)
        existing_data = conn.read(worksheet="Rapports", ttl=0)
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        
        # MISE À JOUR
        conn.update(worksheet="Rapports", data=updated_df)
        
        st.snow() 
        st.success(f"L'opération {action} a été archivée dans la brume...")
        
    except Exception as e:
        st.error(f"Le brouillard est trop épais, erreur : {e}")

# --- FORMULAIRES (Clés uniques k_) ---
with tabs[0]:
    with st.form("atm"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="k_m_atm")
        b = st.number_input("Butin récolté ($)", min_value=0, key="k_b_atm")
        if st.form_submit_button("Valider ATM"):
            handle_submit(m, "ATM", butin=b)

with tabs[1]:
    with st.form("sup"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="k_m_sup")
        b = st.number_input("Butin récolté ($)", min_value=0, key="k_b_sup")
        if st.form_submit_button("Valider Supérette"):
            handle_submit(m, "Supérette", butin=b)

with tabs[2]:
    with st.form("gf"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="k_m_gf")
        b = st.number_input("Butin récolté ($)", min_value=0, key="k_b_gf")
        if st.form_submit_button("Valider Go Fast"):
            handle_submit(m, "Go Fast", butin=b)

with tabs[3]:
    with st.form("cam"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="k_m_cam")
        if st.form_submit_button("Valider Cambriolage"):
            handle_submit(m, "Cambriolage")

with tabs[4]:
    with st.form("dr"):
        m = st.text_input("Membre", placeholder="Ton pseudo", key="k_m_dr")
        d = st.text_input("Type de produit", placeholder="Ex: Weed...", key="k_d_dr")
        q = st.number_input("Quantité", min_value=0, key="k_q_dr")
        b = st.number_input("Total vente ($)", min_value=0, key="k_b_dr")
        if st.form_submit_button("Valider Vente"):
            handle_submit(m, "Drogue", butin=b, drogue=d, quantite=q)
