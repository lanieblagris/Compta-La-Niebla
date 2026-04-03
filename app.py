import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="wide")

# --- 2. BASE DE DONNÉES DES MEMBRES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
}

# --- STYLE CSS ULTIME (FORCE LA BRUME PARTOUT) ---
st.markdown("""
    <style>
    /* 1. On force la transparence de tous les blocs Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background: transparent !important;
    }

    /* Fond noir de base sous l'animation */
    body { background-color: #000000 !important; }

    /* 2. L'ANIMATION DE LA BRUME (FIXÉE AU FOND) */
    .fogwrapper {
        height: 100vh; position: fixed; top: 0; left: 0; width: 100vw;
        z-index: -10; overflow: hidden; pointer-events: none;
    }
    .foglayer {
        position: absolute; height: 100%; width: 200%;
        background: url("https://raw.githubusercontent.com/Anemolo/Fog-Effect/master/fog1.png") repeat-x;
        background-size: contain;
    }
    #layer1 { animation: fogmove 30s linear infinite; opacity: 0.3; }
    #layer2 { animation: fogmove 50s linear infinite; opacity: 0.15; top: 50px; }

    @keyframes fogmove {
        from { transform: translate3d(0, 0, 0); }
        to { transform: translate3d(-50%, 0, 0); }
    }

    /* 3. LISIBILITÉ DU CONTENU */
    .stForm { background-color: rgba(15, 15, 15, 0.8) !important; border: 1px solid #333 !important; }
    h1, h2, h3, h4, p, label { color: white !important; font-family: 'Courier New'; text-shadow: 2px 2px 4px #000; }
    
    /* Sidebar semi-transparente */
    [data-testid="stSidebar"] { background-color: rgba(10, 10, 10, 0.9) !important; }
    </style>

    <div class="fogwrapper">
        <div id="layer1" class="foglayer"></div>
        <div id="layer2" class="foglayer"></div>
    </div>
    """, unsafe_allow_html=True)
# --- 5. INITIALISATION DE LA SESSION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    u = st.session_state["user_login"]
    p = st.session_state["password_login"]
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else:
        st.error("Accès refusé. La brume vous rejette.")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 6. LOGIQUE D'AFFICHAGE ---
if not st.session_state['connected']:
    # PAGE DE CONNEXION
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
    # --- INTERFACE APPRÈS CONNEXION ---
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
        st.markdown(f'<marquee class="brouillard-text" scrollamount="5">⚠️ SESSION ACTIVE : {st.session_state["user_pseudo"].upper()} ⚠️</marquee>', unsafe_allow_html=True)

        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                df = conn.read(worksheet="Rapports", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df, new_row], ignore_index=True))
                st.snow()
                st.rerun() 
            except Exception as e: st.error(f"Erreur : {e}")

        # Formulaires (simplifiés pour l'exemple, garde tes versions si tu veux)
        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        # ... (Garder les autres onglets identiques) ...
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
                    # MODIFICATION DES COLONNES ICI
                    df_recap = stats[['Membre', 'Butin_x', 'Butin_y']].copy()
                    df_recap.columns = ['Membre', 'Actions', 'Drogue']
                    df_recap['Actions'] = df_recap['Actions'].apply(lambda x: f"{int(x):,.0f} $".replace(',', ' '))
                    df_recap['Drogue'] = df_recap['Drogue'].apply(lambda x: f"{int(x):,.0f} $".replace(',', ' '))
                    st.table(df_recap)
        except: pass


        # --- PAGE 2 : COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.write("## 🏛️ COMPTABILITÉ DE LA NIEBLA")
        with st.form("compta_form"):
            st.write("#### Enregistrer une Opération")
            c1, c2, c3 = st.columns(3)
            t_type = c1.selectbox("Type", ["Recette", "Dépense"])
            t_cat = c2.text_input("Catégorie")
            t_montant = c3.number_input("Montant ($)", min_value=0)
            t_note = st.text_area("Note / Justification")
            if st.form_submit_button("Enregistrer"):
                try:
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note}])
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.rerun()
                except: st.error("Erreur de connexion GSheets")

        st.markdown("---")
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                rec, dep = df_all[df_all['Type']=="Recette"]['Montant'].sum(), df_all[df_all['Type']=="Dépense"]['Montant'].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("Recettes", f"{rec:,.0f} $")
                m2.metric("Dépenses", f"{dep:,.0f} $")
                m3.metric("Solde", f"{rec-dep:,.0f} $", delta=float(rec-dep))
                st.dataframe(df_all.sort_values(by="Date", ascending=False), use_container_width=True)
        except: pass
