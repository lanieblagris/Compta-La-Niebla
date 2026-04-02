import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuration de la page
st.set_page_config(page_title="La Niebla - Rapports", page_icon="🥷", layout="centered")

# --- DESIGN CUSTOM CSS ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1c1f26 100%);
    }
    
    /* Animation du message qui défile (Le Brouillard) */
    .brouillard-text {
        font-family: 'Courier New', monospace;
        color: rgba(255, 255, 255, 0.6);
        font-size: 20px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 5px;
        filter: blur(1px); /* Effet flou pour le brouillard */
        padding: 10px 0;
        border-top: 1px solid rgba(255,255,255,0.1);
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* Titre principal */
    h1 {
        color: #ffffff;
        text-shadow: 2px 2px 20px rgba(255,255,255,0.3);
        font-family: 'Courier New', Courier, monospace;
        text-align: center;
        padding-top: 30px;
    }

    /* Style des onglets (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 5px 5px 0px 0px;
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important;
        border-color: #ff4b4b !important;
    }

    /* Formulaires */
    .stForm {
        border: 1px solid #444;
        border-radius: 15px;
        background-color: rgba(38, 39, 48, 0.6);
    }

    /* Bouton */
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ffffff;
        color: #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MESSAGE DÉFILANT (LE BROUILLARD) ---
st.markdown("""
    <marquee class="brouillard-text" scrollamount="5" direction="left">
        ⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE DANS LA NIEBLA ... RESTEZ DISCRETS ... TOUT CE QUI SE PASSE DANS LA BRUME RESTE DANS LA BRUME ... ⚠️
    </marquee>
    """, unsafe_allow_html=True)

# --- TITRE ---
st.write(f"<h1>☁️ L A &nbsp; N I E B L A</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>L'organisation ne dort jamais. Archivez vos actions.</p>", unsafe_allow_html=True)

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

def handle_submit(membre, action, butin=0, drogue="N/A", quantite=0):
    if not membre:
        st.error("L'ombre n'a pas de nom... Entre ton pseudo.")
        return

    try:
        new_row = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Membre": membre,
            "Action": action,
            "Drogue": drogue,
            "Quantite": quantite,
            "Butin": butin
        }])
        
        existing_data = conn.read(worksheet="Rapports", ttl=0)
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="Rapports", data=updated_df)
        
        st.snow() # L'effet de particules
        st.success(f"Archivé avec succès dans la brume.")
        
    except Exception as e:
        st.error(f"Erreur de transmission : {e}")

# --- FORMULAIRES ---
with tabs[0]:
    with st.form("atm"):
        m = st.text_input("👤 Membre", placeholder="Ton matricule", key="k_m_atm")
        b = st.number_input("💵 Butin ($)", min_value=0, key="k_b_atm")
        if st.form_submit_button("TRANSMETTRE RAPPORT ATM"):
            handle_submit(m, "ATM", butin=b)

with tabs[1]:
    with st.form("sup"):
        m = st.text_input("👤 Membre", placeholder="Ton matricule", key="k_m_sup")
        b = st.number_input("💵 Butin ($)", min_value=0, key="k_b_sup")
        if st.form_submit_button("TRANSMETTRE RAPPORT SUPERETTE"):
            handle_submit(m, "Supérette", butin=b)

with tabs[2]:
    with st.form("gf"):
        m = st.text_input("👤 Membre", placeholder="Ton matricule", key="k_m_gf")
        b = st.number_input("💵 Butin ($)", min_value=0, key="k_b_gf")
        if st.form_submit_button("TRANSMETTRE RAPPORT GO FAST"):
            handle_submit(m, "Go Fast", butin=b)

with tabs[3]:
    with st.form("cam"):
        m = st.text_input("👤 Membre", placeholder="Ton matricule", key="k_m_cam")
        if st.form_submit_button("TRANSMETTRE RAPPORT CAMBRIOLAGE"):
            handle_submit(m, "Cambriolage")

with tabs[4]:
    with st.form("dr"):
        m = st.text_input("👤 Membre", placeholder="Ton matricule", key="k_m_dr")
        d = st.text_input("🌿 Produit", placeholder="Ex: Weed...", key="k_d_dr")
        q = st.number_input("📦 Quantité", min_value=0, key="k_q_dr")
        b = st.number_input("💵 Total vente ($)", min_value=0, key="k_b_dr")
        if st.form_submit_button("TRANSMETTRE RAPPORT DROGUE"):
            handle_submit(m, "Drogue", butin=b, drogue=d, quantite=q)
