import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="wide")

# --- BASE DE DONNÉES DES MEMBRES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
}

# --- STYLE CSS (Immersif) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1c1f26 100%); }
    .brouillard-text {
        font-family: 'Courier New', monospace;
        color: rgba(255, 255, 255, 0.6);
        font-size: 18px;
        filter: blur(1px);
        text-align: center;
    }
    h1, h2, h3 { color: #ffffff; text-align: center; font-family: 'Courier New'; }
    .stForm { border: 1px solid #444; border-radius: 15px; background-color: rgba(38, 39, 48, 0.6); }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; border: none; }
    .stButton>button:hover { background-color: #ffffff; color: #ff4b4b; }
    [data-testid="stImage"] { display: block; margin: auto; }
    
    /* Progress bar color */
    .stProgress > div > div > div > div { background-color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'user_pseudo' not in st.session_state:
    st.session_state['user_pseudo'] = ""

def check_login():
    u = st.session_state["user_login"]
    p = st.session_state["password_login"]
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else:
        st.error("Accès refusé. La brume vous rejette.")

# --- CONNEXION SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIQUE D'AFFICHAGE ---
if not st.session_state['connected']:
    # PAGE DE CONNEXION
    st.write("<h1>☁️ S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.write("<p style='text-align: center; color: #888;'>Identifiez-vous pour entrer dans le brouillard</p>", unsafe_allow_html=True)
        st.text_input("Nom de code", key="user_login")
        st.text_input("Mot de passe", type="password", key="password_login")
        st.form_submit_button("ENTRER", on_click=check_login)
else:
    # MESSAGE DÉFILANT
    pseudo = st.session_state['user_pseudo']
    st.markdown(f'<marquee class="brouillard-text" scrollamount="5">⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE {pseudo.upper()} ... TOUT RESTE DANS LA BRUME ... ⚠️</marquee>', unsafe_allow_html=True)

    # --- LOGO (LIEN NETTOYÉ ET CORRIGÉ) ---
    # Nous utilisons le lien direct Raw pour ton fichier "logo.png"
    LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=2"
    st.image(LOGO_URL, width=350)
    
    st.write(f"<p style='text-align: center; color: #ff4b4b; margin-top:-20px;'>Session active : <b>{pseudo}</b></p>", unsafe_allow_html=True)

    # --- SECTION RAPPORTS ---
    tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

    def handle_submit(action, butin=0, drogue="N/A", quantite=0):
        try:
            # Enregistrement avec date ISO pour le tri
            new_row = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Membre": st.session_state['user_pseudo'],
                "Action": action, 
                "Drogue": drogue, 
                "Quantite": float(quantite), 
                "Butin": float(butin)
            }])
            df = conn.read(worksheet="Rapports", ttl=0)
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Rapports", data=updated_df)
            st.snow()
            st.success("Rapport archivé dans la brume.")
            st.rerun() 
        except Exception as e:
            st.error(f"Erreur de transmission : {e}")

    # Formulaires
    with tabs[0]:
        with st.form("atm"):
            b = st.number_input("💵 Butin récolté ($)", min_value=0, key="atmb")
            if st.form_submit_button("TRANSMETTRE ATM"): handle_submit("ATM", butin=b)
    with tabs[1]:
        with st.form("sup"):
            b = st.number_input("💵 Butin récolté ($)", min_value=0, key="supb")
            if st.form_submit_button("TRANSMETTRE SUPERETTE"): handle_submit("Supérette", butin=b)
    with tabs[2]:
        with st.form("gf"):
            b = st.number_input("💵 Butin récolté ($)", min_value=0, key="gfb")
            if st.form_submit_button("TRANSMETTRE GO FAST"): handle_submit("Go Fast", butin=b)
    with tabs[3]:
        with st.form("cam"):
            if st.form_submit_button("TRANSMETTRE CAMBRIOLAGE"): handle_submit("Cambriolage")
    with tabs[4]:
        with st.form("dr"):
            d = st.text_input("🌿 Produit", placeholder="Ex: Weed...", key="drn")
            q = st.number_input("📦 Quantité", min_value=0, key="drq")
            b = st.number_input("💵 Total vente ($)", min_value=0, key="drb")
            if st.form_submit_button("TRANSMETTRE DROGUE"): handle_submit("Drogue", butin=b, drogue=d, quantite=q)

    # --- TABLEAU DES OBJECTIFS ---
    st.markdown("---")
    st.write("### 📊 OBJECTIFS DE LA SEMAINE")
    
    try:
        data = conn.read(worksheet="Rapports", ttl=0)
        
        if data is not None and not data.empty:
            # Nettoyage des données
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            data['Quantite'] = pd.to_numeric(data['Quantite'], errors='coerce').fillna(0)
            data = data.dropna(subset=['Date'])
            
            # Calcul du début de semaine
            today = datetime.datetime.now()
            start_week = (today - datetime.timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0)
            
            week_data = data[data['Date'] >= start_week]

            if not week_data.empty:
                stats = week_data.groupby('Membre').agg({
                    'Action': 'count',
                    'Quantite': 'sum'
                }).reset_index()

                for _, row in stats.iterrows():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    c1.write(f"**{row['Membre']}**")
                    # Barre Actions (Objectif 20)
                    val_act = int(row['Action'])
                    c2.progress(min(val_act/20, 1.0), text=f"Actions: {val_act}/20")
                    # Barre Drogue (Objectif 300)
                    val_dro = int(row['Quantite'])
                    c3.progress(min(val_dro/300, 1.0), text=f"Drogue: {val_dro}/300")
            else:
                st.info("Aucune donnée pour la semaine du " + start_week.strftime("%d/%m"))
        else:
            st.info("Tu te bouge le cul ou quoi ?")
    except Exception as e:
        st.info("En attente de données valides...")

    st.markdown("---")
    if st.button("QUITTER LA SAFE HOUSE"):
        st.session_state['connected'] = False
        st.rerun()
