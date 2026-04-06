import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ET CONSTANTES GLOBALES ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
# Liste des rangs disponibles pour la gestion
RANKS_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue"]

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
    .rank-card {{
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #555;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 5px;
    }}
    .rank-header {{ color: #888; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px; }}
    .member-name {{ font-size: 20px; color: white; font-family: 'Courier New', monospace; }}
    #bgVideo {{
        position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
        z-index: -1000; filter: brightness(0.3); object-fit: cover;
    }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #444 !important; border-radius: 10px; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: white !important; font-family: 'Courier New', monospace; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.9) !important; }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION ET CHARGEMENT DES MEMBRES ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_members_df():
    return conn.read(worksheet="Membres", ttl=0)

if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def reset_form():
    st.session_state.form_key += 1

# Chargement initial des membres pour l'auth
df_members = get_members_df()

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    user_row = df_members[(df_members['Login'] == u) & (df_members['Password'].astype(str) == str(p))]
    if not user_row.empty:
        st.session_state['connected'] = True
        st.session_state['user_login_id'] = u
        st.session_state['user_pseudo'] = user_row.iloc[0]['Pseudo']
        st.session_state['user_role'] = user_row.iloc[0]['Role']

# --- 4. AFFICHAGE ---
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
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        # On récupère le rang à jour
        current_rank = df_members[df_members['Login'] == st.session_state['user_login_id']]['Role'].values[0]
        st.write(f"**Rang :** {current_rank}")
        
        menu = ["Tableau de bord", "Hiérarchie Clan"]
        if st.session_state['user_role'] == "Admin": 
            menu.append("Gestion des Membres")
            menu.append("Comptabilité Globale")
            
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- ONGLET GESTION DES MEMBRES (ADMIN ONLY) ---
    if choice == "Gestion des Membres":
        st.markdown('<div class="gta-title">Admin</div>', unsafe_allow_html=True)
        st.write("### 🎖️ Gestion des Rangs")
        
        # On ne modifie pas le Patron lui-même pour éviter les erreurs d'accès
        members_to_edit = df_members[df_members['Role'] != 'Admin']
        
        for index, row in members_to_edit.iterrows():
            with st.expander(f"👤 {row['Pseudo']} (Actuel: {row['Role']})"):
                new_rank = st.selectbox(f"Nouveau rang pour {row['Pseudo']}", RANKS_LIST, 
                                        index=RANKS_LIST.index(row['Role']) if row['Role'] in RANKS_LIST else 0, 
                                        key=f"rank_{row['Login']}")
                if st.form_submit_button(f"Mettre à jour {row['Pseudo']}", key=f"btn_{row['Login']}"):
                    df_members.at[index, 'Role'] = new_rank
                    conn.update(worksheet="Membres", data=df_members)
                    st.success(f"Rang mis à jour !")
                    time.sleep(1)
                    st.rerun()

    # --- ONGLET HIÉRARCHIE ---
    elif choice == "Hiérarchie Clan":
        st.markdown('<div class="gta-title">Organigrama</div>', unsafe_allow_html=True)
        # Affichage par ordre de RANKS_LIST
        for rank in RANKS_LIST:
            m_list = df_members[df_members['Role'] == rank]['Pseudo'].tolist()
            if m_list:
                st.markdown(f"""
                <div class="rank-card">
                    <div class="rank-header">{rank}</div>
                    <div class="member-name">{' • '.join(m_list)}</div>
                </div>
                """, unsafe_allow_html=True)

    # --- TABLEAU DE BORD ---
    elif choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px; margin-bottom:20px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                new_row_rep = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_row_treso = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_row_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_row_treso], ignore_index=True))
                st.success("Transmis avec succès.")
                time.sleep(1); reset_form(); st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        # Formulaires de saisie
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
                q = st.number_input("📦 Quantité", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d_select, quantite=-abs(q))

        # --- STATISTIQUES (MASQUER LE PATRON) ---
        st.markdown("---")
        st.write("### 📊 STATISTIQUES DE LA SEMAINE")
        try:
            df_stats = conn.read(worksheet="Rapports", ttl=0)
            if not df_stats.empty:
                df_stats['Date'] = pd.to_datetime(df_stats['Date'], errors='coerce')
                start_week = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
                week_data = df_stats[df_stats['Date'] >= start_week].copy()
                
                # On utilise les pseudos de la feuille Membres
                for _, m_row in df_members.iterrows():
                    if m_row['Role'] != "Admin":
                        pseudo = m_row['Pseudo']
                        user_data = week_data[week_data['Membre'] == pseudo]
                        nb_actions = len(user_data[user_data['Action'] != "Drogue"])
                        nb_ventes = abs(user_data[user_data['Action'] == "Drogue"]['Quantite'].sum())
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{pseudo}**")
                        c2.progress(min(float(nb_actions)/20, 1.0), text=f"Actions: {nb_actions}")
                        c3.progress(min(float(nb_ventes)/300, 1.0), text=f"Ventes: {int(nb_ventes)}")
        except: pass

    # --- COMPTABILITÉ GLOBALE ---
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
                        df_t = conn.read(worksheet="Tresorerie", ttl=0)
                        ops = pd.DataFrame([
                            {"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Dépense", "Etat": "Sale", "Catégorie": "Blanchiment", "Montant": float(m_sale), "Note": "Sortie blanchiment"},
                            {"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Propre", "Catégorie": "Blanchiment", "Montant": float(propre), "Note": f"Retour (-{taux}%)"}
                        ])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_t, ops], ignore_index=True))
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
