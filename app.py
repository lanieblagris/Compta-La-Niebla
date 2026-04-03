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
}

# --- STYLE CSS (NOIR + ANIMATION BRUME) ---
st.markdown("""
    <style>
    /* Fond noir total */
    .stApp { background-color: #000000 !important; overflow: hidden; }

    /* ANIMATION DE LA BRUME (Seulement pour le fond) */
    .fog-container {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; /* Derrière tout */
        background: #000;
    }

    .fog {
        position: absolute;
        top: 0; left: 0; width: 200%; height: 100%;
        background: url('https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/fog.png'); /* On utilise une texture de brume */
        background-repeat: repeat-x;
        opacity: 0.3;
        animation: drift 60s linear infinite;
    }

    @keyframes drift {
        from { transform: translateX(0); }
        to { transform: translateX(-50%); }
    }

    /* Style du texte et formulaires */
    .brouillard-text { font-family: 'Courier New', monospace; color: rgba(255, 255, 255, 0.6); font-size: 18px; text-align: center; margin-top: 20px; }
    h1, h2, h3, h4 { color: #ffffff; text-align: center; font-family: 'Courier New'; }
    .stForm { border: 1px solid #333; border-radius: 15px; background-color: rgba(20, 20, 20, 0.95); position: relative; z-index: 10; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; border: none; }
    .stButton>button:hover { background-color: #ffffff; color: #ff4b4b; }
    .stProgress > div > div > div > div { background-color: #ff4b4b; }
    .stTable { background-color: #111; color: white; border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #333; }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ""

def check_login():
    u = st.session_state["user_login"]
    p = st.session_state["password_login"]
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else:
        st.error("Accès refusé. La brume vous rejette.")

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

if not st.session_state['connected']:
    # --- PAGE DE CONNEXION AVEC ANIMATION ---
    st.markdown('<div class="fog-container"><div class="fog"></div></div>', unsafe_allow_html=True)
    
    st.write("<br><br>", unsafe_allow_html=True)
    st.write("<h1>☁️ S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    st.write("<h3>L A &nbsp; N I E B L A</h3>", unsafe_allow_html=True)
    
    with st.container():
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            with st.form("login_form"):
                st.write("<p style='text-align: center; color: #888;'>Identifiez-vous pour entrer</p>", unsafe_allow_html=True)
                st.text_input("Nom de code", key="user_login")
                st.text_input("Mot de passe", type="password", key="password_login")
                st.form_submit_button("ENTRER", on_click=check_login)
else:
    # --- NAVIGATION SIDEBAR ---
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin":
            st.write("---")
            st.write("🔑 **DIRECTION**")
            menu.append("Comptabilité Globale")
        
        choice = st.radio("Navigation", menu)
        st.write("---")
        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    # --- PAGE 1 : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="width:100%;"><img src="{LOGO_URL}" style="width:100%; height:250px; object-fit:cover; border-radius:10px; border:2px solid #333;"></div>', unsafe_allow_html=True)
        st.markdown(f'<marquee class="brouillard-text" scrollamount="5">⚠️ TRANSMISSION SÉCURISÉE ... BIENVENUE {st.session_state["user_pseudo"].upper()} ... ⚠️</marquee>', unsafe_allow_html=True)

        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                df = conn.read(worksheet="Rapports", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df, new_row], ignore_index=True))
                st.snow()
                st.rerun() 
            except Exception as e: st.error(f"Erreur : {e}")

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
                d = st.text_input("🌿 Produit", placeholder="Weed...", key="drn")
                q = st.number_input("📦 Quantité", min_value=0, key="drq")
                b = st.number_input("💵 Total vente ($)", min_value=0, key="drb")
                if st.form_submit_button("TRANSMETTRE DROGUE"): handle_submit("Drogue", butin=b, drogue=d, quantite=q)

        st.markdown("---")
        st.write("### 📊 STATISTIQUES DE LA SEMAINE")
        try:
            data = conn.read(worksheet="Rapports", ttl=0)
            if data is not None and not data.empty:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                data['Quantite'] = pd.to_numeric(data['Quantite'], errors='coerce').fillna(0)
                data['Butin'] = pd.to_numeric(data['Butin'], errors='coerce').fillna(0)
                today = datetime.datetime.now()
                start_week = (today - datetime.timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0)
                week_data = data[data['Date'] >= start_week].copy()

                if not week_data.empty:
                    stats_actions = week_data[week_data['Action'] != "Drogue"].groupby('Membre').agg({'Action': 'count', 'Butin': 'sum'}).reset_index().rename(columns={'Butin': 'Argent_Actions'})
                    stats_drogue = week_data[week_data['Action'] == "Drogue"].groupby('Membre').agg({'Quantite': 'sum', 'Butin': 'sum'}).reset_index().rename(columns={'Butin': 'Argent_Drogue'})
                    stats = pd.merge(stats_actions, stats_drogue, on='Membre', how='outer').fillna(0)

                    for _, row in stats.iterrows():
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{row['Membre']}**")
                        v_act = int(row['Action'])
                        c2.progress(min(v_act/20, 1.0), text=f"Actions: {v_act}/20" + (f" 🔥 (+{v_act-20})" if v_act > 20 else ""))
                        v_dro = int(row['Quantite'])
                        c3.progress(min(v_dro/300, 1.0), text=f"Drogue: {v_dro}/300" + (f" 💰 (+{v_dro-300})" if v_dro > 300 else ""))

                    st.write("#### 💸 Récapitulatif des Gains")
                    df_f = stats[['Membre', 'Argent_Actions', 'Argent_Drogue']].copy()
                    df_f.columns = ['Membre', 'Butin Actions ($)', 'Ventes Drogue ($)']
                    df_f['Butin Actions ($)'] = df_f['Butin Actions ($)'].apply(lambda x: f"{x:,.0f} $")
                    df_f['Ventes Drogue ($)'] = df_f['Ventes Drogue ($)'].apply(lambda x: f"{x:,.0f} $")
                    st.table(df_f)
                else: st.info("Au boulot feneant !")
        except Exception as e: st.info("En attente de données...")

    # --- PAGE 2 : COMPTABILITÉ GLOBALE (ADMIN) ---
    elif choice == "Comptabilité Globale":
        st.write("## 🏛️ DIRECTION - GESTION DU COFFRE")
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                rec = df_all[df_all['Type'] == "Recette"]['Montant'].sum()
                dep = df_all[df_all['Type'] == "Dépense"]['Montant'].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("Recettes Totales", f"{rec:,.0f} $")
                m2.metric("Dépenses Totales", f"{dep:,.0f} $")
                m3.metric("SOLDE DU COFFRE", f"{rec-dep:,.0f} $")
        except: pass

        st.markdown("---")
        with st.form("admin_compta"):
            st.write("#### ➕ Ajouter une transaction")
            c1, c2, c3 = st.columns(3)
            t_type = c1.selectbox("Nature", ["Recette", "Dépense"])
            t_cat = c2.text_input("Catégorie")
            t_mont = c3.number_input("Montant ($)", min_value=0)
            t_note = st.text_area("Justification")
            if st.form_submit_button("Valider la transaction"):
                try:
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Catégorie": t_cat, "Montant": float(t_mont), "Note": t_note}])
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.rerun()
                except Exception as e: st.error(f"Erreur : {e}")
