import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time
import hashlib  # ✅ ajout sécurité

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

# --- HAUT DE PAGE STYLISÉ ---
st.markdown(f"""
    <div style="text-align: center; margin-top: -50px;">
        <div class="gta-title" style="margin-bottom: 0px;">La Niebla</div>
        <div style="
            font-family: 'Courier New', monospace;
            color: #888;
            font-size: 18px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 20px;
            opacity: 0.8;
            font-style: italic;
        ">
            "En el silencio, mandamos."
        </div>
    </div>
""", unsafe_allow_html=True)

VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

# --- STYLE CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{ background: transparent !important; }}
    body {{ background-color: #000000; }}
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 0 0 10px #fff, 0 0 20px #aaa;
        margin-top: -60px; margin-bottom: 10px; letter-spacing: 3px;
    }}
    button:hover {{ transform: scale(1.05); transition: 0.2s; }}  /* ✅ effet hover */
    #bgVideo {{
        position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
        z-index: -1000; filter: brightness(0.3); object-fit: cover;
    }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
""", unsafe_allow_html=True)

# --- HASH PASSWORD ---
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# --- USERS (sécurisés) ---
USERS = {
    "Admin": {"password": hash_password("0000"), "pseudo": "El Patron"},
    "Alex": {"password": hash_password("Alx220717"), "pseudo": "Alex Smith"},
    "Dany": {"password": hash_password("081219"), "pseudo": "Dany Smith"},
    "Emilio": {"password": hash_password("azertyuiop123"), "pseudo": "Emilio Montoya"},
    "Aziz": {"password": hash_password("asmith"), "pseudo": "Aziz Smith"},
    "Junior": {"password": hash_password("Loup1304"), "pseudo": "Madra Junior"},
}

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == hash_password(p):  # ✅ sécurisé
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]

conn = st.connection("gsheets", type=GSheetsConnection)

# --- SAFE UPDATE (anti bug concurrence) ---
def safe_update(sheet, new_row):
    for _ in range(3):
        try:
            df = conn.read(worksheet=sheet, ttl=0)
            conn.update(worksheet=sheet, data=pd.concat([df, new_row], ignore_index=True))
            return True
        except:
            time.sleep(1)
    return False

# --- LOGIN ---
if not st.session_state['connected']:
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        st.text_input("NOM DE CODE", key="user_login")
        st.text_input("MOT DE PASSE", type="password", key="password_login")
        if st.form_submit_button("S'INFILTRER"):
            check_login()
            if st.session_state['connected']:
                st.rerun()
            else:
                st.error("Accès refusé")

# --- APP ---
else:
    with st.sidebar:
        st.write(f"🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin":
            menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)

        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    if choice == "Tableau de bord":

        tabs = st.tabs(["💰 ATM", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            new_row = pd.DataFrame([{
                "Date": datetime.datetime.now(),
                "Membre": st.session_state['user_pseudo'],
                "Action": action,
                "Drogue": drogue,
                "Quantite": float(quantite),
                "Butin": float(butin)
            }])

            ok1 = safe_update("Rapports", new_row)

            new_op = pd.DataFrame([{
                "Date": datetime.datetime.now(),
                "Type": "Recette",
                "Etat": "Sale",
                "Catégorie": action,
                "Montant": float(butin),
                "Note": f"{st.session_state['user_pseudo']}"
            }])

            ok2 = safe_update("Tresorerie", new_op)

            if ok1 and ok2:
                st.success("Transmis avec succès.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Erreur d'envoi")

        # --- ATM ---
        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"):
                    handle_submit("ATM", butin=b)

        # --- DROGUE AVEC SÉCURITÉ STOCK ---
        with tabs[1]:
            with st.form("dr"):
                d = st.selectbox("Produit", ["Marijuana", "Cocaine", "Meth"])
                q = st.number_input("Quantité", min_value=0.0)
                b = st.number_input("Prix", min_value=0)

                if st.form_submit_button("Vendre"):
                    df = conn.read(worksheet="Rapports", ttl=0)
                    stock = df[df["Drogue"] == d]["Quantite"].sum()

                    if stock < q:
                        st.error("Stock insuffisant !")
                    else:
                        handle_submit("Drogue", butin=b, drogue=d, quantite=-abs(q))

        # --- STATS ---
        st.write("### 📊 STATISTIQUES")

        df = conn.read(worksheet="Rapports", ttl=0)
        if df is not None and not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            week = df[df['Date'] >= datetime.datetime.now() - datetime.timedelta(days=7)]

            stats = week.groupby("Membre").agg({
                "Action": "count",
                "Quantite": lambda x: abs(x).sum(),
                "Butin": "sum"
            }).reset_index()

            max_actions = max(stats["Action"].max(), 1)

            for _, row in stats.iterrows():
                c1, c2 = st.columns([1,2])
                c1.write(row["Membre"])
                c2.progress(row["Action"] / max_actions)

            # --- LEADERBOARD ---
            st.write("### 🏆 TOP 3")
            top = stats.sort_values(by="Butin", ascending=False).head(3)
            st.table(top)
