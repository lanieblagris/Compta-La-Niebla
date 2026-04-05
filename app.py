import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

# --- 2. STYLE CSS & BACKGROUND VIDEO ---
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
    .lore-quote {{
        font-family: 'Courier New', monospace; color: #888; font-size: 18px;
        text-align: center; letter-spacing: 2px; text-transform: uppercase;
        margin-bottom: 30px; opacity: 0.8; font-style: italic;
    }}
    #bgVideo {{
        position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
        z-index: -1000; filter: brightness(0.3); object-fit: cover;
    }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #444 !important; border-radius: 10px; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: white !important; font-family: 'Courier New', monospace; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.9) !important; }}
    [data-testid="stMetricValue"] {{ color: white !important; }}
    [data-testid="stMetricLabel"] {{ color: #bbb !important; }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION ET CACHE ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def load_data(sheet):
    return conn.read(worksheet=sheet)

# --- 4. GESTION DES UTILISATEURS (DYNAMIQUE VIA GSHEETS) ---
def get_all_users():
    try:
        df_users = conn.read(worksheet="Membres", ttl=0)
        return {str(row['Login']): {"password": str(row['Password']), "pseudo": row['Pseudo'], "role": row['Role']} for _, row in df_users.iterrows()}
    except:
        # Utilisateur de secours si l'onglet est vide ou inaccessible
        return {"Admin": {"password": "0000", "pseudo": "El Patron", "role": "Admin"}}

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    users = get_all_users()
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in users and users[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = users[u]["role"]
        st.session_state['user_pseudo'] = users[u]["pseudo"]

# --- 5. INTERFACE ---
if not st.session_state['connected']:
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    st.markdown('<div class="lore-quote">"Le Gris n\'est pas qu\'une couleur, c\'est une attitude."</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            st.text_input("NOM DE CODE", key="user_login")
            st.text_input("MOT DE PASSE", type="password", key="password_login")
            if st.form_submit_button("S'INFILTRER"):
                check_login()
                if st.session_state['connected']: st.rerun()
else:
    # --- BARRE LATÉRALE ---
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin": menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- TABLEAU DE BORD (MEMBRES) ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        st.markdown('<div class="lore-quote">"Le Gris n\'est pas qu\'une couleur, c\'est une attitude."</div>', unsafe_allow_html=True)
        
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px; margin-bottom:20px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])
        DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            new_row_rep = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
            new_row_treso = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
            
            success = False
            for _ in range(3):
                try:
                    df_rep = conn.read(worksheet="Rapports", ttl=0)
                    conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_row_rep], ignore_index=True))
                    df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_row_treso], ignore_index=True))
                    st.cache_data.clear()
                    success = True
                    break
                except: time.sleep(1)
            if success:
                st.success("Validé dans les archives.")
                time.sleep(1); st.rerun()
            else: st.error("Échec de connexion.")

        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b_atm")
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form("sup"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b_sup")
                if st.form_submit_button("VALIDER SUPERETTE"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form("gf"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b_gf")
                if st.form_submit_button("VALIDER GO FAST"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form("cam"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form("dr"):
                d_select = st.selectbox("🌿 Produit", DRUG_LIST)
                d_final = d_select
                if d_select == "Autre": d_final = st.text_input("Nom de la drogue")
                q = st.number_input("📦 Quantité vendue", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"):
                    if d_select == "Autre" and not d_final: st.error("Précisez le nom.")
                    else: handle_submit("Drogue", butin=b, drogue=d_final, quantite=-abs(q))

        # --- STATS ---
        st.markdown("---")
        st.write("### 📊 ACTIVITÉ HEBDOMADAIRE")
        try:
            data = load_data("Rapports")
            if not data.empty:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                start_week = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0)
                week_data = data[data['Date'] >= start_week].copy()
                
                users_list = get_all_users()
                for u_key in users_list:
                    pseudo = users_list[u_key]["pseudo"]
                    p_data = week_data[week_data['Membre'] == pseudo]
                    nb_act = len(p_data[p_data['Action'] != "Drogue"])
                    nb_dr = abs(p_data[p_data['Action'] == "Drogue"]['Quantite'].sum())
                    c1, c2, c3 = st.columns([1, 2, 2])
                    c1.write(f"**{pseudo}**")
                    c2.progress(min(nb_act/20, 1.0), text=f"Actions: {nb_act}")
                    c3.progress(min(nb_dr/300, 1.0), text=f"Drogue: {int(nb_dr)}")
        except: pass

    # --- COMPTABILITÉ GLOBALE (ADMIN) ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        sub_tabs = st.tabs(["📊 Finances", "🧼 Blanchiment", "📦 Stocks", "👥 Recrutement"])

        with sub_tabs[0]: # FINANCES
            with st.form("manual_op"):
                st.write("#### Enregistrer une transaction")
                c1, c2, c3, c4 = st.columns(4)
                t_type = c1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = c2.selectbox("Argent", ["Sale", "Propre"])
                t_cat = c3.text_input("Catégorie")
                t_montant = c4.number_input("Montant ($)", min_value=0)
                t_note = st.text_area("Note")
                if st.form_submit_button("VALIDER TRANSACTION"):
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note}])
                    for _ in range(3):
                        try:
                            df_c = conn.read(worksheet="Tresorerie", ttl=0)
                            conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                            st.cache_data.clear(); st.success("Enregistré."); time.sleep(1); st.rerun(); break
                        except: time.sleep(1)

        with sub_tabs[1]: # BLANCHIMENT
            with st.form("blanch_form"):
                st.write("#### Blanchiment d'argent")
                col_a, col_b = st.columns(2)
                m_sale = col_a.number_input("Montant sale ($)", min_value=0)
                taux = col_b.slider("Taux (%)", 0, 100, 20)
                propre = m_sale * (1 - taux/100)
                if st.form_submit_button("LANCER LE BLANCHIMENT"):
                    op_s = {"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Dépense", "Etat": "Sale", "Catégorie": "Blanchiment", "Montant": float(m_sale), "Note": "Sortie sale"}
                    op_p = {"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Propre", "Catégorie": "Blanchiment", "Montant": float(propre), "Note": f"Retour propre (-{taux}%)"}
                    for _ in range(3):
                        try:
                            df_t = conn.read(worksheet="Tresorerie", ttl=0)
                            conn.update(worksheet="Tresorerie", data=pd.concat([df_t, pd.DataFrame([op_s, op_p])], ignore_index=True))
                            st.cache_data.clear(); st.success("Transaction terminée."); time.sleep(1); st.rerun(); break
                        except: time.sleep(1)

        with sub_tabs[2]: # STOCKS
            with st.form("stock_form"):
                st.write("#### Gestion des Arrivages")
                c1, c2 = st.columns(2)
                d_n_sel = c1.selectbox("Produit", ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"])
                d_n_fin = d_n_sel
                if d_n_sel == "Autre": d_n_fin = st.text_input("Nom spécifique")
                d_q = c2.number_input("Quantité à ajouter", min_value=0.0)
                if st.form_submit_button("METTRE À JOUR LE STOCK"):
                    new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Drogue", "Drogue": d_n_fin, "Quantite": float(d_q), "Butin": 0}])
                    for _ in range(3):
                        try:
                            df_all_r = conn.read(worksheet="Rapports", ttl=0)
                            conn.update(worksheet="Rapports", data=pd.concat([df_all_r, new_s], ignore_index=True))
                            st.cache_data.clear(); st.success("Inventaire mis à jour."); time.sleep(1); st.rerun(); break
                        except: time.sleep(1)
            st.write("---")
            try:
                df_rep_s = load_data("Rapports")
                if not df_rep_s.empty:
                    df_drugs = df_rep_s[df_rep_s['Action'] == "Drogue"].copy()
                    stock_final = df_drugs.groupby('Drogue')['Quantite'].sum().reset_index()
                    cols = st.columns(4)
                    for i, row in stock_final.iterrows():
                        cols[i % 4].metric(row['Drogue'], f"{row['Quantite']:.1f} u")
            except: pass

        with sub_tabs[3]: # RECRUTEMENT (DYNAMIQUE)
            st.write("#### 👥 Recrutement & Familia")
            with st.form("recruit"):
                c1, c2, c3 = st.columns(3)
                n_log = c1.text_input("Login")
                n_pas = c2.text_input("Password")
                n_pse = c3.text_input("Pseudo RP")
                n_rol = st.selectbox("Rôle", ["Membre", "Admin"])
                if st.form_submit_button("INTÉGRER LE NOUVEAU MEMBRE"):
                    if n_log and n_pas and n_pse:
                        new_m = pd.DataFrame([{"Login": n_log, "Password": n_pas, "Pseudo": n_pse, "Role": n_rol}])
                        for _ in range(3):
                            try:
                                df_m = conn.read(worksheet="Membres", ttl=0)
                                conn.update(worksheet="Membres", data=pd.concat([df_m, new_m], ignore_index=True))
                                st.success(f"Bienvenue à {n_pse}."); time.sleep(1); st.rerun(); break
                            except: time.sleep(1)
            st.write("---")
            try:
                df_m_list = conn.read(worksheet="Membres", ttl=0)
                st.dataframe(df_m_list[["Pseudo", "Role", "Login"]], use_container_width=True)
            except: pass

        # --- FOOTER FINANCIER ---
        st.markdown("---")
        try:
            df_all = load_data("Tresorerie")
            if not df_all.empty:
                df_calc = df_all.dropna(subset=['Montant', 'Type', 'Etat'])
                rec_p = df_calc[(df_calc['Type']=="Recette") & (df_calc['Etat']=="Propre")]['Montant'].sum()
                dep_p = df_calc[(df_calc['Type']=="Dépense") & (df_calc['Etat']=="Propre")]['Montant'].sum()
                rec_s = df_calc[(df_calc['Type']=="Recette") & (df_calc['Etat']=="Sale")]['Montant'].sum()
                dep_s = df_calc[(df_calc['Type']=="Dépense") & (df_calc['Etat']=="Sale")]['Montant'].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("SOLDE PROPRE", f"{rec_p - dep_p:,.0f} $")
                m2.metric("SOLDE SALE", f"{rec_s - dep_s:,.0f} $")
                m3.metric("TOTAL GLOBAL", f"{(rec_p + rec_s) - (dep_p + dep_s):,.0f} $")
        except: pass
