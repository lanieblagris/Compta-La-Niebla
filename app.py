import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ET CONSTANTES GLOBALES ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
ROLES_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue", "Infiltré"]

# --- 2. STYLE CSS & BACKGROUND ---
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

# --- 3. CONNEXION ET FONCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def log_invisible(action, details=""):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        df_r = conn.read(worksheet="Rapports", ttl=0)
        new_log = pd.DataFrame([{
            "Date": ts,
            "Membre": st.session_state.get('user_pseudo', 'Système'),
            "Action": f"[LOG] {action}",
            "Drogue": "N/A", "Quantite": 0, "Butin": 0, "Note": details
        }])
        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_log], ignore_index=True))
    except: pass

def get_members():
    return conn.read(worksheet="Membres", ttl=0)

if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def reset_form():
    st.session_state.form_key += 1

def check_login():
    df_m = get_members()
    st.write("--- DEBUG ---")
st.write("Colonnes détectées :", df_m.columns.tolist())
st.write("Nombre de membres trouvés :", len(df_m))
st.dataframe(df_m) # Affiche le tableau complet pour vérifier
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    
    # Recherche du membre dans la feuille Google Sheets
    user_row = df_m[(df_m['Login'] == u) & (df_m['Password'].astype(str) == str(p))]
    
    if not user_row.empty:
        st.session_state['connected'] = True
        # Si c'est le compte Admin, on lui donne le rôle Admin système
        st.session_state['user_role'] = "Admin" if u == "Admin" else user_row.iloc[0]['Role']
        st.session_state['user_login_name'] = u
        st.session_state['user_pseudo'] = user_row.iloc[0]['Pseudo']
        log_invisible("Connexion", f"Login réussi pour {u}")
    else:
        st.error("Accès refusé.")

