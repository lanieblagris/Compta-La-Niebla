import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="wide")

# --- BASE DE DONNÉES DES MEMBRES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Emilio": {"password": "azertyuiop123", "pseudo": "Emilio Montoya"},
}

# --- STYLE CSS (NOIR PUR ET IMMERSIF) ---
st.markdown("""
    <style>
    /* Fond noir total */
    .stApp {
        background-color: #000000 !important;
    }

    /* Texte défilant style brouillard */
    .brouillard-text {
        font-family: 'Courier New', monospace;
        color: rgba(255, 255, 255, 0.6);
        font-size: 18px;
        text-align: center;
        margin-top: 20px;
    }

    /* Titres et visuels */
    h1, h2, h3, h4 { color: #ffffff; text-align: center; font-family: 'Courier New'; }
    
    /* Formulaires et blocs */
    .stForm { 
        border: 1px solid #333; 
        border-radius: 15px; 
        background-color: rgba(20, 20, 20, 0.9); 
    }
    
    /* Bouton Rouge Niebla */
    .stButton>button { 
        width: 100%; 
        background-color: #ff4b4b; 
        color: white; 
        font-weight: bold; 
        border-radius: 10px; 
        border: none;
    }
    .stButton>button:hover { background-color: #ffffff; color: #ff4b4b; }
    
    /* Barres de progression rouges */
    .stProgress > div > div > div > div { background-color: #ff4b4b; }
    
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] { background-color: #111; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #ffffff; }
    
    /* Tableaux financiers */
    .stTable {
        background-color: #111;
        color: white;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
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

# --- CONNEXION GOOGLE SHEETS ---
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
    # VARIABLES UTILES
    LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
    pseudo = st.session_state['user_pseudo']

    # --- BANNIÈRE PLEINE LARGEUR ---
    st.markdown(f"""
        <div style="width: 100%; overflow: hidden; margin-bottom: 10px;">
            <img src="{LOGO_URL}" style="width: 100%; height: 250px; object-fit: cover; border-radius: 10px; border: 2px solid #333;">
        </div>
        """, unsafe_allow_html=True)

    # MESSAGE DÉFILANT
    st.markdown(f'<marquee class="brouillard-text" scrollamount="5">⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE {pseudo.upper()} ... TOUT RESTE DANS LA BRUME ... ⚠️</marquee>', unsafe_allow_html=True)
    st.write(f"<p style='text-align: center; color: #ff4b4b; margin-top:-10px; font-weight: bold;'>Session active : {pseudo}</p>", unsafe_allow_html=True)

    # --- SECTION RAPPORTS ---
    tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

    def handle_submit(action, butin=0, drogue="N/A", quantite=0):
        try:
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
            st.success("Rapport archivé.")
            st.rerun() 
        except Exception as e:
            st.error(f"Erreur : {e}")

    with tabs[0]:
        with st.form("atm"):
            b = st.number_input("💵 Butin ($)", min_value=0, key="atmb")
            if st.form_submit_button("TRANSMETTRE ATM"): handle_submit("ATM", butin=b)
    with tabs[1]:
        with st.form("sup"):
            b = st.number_input("💵 Butin ($)", min_value=0, key="supb")
            if st.form_submit_button("TRANSMETTRE SUPERETTE"): handle_submit("Supérette", butin=b)
    with tabs[2]:
        with st.form("gf"):
            b = st.number_input("💵 Butin ($)", min_value=0, key="gfb")
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

    # --- TABLEAU DES STATISTIQUES HEBDOMADAIRES ---
    st.markdown("---")
    st.write("### 📊 STATISTIQUES DE LA SEMAINE")
    
    try:
        data = conn.read(worksheet="Rapports", ttl=0)
        
        if data is not None and not data.empty:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            data['Quantite'] = pd.to_numeric(data['Quantite'], errors='coerce').fillna(0)
            data['Butin'] = pd.to_numeric(data['Butin'], errors='coerce').fillna(0)
            data = data.dropna(subset=['Date'])
            
            today = datetime.datetime.now()
            start_week = (today - datetime.timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0)
            week_data = data[data['Date'] >= start_week].copy()

            if not week_data.empty:
                # Calcul Actions (Tout sauf Drogue)
                actions_df = week_data[week_data['Action'] != "Drogue"]
                stats_actions = actions_df.groupby('Membre').agg({'Action': 'count', 'Butin': 'sum'}).reset_index()
                stats_actions.rename(columns={'Butin': 'Argent_Actions'}, inplace=True)
                
                # Calcul Drogue
                drogue_df = week_data[week_data['Action'] == "Drogue"]
                stats_drogue = drogue_df.groupby('Membre').agg({'Quantite': 'sum', 'Butin': 'sum'}).reset_index()
                stats_drogue.rename(columns={'Butin': 'Argent_Drogue'}, inplace=True)

                stats = pd.merge(stats_actions, stats_drogue, on='Membre', how='outer').fillna(0)

                # AFFICHAGE DES BARRES
                for _, row in stats.iterrows():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    c1.write(f"**{row['Membre']}**")
                    
                    val_act = int(row['Action'])
                    txt_act = f"Actions: {val_act}/20"
                    if val_act > 20: txt_act += f" 🔥 (+{val_act-20})"
                    c2.progress(min(val_act/20, 1.0), text=txt_act)
                    
                    val_dro = int(row['Quantite'])
                    txt_dro = f"Drogue: {val_dro}/300"
                    if val_dro > 300: txt_dro += f" 💰 (+{val_dro-300})"
                    c3.progress(min(val_dro/300, 1.0), text=txt_dro)

                # TABLEAU FINANCIER
                st.write("#### 💸 Récapitulatif des Gains")
                df_finance = stats[['Membre', 'Argent_Actions', 'Argent_Drogue']].copy()
                df_finance.columns = ['Membre', 'Butin Actions ($)', 'Ventes Drogue ($)']
                
                df_finance['Butin Actions ($)'] = df_finance['Butin Actions ($)'].apply(lambda x: f"{x:,.0f} $".replace(',', ' '))
                df_finance['Ventes Drogue ($)'] = df_finance['Ventes Drogue ($)'].apply(lambda x: f"{x:,.0f} $".replace(',', ' '))
                
                st.table(df_finance)
            else:
                st.info("Aucune activité cette semaine.")
        else:
            st.info("Allez au boulot feneant !")
    except Exception as e:
        st.info("En attente de données...")

    st.markdown("---")
    if st.button("QUITTER LA SAFE HOUSE"):
        st.session_state['connected'] = False
        st.rerun()
