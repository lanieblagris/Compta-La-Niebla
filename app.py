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

# --- STYLE CSS (IMMERSION TOTALE AVEC BRUME) ---
# Nous utilisons les liens bruts (raw) pour charger les images directement.
LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=3"
BRUME_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/brume.png?v=1"

st.markdown(f"""
    <style>
    /* 1. FOND NOIR TOTAL ET BRUME FIXE */
    .stApp {{
        background-color: #000000; /* Fond noir pur */
        background-image: url('{BRUME_URL}'); /* Image de brume */
        background-size: cover; /* Couvre tout l'écran */
        background-position: center; /* Centrée */
        background-repeat: no-repeat; /* Ne se répète pas */
        background-attachment: fixed; /* La brume reste fixe quand on scrolle */
    }}

    /* 2. TEXTE BROUILLARD DÉFILANT */
    .brouillard-text {{
        font-family: 'Courier New', monospace;
        color: rgba(255, 255, 255, 0.6);
        font-size: 18px;
        filter: blur(1px);
        text-align: center;
        margin-top: 20px;
    }}

    /* 3. TITRES ET TEXTES */
    h1, h2, h3 {{ color: #ffffff; text-align: center; font-family: 'Courier New'; }}
    .stForm {{ border: 1px solid #444; border-radius: 15px; background-color: rgba(38, 39, 48, 0.8); }}
    .stButton>button {{ width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; border: none; }}
    .stButton>button:hover {{ background-color: #ffffff; color: #ff4b4b; }}
    
    /* Centrage de l'image de bannière standard si nécessaire */
    [data-testid="stImage"] {{ display: block; margin: auto; }}
    
    /* 4. PROGRESS BARS ROUGES */
    .stProgress > div > div > div > div {{ background-color: #ff4b4b; }}
    
    /* Correction de couleur pour les onglets */
    .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(38, 39, 48, 0.8); border-radius: 10px; }}
    .stTabs [data-baseweb="tab"] {{ color: #ffffff; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: #ff4b4b; }}
    
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

# --- LOGIQUE D'AFFICHAGE PRINCIPALE ---
if not st.session_state['connected']:
    # PAGE DE CONNEXION SÉCURISÉE
    st.write("<h1>☁️ S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.write("<p style='text-align: center; color: #888;'>Identifiez-vous pour entrer dans le brouillard</p>", unsafe_allow_html=True)
        st.text_input("Nom de code", key="user_login")
        st.text_input("Mot de passe", type="password", key="password_login")
        st.form_submit_button("ENTRER", on_click=check_login)
else:
    # BANDEAU BANNIÈRE PLEINE LARGEUR CORRIGÉ
    st.markdown(f"""
        <div style="width: 100%; overflow: hidden; margin-bottom: 10px;">
            <img src="{LOGO_URL}" style="width: 100%; height: 250px; object-fit: cover; border-radius: 10px; border: 2px solid #333;">
        </div>
        """, unsafe_allow_html=True)

    # MESSAGE DÉFILANT
    pseudo = st.session_state['user_pseudo']
    st.markdown(f'<marquee class="brouillard-text" scrollamount="5">⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE {pseudo.upper()} ... TOUT RESTE DANS LA BRUME ... ⚠️</marquee>', unsafe_allow_html=True)

    # INFORMATION SESSION
    st.write(f"<p style='text-align: center; color: #ff4b4b; margin-top:-10px; font-weight: bold;'>Session active : {pseudo}</p>", unsafe_allow_html=True)

    # --- SECTION RAPPORTS D'ACTIVITÉ ---
    tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

    def handle_submit(action, butin=0, drogue="N/A", quantite=0):
        try:
            # Enregistrement avec date ISO pour le tri
            new_row = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Membre": st.session_state['user_pseudo'],
                "Action": action, 
                "Drogue": drogue, 
                "Quantite": float(quantite), # Forcer en nombre
                "Butin": float(butin) # Forcer en nombre
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

   # --- TABLEAU DES OBJECTIFS & RÉCAPITULATIF FINANCIER ---
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
                # 1. Calcul pour les Missions (Tout sauf Drogue)
                actions_df = week_data[week_data['Action'] != "Drogue"]
                stats_actions = actions_df.groupby('Membre').agg({
                    'Action': 'count',
                    'Butin': 'sum'
                }).reset_index()
                stats_actions.rename(columns={'Butin': 'Argent_Missions'}, inplace=True)
                
                # 2. Calcul pour la Drogue
                drogue_df = week_data[week_data['Action'] == "Drogue"]
                stats_drogue = drogue_df.groupby('Membre').agg({
                    'Quantite': 'sum',
                    'Butin': 'sum'
                }).reset_index()
                stats_drogue.rename(columns={'Butin': 'Argent_Drogue'}, inplace=True)

                # Fusion des données
                stats = pd.merge(stats_actions, stats_drogue, on='Membre', how='outer').fillna(0)

                # --- AFFICHAGE DES BARRES DE PROGRESSION ---
                for _, row in stats.iterrows():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    c1.write(f"**{row['Membre']}**")
                    
                    # Missions (Obj 20)
                    val_act = int(row['Action'])
                    txt_act = f"Missions: {val_act}/20"
                    if val_act > 20: txt_act += f" 🔥 (+{val_act-20})"
                    c2.progress(min(val_act/20, 1.0), text=txt_act)
                    
                    # Drogue (Obj 300)
                    val_dro = int(row['Quantite'])
                    txt_dro = f"Drogue: {val_dro}/300"
                    if val_dro > 300: txt_dro += f" 💰 (+{val_dro-300})"
                    c3.progress(min(val_dro/300, 1.0), text=txt_dro)

                # --- NOUVEAU : TABLEAU FINANCIER ---
                st.write("#### 💸 Récapitulatif des Gains")
                
                # On prépare un tableau propre pour l'affichage
                df_finance = stats[['Membre', 'Argent_Missions', 'Argent_Drogue']].copy()
                df_finance.columns = ['Membre', 'Butin Missions ($)', 'Ventes Drogue ($)']
                
                # Formatage pour ajouter le symbole $ et les séparateurs de milliers
                df_finance['Butin Missions ($)'] = df_finance['Butin Missions ($)'].apply(lambda x: f"{x:,.0f} $".replace(',', ' '))
                df_finance['Ventes Drogue ($)'] = df_finance['Ventes Drogue ($)'].apply(lambda x: f"{x:,.0f} $".replace(',', ' '))
                
                # Affichage du tableau stylisé
                st.table(df_finance)

            else:
                st.info(f"Aucune activité pour la semaine du {start_week.strftime('%d/%m')}")
        else:
            st.info("Tu te bouges le cul ou quoi ?")
    except Exception as e:
        st.info("En attente de données valides...")

    # --- BOUTON DE SORTIE ---
    st.markdown("---")
    col_out, col_empty = st.columns([1, 3])
    with col_out:
        if st.button("QUITTER LA SAFE HOUSE"):
            st.session_state['connected'] = False
            st.rerun()
