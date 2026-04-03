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

# --- STYLE CSS (CORRIGÉ) ---
st.markdown("""
    <style>
    /* Fond noir total */
    .stApp { background-color: #000000 !important; }

    /* ANIMATION DE LA BRUME (FOG) */
    .fogwrapper {
        height: 100%;
        position: fixed;
        top: 0;
        width: 100%;
        -webkit-filter: blur(1px);
        filter: blur(1px);
        z-index: 0;
    }
    #foglayer_01, #foglayer_02, #foglayer_03 {
        height: 100%;
        position: absolute;
        width: 200%;
    }
    #foglayer_01 .image01, #foglayer_01 .image02,
    #foglayer_02 .image01, #foglayer_02 .image02,
    #foglayer_03 .image01, #foglayer_03 .image02 {
        float: left;
        height: 100%;
        width: 50%;
    }
    #foglayer_01 { -webkit-animation: foglayer_01_opacity 10s linear infinite, foglayer_moveme 15s linear infinite; animation: foglayer_01_opacity 10s linear infinite, foglayer_moveme 15s linear infinite; }
    #foglayer_02 { -webkit-animation: foglayer_02_opacity 15s linear infinite, foglayer_moveme 13s linear infinite; animation: foglayer_02_opacity 15s linear infinite, foglayer_moveme 13s linear infinite; }
    #foglayer_03 { -webkit-animation: foglayer_03_opacity 20s linear infinite, foglayer_moveme 11s linear infinite; animation: foglayer_03_opacity 20s linear infinite, foglayer_moveme 11s linear infinite; }

    .image01, .image02 {
        background: url("https://raw.githubusercontent.com/Anemolo/Fog-Effect/master/fog1.png") center center / cover no-repeat transparent;
    }

    @-webkit-keyframes foglayer_moveme { 0% { left: 0; } 100% { left: -100%; } }
    @keyframes foglayer_moveme { 0% { left: 0; } 100% { left: -100%; } }

    @-webkit-keyframes foglayer_01_opacity { 0% { opacity: .1; } 22% { opacity: .5; } 40% { opacity: .28; } 58% { opacity: .4; } 80% { opacity: .16; } 100% { opacity: .1; } }
    @keyframes foglayer_01_opacity { 0% { opacity: .1; } 22% { opacity: .5; } 40% { opacity: .28; } 58% { opacity: .4; } 80% { opacity: .16; } 100% { opacity: .1; } }
    
    .brouillard-text { font-family: 'Courier New', monospace; color: rgba(255, 255, 255, 0.6); font-size: 18px; text-align: center; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; font-family: 'Courier New'; }
    .stForm { border: 1px solid #333; border-radius: 15px; background-color: rgba(10, 10, 10, 0.85); position: relative; z-index: 100; }
    .stButton>button { background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 10px; border: none; width: 100%; }
    .stProgress > div > div > div > div { background-color: #ff4b4b; }
    [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #333; }
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
        st.error("Accès refusé par La Niebla.")

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIQUE D'AFFICHAGE ---
if not st.session_state['connected']:
    # --- PAGE DE CONNEXION ---
    st.markdown("""
        <div class="fogwrapper">
            <div id="foglayer_01" class="fog"><div class="image01"></div><div class="image02"></div></div>
            <div id="foglayer_02" class="fog"><div class="image01"></div><div class="image02"></div></div>
            <div id="foglayer_03" class="fog"><div class="image01"></div><div class="image02"></div></div>
        </div>
    """, unsafe_allow_html=True)

    st.write("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='letter-spacing: 10px;'>S A F E &nbsp; H O U S E</h1>", unsafe_allow_html=True)
    
    left, mid, right = st.columns([1, 1.5, 1])
    with mid:
        with st.form("login_form"):
            st.write("<p style='text-align: center; color: #888;'>L'argent n'aime pas le bruit, la brume si.</p>", unsafe_allow_html=True)
            st.text_input("Nom de code", key="user_login")
            st.text_input("Mot de passe", type="password", key="password_login")
            if st.form_submit_button("ENTRER DANS LA ZONE"):
                check_login()
                if st.session_state['connected']:
                    st.rerun()
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
        if st.button("Quitter la session"):
            st.session_state['connected'] = False
            st.rerun()

    # --- PAGE 1 : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.image(LOGO_URL)
        st.markdown(f'<marquee class="brouillard-text" scrollamount="5">⚠️ SESSION ACTIVE : {st.session_state["user_pseudo"].upper()} ⚠️</marquee>', unsafe_allow_html=True)

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
                        c2.progress(min(v_act/20, 1.0), text=f"Actions: {v_act}/20")
                        v_dro = int(row['Quantite'])
                        c3.progress(min(v_dro/300, 1.0), text=f"Drogue: {v_dro}/300")
                    
                    st.write("#### 💸 Récapitulatif")
                    st.table(stats[['Membre', 'Argent_Actions', 'Argent_Drogue']])
                else: st.info("Au boulot feneant !")
        except: st.info("Synchronisation des données...")

    # --- PAGE ADMIN : COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.write("## 🏛️ GESTION DU COFFRE - DIRECTION")
        
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                rec = df_all[df_all['Type'] == "Recette"]['Montant'].sum()
                dep = df_all[df_all['Type'] == "Dépense"]['Montant'].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("Recettes Totales", f"{rec:,.0f} $")
                m2.metric("Dépenses Totales", f"{dep:,.0f} $")
                m3.metric("SOLDE DU COFFRE", f"{rec-dep:,.0f} $", delta=float(rec-dep))
        except: st.warning("Créez l'onglet 'Tresorerie' sur GSheets.")

        st.markdown("---")
        with st.form("admin_compta"):
            st.write("#### ➕ Ajouter une transaction")
            c1, c2, c3 = st.columns(3)
            t_type = c1.selectbox("Nature", ["Recette", "Dépense"])
            t_cat = c2.text_input("Catégorie (Loyer, Blanchiment...)")
            t_mont = c3.number_input("Montant ($)", min_value=0)
            t_note = st.text_area("Justification")
            if st.form_submit_button("VALIDER TRANSACTION"):
                try:
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Catégorie": t_cat, "Montant": float(t_mont), "Note": t_note}])
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.rerun()
                except Exception as e: st.error(f"Erreur : {e}")

        st.markdown("---")
        st.write("#### 📝 Journal de bord")
        try:
            df_v = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_v.empty:
                st.dataframe(df_v.sort_values(by="Date", ascending=False), use_container_width=True)
        except: pass