# --- 4. AFFICHAGE ET NAVIGATION ---
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
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        st.write(f"Grade : **{st.session_state['user_role']}**")
        menu = ["Tableau de bord"]
        # Seul le Login "Admin" a accès aux outils de gestion
        if st.session_state['user_login_name'] == "Admin": 
            menu.append("Comptabilité Globale")
            menu.append("Gestion des Membres")
            menu.append("Archives de la Niebla")
            
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            log_invisible("Déconnexion", "Session fermée")
            st.session_state.clear()
            st.rerun()

    # --- PAGE : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px; margin-bottom:20px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                new_row_rep = pd.DataFrame([{"Date": now, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_row_treso = pd.DataFrame([{"Date": now, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_row_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_row_treso], ignore_index=True))
                st.success("Transmis avec succès.")
                time.sleep(1); reset_form(); st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form(key=f"sup_{st.session_state.form_key}"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER SUPERETTE"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form(key=f"gf_{st.session_state.form_key}"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER GO FAST"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form(key=f"cam_{st.session_state.form_key}"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form(key=f"dr_{st.session_state.form_key}"):
                d_select = st.selectbox("🌿 Produit", DRUG_LIST)
                d_final = d_select
                if d_select == "Autre": d_final = st.text_input("Nom spécifique")
                q = st.number_input("📦 Quantité", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d_final, quantite=-abs(q))
               
        st.markdown("---")
        st.write("### 📊 STATISTIQUES DE LA SEMAINE")
        try:
            df_stats = conn.read(worksheet="Rapports", ttl=0)
            df_m_list = get_members()
            if not df_stats.empty:
                df_stats['Date'] = pd.to_datetime(df_stats['Date'], errors='coerce')
                start_week = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
                week_data = df_stats[(df_stats['Date'] >= start_week) & (~df_stats['Action'].str.contains(r'\[LOG\]', na=False))].copy()
                
                for _, m_row in df_m_list.iterrows():
                    if m_row['Login'] != "Admin":
                        pseudo = m_row["Pseudo"]
                        user_data = week_data[week_data['Membre'] == pseudo]
                        nb_actions = len(user_data[user_data['Action'] != "Drogue"])
                        nb_ventes = abs(user_data[user_data['Action'] == "Drogue"]['Quantite'].sum())
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{pseudo}**")
                        c2.progress(min(float(nb_actions)/20, 1.0), text=f"Actions: {nb_actions}")
                        c3.progress(min(float(nb_ventes)/300, 1.0), text=f"Ventes: {int(nb_ventes)}")
        except: pass

    # --- PAGE : GESTION DES MEMBRES (ADMIN UNIQUEMENT) ---
    elif choice == "Gestion des Membres":
        st.markdown('<div class="gta-title">Membres</div>', unsafe_allow_html=True)
        df_m = get_members()
        st.write("### 🗃️ Liste des membres et grades")
        
        for index, row in df_m.iterrows():
            if row['Login'] == "Admin": continue
            
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(f"👤 **{row['Pseudo']}**")
            
            # Sélecteur de rôle
            current_role = row['Role']
            idx = ROLES_LIST.index(current_role) if current_role in ROLES_LIST else 0
            new_role = col2.selectbox(f"Grade de {row['Login']}", ROLES_LIST, index=idx, key=f"sel_{row['Login']}")
            
            if col3.button("Mettre à jour", key=f"btn_{row['Login']}"):
                df_m.at[index, 'Role'] = new_role
                conn.update(worksheet="Membres", data=df_m)
                log_invisible("Grade", f"{row['Pseudo']} promu {new_role}")
                st.success("Mis à jour !"); time.sleep(1); st.rerun()

    # --- PAGE : ARCHIVES ---
    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        try:
            df_arc = conn.read(worksheet="Rapports", ttl=0)
            filtre = st.radio("Affichage", ["Toutes", "Rapports", "Logs Système"], horizontal=True)
            if filtre == "Rapports": df_arc = df_arc[~df_arc['Action'].str.contains(r'\[LOG\]', na=False)]
            elif filtre == "Logs Système": df_arc = df_arc[df_arc['Action'].str.contains(r'\[LOG\]', na=False)]
            st.dataframe(df_arc.sort_index(ascending=False), use_container_width=True)
        except: st.error("Erreur archives.")

    # --- PAGE : COMPTABILITÉ ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        sub_tabs = st.tabs(["📊 Vue d'ensemble", "🧼 Blanchiment", "📦 Gestion des Stocks"])
        
        with sub_tabs[0]:
            with st.form(key=f"man_{st.session_state.form_key}"):
                st.write("#### Opération Manuelle")
                col1, col2, col3, col4 = st.columns(4)
                t_type = col1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = col2.selectbox("Argent", ["Sale", "Propre"])
                t_cat = col3.text_input("Catégorie")
                t_montant = col4.number_input("Montant ($)", min_value=0)
                t_note = st.text_area("Note")
                if st.form_submit_button("Valider"):
                    try:
                        new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note}])
                        df_c = conn.read(worksheet="Tresorerie", ttl=0)
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                        log_invisible("Compta", f"Opération manuelle: {t_cat}")
                        st.success("Enregistré."); time.sleep(1); reset_form(); st.rerun()
                    except: st.error("Erreur Sheets.")

        with sub_tabs[1]:
            with st.form(key=f"bl_{st.session_state.form_key}"):
                st.write("#### 🧼 Blanchisseur")
                ca, cb = st.columns(2)
                m_sale = ca.number_input("Montant sale ($)", min_value=0)
                taux = cb.slider("Taux (%)", 0, 100, 20)
                if st.form_submit_button("BLANCHIR"):
                    try:
                        propre = m_sale * (1 - taux/100)
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        op_s = {"Date": now, "Type": "Dépense", "Etat": "Sale", "Catégorie": "Blanchiment", "Montant": float(m_sale), "Note": "Sortie blanchiment"}
                        op_p = {"Date": now, "Type": "Recette", "Etat": "Propre", "Catégorie": "Blanchiment", "Montant": float(propre), "Note": f"Retour (-{taux}%)"}
                        df_t = conn.read(worksheet="Tresorerie", ttl=0)
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_t, pd.DataFrame([op_s, op_p])], ignore_index=True))
                        log_invisible("Blanchiment", f"{m_sale}$ lavés")
                        st.success("Blanchi !"); time.sleep(1); reset_form(); st.rerun()
                    except: st.error("Erreur.")

        with sub_tabs[2]:
            with st.form(key=f"stk_{st.session_state.form_key}"):
                st.write("#### 📦 Gestion des Stocks")
                cs1, cs2 = st.columns(2)
                d_name = cs1.selectbox("Produit", DRUG_LIST)
                d_qty = cs2.number_input("Quantité", min_value=0.0)
                if st.form_submit_button("VALIDER L'ARRIVAGE"):
                    try:
                        new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Drogue", "Drogue": d_name, "Quantite": float(d_qty), "Butin": 0}])
                        df_all_r = conn.read(worksheet="Rapports", ttl=0)
                        conn.update(worksheet="Rapports", data=pd.concat([df_all_r, new_s], ignore_index=True))
                        log_invisible("Stock", f"Ajout {d_qty} {d_name}")
                        st.success("Stock mis à jour !"); time.sleep(1); reset_form(); st.rerun()
                    except: st.error("Erreur Sheets.")

        try:
            df_view = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_view.empty:
                st.markdown("---")
                def calc(df, et):
                    sub = df[df['Etat'] == et]
                    return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
                s_sale, s_propre = calc(df_view, 'Sale'), calc(df_view, 'Propre')
                c1, c2, c3 = st.columns(3)
                c1.metric("SOLDE PROPRE", f"{s_propre:,.0f} $")
                c2.metric("SOLDE SALE", f"{s_sale:,.0f} $")
                c3.metric("TOTAL GLOBAL", f"{(s_propre+s_sale):,.0f} $")
                st.dataframe(df_view.sort_index(ascending=False).head(10), use_container_width=True)
        except: pass
