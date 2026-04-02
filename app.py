import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="La Niebla - Login", page_icon="🥷", layout="centered")

# --- STYLE CSS (Ambiance Brouillard) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1c1f26 100%); }
    .brouillard-text {
        font-family: 'Courier New', monospace;
        color: rgba(255, 255, 255, 0.6);
        font-size: 18px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 5px;
        filter: blur(1px);
        padding: 10px 0;
        text-align: center;
    }
    h1 { color: #ffffff; text-align: center; font-family: 'Courier New'; }
    .stForm { border: 1px solid #444; border-radius: 15px; background-color: rgba(38, 39, 48, 0.6); }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA CONNEXION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    # MODIFIE TES IDENTIFIANTS ICI
    if st.session_state["user"] == "Niebla" and st.session_state["password"] == "1234":
        st.session_state['connected'] = True
    else:
        st.error("Accès refusé. La brume vous rejette.")

# --- PAGE DE CONNEXION ---
if not st.session_state['connected']:
    st.write("<h1>☁️ S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.write("<p style='text-align: center; color: #888;'>Identifiez-vous pour entrer dans le brouillard</p>", unsafe_allow_html=True)
        st.text_input("Nom de code", key="user")
        st.text_input("Mot de passe", type="password", key="password")
        st.form_submit_button("ENTRER", on_click=check_login)
    st.stop() # Bloque le reste du code tant qu'on n'est pas connecté

# --- SI CONNECTÉ, AFFICHE LE RESTE DU SITE ---

# Message défilant
st.markdown("""
    <marquee class="brouillard-text" scrollamount="5" direction="left">
        ⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE DANS LA NIEBLA ... RESTEZ DISCRETS ... ⚠️
    </marquee>
    """, unsafe_allow_html=True)

st.write(f"<h1>☁️ L A &nbsp; N I E B L A</h1>", unsafe_allow_html=True)

# Connexion Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

def handle_submit(membre, action, butin=0, drogue="N/A", quantite=0):
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
        st.snow()
        st.success(f"Archivé avec succès.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- FORMULAIRES ---
with tabs[0]:
    with st.form("atm"):
        m = st.text_input("👤 Membre", placeholder="Ton pseudo", key="k_m_atm")
        b = st.number_input("💵 Butin ($)", min_value=0, key="k_b_atm")
        if st.form_submit_button("TRANSMETTRE"):
            handle_submit(m, "ATM", butin=b)

with tabs[1]:
    with st.form("sup"):
        m = st.text_input("👤 Membre", placeholder="Ton pseudo", key="k_m_sup")
        b = st.number_input("💵 Butin ($)", min_value=0, key="k_b_sup")
        if st.form_submit_button("TRANSMETTRE"):
            handle_submit(m, "Supérette", butin=b)

with tabs[2]:
    with st.form("gf"):
        m = st.text_input("👤 Membre", placeholder="Ton pseudo", key="k_m_gf")
        b = st.number_input("💵 Butin ($)", min_value=0, key="k_b_gf")
        if st.form_submit_button("TRANSMETTRE"):
            handle_submit(m, "Go Fast", butin=b)

with tabs[3]:
    with st.form("cam"):
        m = st.text_input("👤 Membre", placeholder="Ton pseudo", key="k_m_cam")
        if st.form_submit_button("TRANSMETTRE"):
            handle_submit(m, "Cambriolage")

with tabs[4]:
    with st.form("dr"):
        m = st.text_input("👤 Membre", placeholder="Ton pseudo", key="k_m_dr")
        d = st.text_input("🌿 Produit", placeholder="Ex: Weed...", key="k_d_dr")
        q = st.number_input("📦 Quantité", min_value=0, key="k_q_dr")
        b = st.number_input("💵 Total vente ($)", min_value=0, key="k_b_dr")
        if st.form_submit_button("TRANSMETTRE"):
            handle_submit(m, "Drogue", butin=b, drogue=d, quantite=q)

# Option de déconnexion en bas de page
if st.button("QUITTER LA SAFE HOUSE"):
    st.session_state['connected'] = False
    st.rerun()
