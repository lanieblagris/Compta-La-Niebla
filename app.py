import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="centered")

# --- BASE DE DONNÉES DES MEMBRES ---
# Format : "Nom de code": {"password": "Mdp", "pseudo": "Nom affiché dans le Sheets"}
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Niebla": {"password": "1234", "pseudo": "Membre_Alpha"},
    "Ghost": {"password": "5678", "pseudo": "L'Ombre"},
    # Rajoute tes membres ici sur le même modèle
}

# --- STYLE CSS ---
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
    st.session_state['user_pseudo'] = ""

def check_login():
    user_input = st.session_state["user_login"]
    pass_input = st.session_state["password_login"]
    
    if user_input in USERS and USERS[user_input]["password"] == pass_input:
        st.session_state['connected'] = True
        st.session_state['user_pseudo'] = USERS[user_input]["pseudo"]
    else:
        st.error("Accès refusé. La brume vous rejette.")

# --- PAGE DE CONNEXION ---
if not st.session_state['connected']:
    st.write("<h1>☁️ S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.write("<p style='text-align: center; color: #888;'>Identifiez-vous pour entrer dans le brouillard</p>", unsafe_allow_html=True)
        st.text_input("Nom de code", key="user_login")
        st.text_input("Mot de passe", type="password", key="password_login")
        st.form_submit_button("ENTRER", on_click=check_login)
    st.stop()

# --- SI CONNECTÉ ---

# Message défilant
st.markdown(f"""
    <marquee class="brouillard-text" scrollamount="5" direction="left">
        ⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE {st.session_state['user_pseudo'].upper()} ... RESTEZ DISCRETS ... ⚠️
    </marquee>
    """, unsafe_allow_html=True)

st.write(f"<h1>☁️ L A &nbsp; N I E B L A</h1>", unsafe_allow_html=True)
st.write(f"<p style='text-align: center; color: #ff4b4b;'>Session active : <b>{st.session_state['user_pseudo']}</b></p>", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

def handle_submit(action, butin=0, drogue="N/A", quantite=0):
    try:
        # On récupère automatiquement le pseudo de la session
        membre_actif = st.session_state['user_pseudo']
        
        new_row = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Membre": membre_actif,
            "Action": action,
            "Drogue": drogue,
            "Quantite": quantite,
            "Butin": butin
        }])
        
        existing_data = conn.read(worksheet="Rapports", ttl=0)
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="Rapports", data=updated_df)
        st.snow()
        st.success(f"Rapport de {membre_actif} archivé.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- FORMULAIRES (SANS CHAMP MEMBRE) ---
with tabs[0]:
    with st.form("atm"):
        b = st.number_input("💵 Butin récolté ($)", min_value=0, key="k_b_atm")
        if st.form_submit_button("TRANSMETTRE ATM"):
            handle_submit("ATM", butin=b)

with tabs[1]:
    with st.form("sup"):
        b = st.number_input("💵 Butin récolté ($)", min_value=0, key="k_b_sup")
        if st.form_submit_button("TRANSMETTRE SUPERETTE"):
            handle_submit("Supérette", butin=b)

with tabs[2]:
    with st.form("gf"):
        b = st.number_input("💵 Butin récolté ($)", min_value=0, key="k_b_gf")
        if st.form_submit_button("TRANSMETTRE GO FAST"):
            handle_submit("Go Fast", butin=b)

with tabs[3]:
    with st.form("cam"):
        if st.form_submit_button("TRANSMETTRE CAMBRIOLAGE"):
            handle_submit("Cambriolage")

with tabs[4]:
    with st.form("dr"):
        d = st.text_input("🌿 Produit", placeholder="Ex: Weed...", key="k_d_dr")
        q = st.number_input("📦 Quantité", min_value=0, key="k_q_dr")
        b = st.number_input("💵 Total vente ($)", min_value=0, key="k_b_dr")
        if st.form_submit_button("TRANSMETTRE DROGUE"):
            handle_submit("Drogue", butin=b, drogue=d, quantite=q)

st.markdown("---")
if st.button("QUITTER LA SAFE HOUSE"):
    st.session_state['connected'] = False
    st.rerun()
