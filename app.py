import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
ROLES_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue", "Infiltré"]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #000000; }
    .gta-title {
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 5px 5px 15px #000; margin-top: -60px; margin-bottom: 10px;
    }
    .stForm { background-color: rgba(10, 10, 10, 0.9) !important; border: 1px solid #444 !important; border-radius: 10px; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: white !important; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.9) !important; }
    [data-testid="stMetricValue"] { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FONCTIONS SYSTÈME & CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_members():
    try:
        return conn.read(worksheet="Membres", ttl=0)
    except:
        return pd.DataFrame(columns=["Login", "Password", "Pseudo", "Role"])

def log_invisible(action, details=""):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        df_r = conn.read(worksheet="Rapports", ttl=0)
        new_log = pd.DataFrame([{"Date": ts, "Membre": st.session_state.get('user_pseudo', 'Système'), "Action": f"[LOG] {action}", "Drogue": "N/A", "Quantite": 0, "Butin": 0, "Note": details}])
        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_log], ignore_index=True))
    except: pass

if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def reset_form():
    st.session_state.form_key += 1

def check_login():
    df_m = get_members()
    u_input = st.session_state.get("user_login")
    p_input = str(st.session_state.get("password_login"))
    
    if not df_m.empty:
        df_m['Login'] = df_m['Login'].astype(str)
        # Nettoyage automatique des .0 si Google Sheets transforme le MDP en nombre
        df_m['Password'] = df_m['Password'].astype(str).str.replace('.0', '', regex=False)
        
        user_row = df_m[(df_m['Login'] == u_input) & (df_m['Password'] == p_input)]
        
        if not user_row.empty:
            st.session_state['connected'] = True
            st.session_state['user_login_name'] = u_input
            st.session_state['user_role'] = "Admin" if u_input == "Admin" else user_row.iloc[0]['Role']
            st.session_state['user_pseudo'] = user_row.iloc[0]['Pseudo']
            log_invisible("Connexion", "Succès")
            return
    st.error("Identifiants incorrects.")

# --- 3. PAGE DE CONNEXION ---
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
    # --- 4. NAVIGATION ---
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        st.write(f"Grade : **{st.session_state['user_role']}**")
        menu = ["Tableau de bord"]
        if st.session_state['user_login_name'] == "Admin": 
            menu += ["Comptabilité Globale", "Gestion des Membres", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- PAGE : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                
                new_rep = pd.DataFrame([{"Date": now, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_treso = pd.DataFrame([{"Date": now, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Transmis !"); time.sleep(1); reset_form(); st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form(key=f"sup_{st.session_state.form_key}"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER SUPERETTE"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form(key=f"gf_{st.session_state.form_key}"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER GO FAST"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form(key=f"cam_{st.session_state.form_key}"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form(key=f"dr_{st.session_state.form_key}"):
                d_select = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Quantité", min_value=0.0)
                b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d_select, quantite=-abs(q))

        st.markdown("---")
        st.write("### 📊 STATS DE LA SEMAINE")
        try:
            df_s = conn.read(worksheet="Rapports", ttl=0)
            df_m = get_members()
            if not df_s.empty:
                df_s['Date'] = pd.to_datetime(df_s['Date'], errors='coerce')
                lundi = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
                # On filtre les logs système pour ne pas fausser les stats
                week_data = df_s[(df_s['Date'] >= lundi) & (~df_s['Action'].str.contains(r'\[LOG\]', na=False))]
                
                for _, m in df_m.iterrows():
                    if m['Login'] != "Admin":
                        p = m['Pseudo']
                        u_data = week_data[week_data['Membre'] == p]
                        act = len(u_data[u_data['Action'] != "Drogue"])
                        vnt = abs(u_data[u_data['Action'] == "Drogue"]['Quantite'].sum())
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{p}**")
                        c2.progress(min(float(act)/20, 1.0), text=f"Actions: {act}")
                        c3.progress(min(float(vnt)/300, 1.0), text=f"Ventes: {int(vnt)}")
        except: pass

    # --- PAGE : GESTION MEMBRES (ADMIN) ---
    elif choice == "Gestion des Membres":
        st.markdown('<div class="gta-title">Membres</div>', unsafe_allow_html=True)
        df_m = get_members()
        for i, r in df_m.iterrows():
            if r['Login'] == "Admin": continue
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"👤 **{r['Pseudo']}**")
            curr_r = r['Role']
            new_r = c2.selectbox(f"Grade", ROLES_LIST, index=ROLES_LIST.index(curr_r) if curr_r in ROLES_LIST else 0, key=f"r_{r['Login']}")
            if c3.button("MAJ", key=f"b_{r['Login']}"):
                df_m.at[i, 'Role'] = new_r
                conn.update(worksheet="Membres", data=df_m)
                log_invisible("Grade", f"{r['Pseudo']} -> {new_r}")
                st.success("Fait !"); time.sleep(1); st.rerun()

    # --- PAGE : COMPTABILITÉ (ADMIN) ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["📊 Solde", "🧼 Blanchiment", "📦 Stocks"])
        
        with t1:
            with st.form("op_man"):
                st.write("#### Opération Manuelle")
                col1, col2, col3 = st.columns(3)
                typ = col1.selectbox("Type", ["Recette", "Dépense"])
                et = col2.selectbox("Argent", ["Sale", "Propre"])
                mnt = col3.number_input("Montant ($)", min_value=0)
                cat = st.text_input("Catégorie / Note")
                if st.form_submit_button("Enregistrer"):
                    try:
                        df_c = conn.read(worksheet="Tresorerie", ttl=0)
                        new_o = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": typ, "Etat": et, "Catégorie": "Manuel", "Montant": float(mnt), "Note": cat}])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_o
