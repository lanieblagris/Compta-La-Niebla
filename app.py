import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="wide")

# --- 2. LIEN VIDÉO (FONCTIONNEL) ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

# --- 3. STYLE CSS & FOND VIDÉO ---
st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
        background: transparent !important;
    }}
    body {{ background-color: #000000; }}
    #bgVideo {{
        position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
        z-index: -1000; filter: brightness(0.4); object-fit: cover;
    }}
    .stForm {{ 
        background-color: rgba(10, 10, 10, 0.8) !important; 
        border: 1px solid #333 !important; border-radius: 15px;
    }}
    h1, h2, h3, h4, p, label, .stMarkdown {{ 
        color: white !important; font-family: 'Courier New', monospace;
        text-shadow: 2px 2px 4px #000;
    }}
    [data-testid="stSidebar"] {{ background-color: rgba(10, 10, 10, 0.9) !important; }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 4. BASE DE DONNÉES DES MEMBRES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
}

# --- 5. INITIALISATION DE LA SESSION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else:
        st.error("Accès refusé. La brume vous rejette.")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 6. LOGIQUE D'AFFICHAGE ---
if not st.session_state['connected']:
    st.write("<br><br><br><br>", unsafe_allow_html=True)
    st.write("<h1>☁️ S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        with st.form("login_form"):
            st.text_input("Nom de code", key="user_login")
            st.text_input("Mot de passe", type="password", key="password_login")
            if st.form_submit_button("ENTRER"):
                check_login()
                if st.session_state['connected']: st.rerun()
else:
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin":
            menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    if choice == "Tableau de bord":
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:250px; object-fit:cover; border-radius:10px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                df = conn.read(worksheet="Rapports", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df, new_row], ignore_index=True))
                st.snow()
                st.rerun() 
            except Exception as e:
                st.error(f"Erreur lors de l'envoi : {e}")

        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="val_atm")
                if st.form_submit_button("TRANSMETTRE ATM"): handle_submit("ATM", butin=b)
        
        with tabs[4]:
            with st.form("dr"):
                d = st.text_input("🌿 Produit")
                q = st.number_input("📦 Quantité", min_value=0)
                b = st.number_input("💵 Vente ($)", min_value=0)
                if st.form_submit_button("VALIDER DROGUE"): handle_submit("Drogue", butin=b, drogue=d, quantite=q)

        # --- STATS HEBDOMADAIRES ---
        st.markdown("---")
        st.write("### 📊 STATISTIQUES DE LA SEMAINE")
        try:
            data = conn.read(worksheet="Rapports", ttl=0)
            if data is not None and not data.empty:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                today = datetime.datetime.now()
                start_week = (today - datetime.timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0)
                week_data = data[data['Date'] >= start_week].copy()

                if not week_data.empty:
                    s_act = week_data[week_data['Action'] != "Drogue"].groupby('Membre').agg({'Action': 'count', 'Butin': 'sum'}).reset_index()
                    s_dro = week_data[week_data['Action'] == "Drogue"].groupby('Membre').agg({'Quantite': 'sum', 'Butin': 'sum'}).reset_index()
                    stats = pd.merge(s_act, s_dro, on='Membre', how='outer').fillna(0)

                    for _, row in stats.iterrows():
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{row['Membre']}**")
                        c2.progress(min(int(row['Action'])/20, 1.0), text=f"Actions: {int(row['Action'])}/20")
                        c3.progress(min(int(row['Quantite'])/300, 1.0), text=f"Drogue: {int(row['Quantite'])}/300")

                    st.write("#### 💸 Récapitulatif des Gains")
                    df_recap = stats[['Membre', 'Butin_x', 'Butin_y']].copy()
                    df_recap.columns = ['Membre', 'Actions', 'Drogue']
                    df_recap['Actions'] = df_recap['Actions'].apply(lambda x: f"{int(x):,} $".replace(',', ' '))
                    df_recap['Drogue'] = df_recap['Drogue'].apply(lambda x: f"{int(x):,} $".replace(',', ' '))
                    st.table(df_recap)
            else:
                st.info("Aucune donnée disponible.")
        except Exception as e:
            st.info("Chargement des données...")

    elif choice == "Comptabilité Globale":
        st.write("## 🏛️ COMPTABILITÉ")
