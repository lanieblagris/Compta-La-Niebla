import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION ET CONSTANTES ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Emilio": {"password": "azertyuiop123", "pseudo": "Emilio Montoya"},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith"},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin"},
}

# --- 2. STYLE CSS & DESIGN ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp {{ background: transparent !important; }}
    body {{ background-color: #000000; }}
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 5px 5px 15px #000, 0 0 25px #555;
        margin-top: -60px; margin-bottom: 0px; letter-spacing: 3px;
    }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #444 !important; border-radius: 10px; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: white !important; font-family: 'Courier New', monospace; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.9) !important; }}
    [data-testid="stMetricValue"] {{ color: white !important; }}
    [data-testid="stMetricLabel"] {{ color: #bbb !important; }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS SYSTÈME & HEURE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    """Heure actuelle France (UTC+2)"""
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

def log_invisible(action, details=""):
    try:
        ts = get_now()
        df_r = conn.read(worksheet="Rapports", ttl=0)
        new_log = pd.DataFrame([{"Date": ts, "Membre": st.session_state.get('user_pseudo', 'Système'), "Action": f"[LOG] {action}", "Drogue": "N/A", "Quantite": 0, "Butin": 0, "Note": details}])
        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_log], ignore_index=True))
    except: pass

if 'connected' not in st.session_state: st.session_state['connected'] = False
if "form_key" not in st.session_state: st.session_state.form_key = 0

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
        log_invisible("Connexion", f"Login réussi")
    else:
        st.error("Identifiants incorrects.")

# --- 4. INTERFACE ---
if not st.session_state['connected']:
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            st.text_input("NOM DE CODE", key="user_login")
            st.text_input("MOT DE PASSE", type="password", key="password_login")
            if st.form_submit_button("S'INFILTRER"):
                check_login()
                if st.session_state['connected']: st.rerun()
else:
    # SIDEBAR
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin": 
            menu += ["Comptabilité Globale", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        
        # 1. MES 3 DERNIÈRES ACTIONS (POUR LE MEMBRE)
        st.write("### 🕒 Mes 3 dernières activités")
        try:
            df_full = conn.read(worksheet="Rapports", ttl=0)
            if not df_full.empty:
                ma_compta = df_full[
                    (df_full['Membre'] == st.session_state['user_pseudo']) & 
                    (~df_full['Action'].str.contains(r'\[LOG\]', na=False))
                ].tail(3).iloc[::-1]
                if not ma_compta.empty:
                    st.table(ma_compta[['Date', 'Action', 'Butin']])
                else:
                    st.info("Aucune action récente.")
        except: pass

        st.markdown("---")
        
        # 2. ONGLETS DE SAISIE
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                ts = get_now()
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                new_rep = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_treso = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Transmis !"); time.sleep(1); st.session_state.form_key += 1; st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form(key=f"sup_{st.session_state.form_key}"):
                b = st.number_input("Butin
