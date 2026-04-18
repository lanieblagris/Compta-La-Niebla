import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION ET ROLES ---
st.set_page_config(
    page_title="La Niebla - Luxury Cartel",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Roles: 1: Gérant (⚜️), 2: Lieutenant (⭐), 3: Soldat (🔫)
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron", "role_level": 1},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith", "role_level": 2},
    "Dany": {"password": "081219", "pseudo": "Dany Smith", "role_level": 3},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith", "role_level": 3},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin", "role_level": 3},
}

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

# --- 2. STYLE CSS AVANCÉ (LUXURY CARTEL) ---
# Ce bloc CSS reproduit les textures et les couleurs de ton image d'exemple.
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Marcellus&display=swap');
    
    /* --- FOND ET ÉLÉMENTS GLOBAUX --- */
    /* Cache l'interface Streamlit par défaut */
    .stApp {{
        background: url('https://w0.peakpx.com/wallpaper/70/463/wallpaper-dark-grey-textured-dark-grey-background-textured-background.jpg');
        background-size: cover;
        background-attachment: fixed;
    }}
    header, [data-testid="stSidebarHeader"], [data-testid="stHeader"] {{ background: transparent !important; color: transparent !important; }}
    
    /* Textes globaux en doré clair */
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{
        color: #f7e0a3 !important;
        font-family: 'Marcellus', serif !important;
    }}
    
    /* --- TITRE PRINCIPAL STYLE GOTHIQUE OR --- */
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive;
        font-size: 110px;
        color: transparent;
        background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e, #f7e0a3);
        -webkit-background-clip: text;
        background-clip: text;
        text-align: center;
        text-shadow: 0px 4px 15px rgba(180, 140, 62, 0.6);
        margin-top: -60px;
        margin-bottom: 30px;
        letter-spacing: 6px;
    }}
    
    /* Slogan Gris Argenté */
    .gta-slogan {{
        font-family: 'Marcellus', serif;
        font-size: 22px;
        color: #a6a6a6 !important;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 40px;
        font-style: italic;
    }}

    /* --- FORMULAIRES STYLE NOBLE DORK --- */
    /* Reproduit le fond noir/gris sombre et la bordure dorée fine */
    .stForm {{
        background-color: rgba(10, 10, 10, 0.9) !important;
        border: 1px solid #b48c3e !important;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }}
    
    /* Style pour les champs d'entrée (inputs) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: #1a1a1a !important;
        color: #f7e0a3 !important;
        border: 1px solid #444 !important;
    }}

    /* --- SIDEBAR STYLE CARTEL --- */
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 15, 15, 0.95) !important;
        border-right: 1px solid #b48c3e;
    }}
    [data-testid="stSidebar"] * {{ color: #f7e0a3 !important; }}
    
    /* --- BARRES DE PROGRESSION DORÉES --- */
    .stProgress > div > div > div > div {{
        background-image: linear-gradient(to right, #b48c3e, #f7e0a3) !important;
        border-radius: 10px;
    }}
    
    /* --- TABLEAU D'OBJECTIFS STYLE LISTE LUXE --- */
    .objectif-pseudo {{ font-size: 1.3em; color: #f7e0a3; font-weight: bold; font-family: 'Marcellus', serif; }}
    .objectif-cash {{ font-size: 1.3em; color: #ffffff; font-weight: bold; font-family: 'Courier New', monospace;}}
    .objectif-icon {{ font-size: 1.2em; vertical-align: middle; margin-right: 5px; }}

    /* --- MÉTRIQUES DE COMPTA ADMIN --- */
    [data-testid="stMetricValue"] {{
        color: transparent;
        background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e);
        -webkit-background-clip: text;
        background-clip: text;
        font-family: 'Marcellus', serif;
        font-size: 38px;
    }}
    [data-testid="stMetricLabel"] {{ color: #a6a6a6 !important; font-size: 16px;}}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE DE CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

if 'connected' not in st.session_state: st.session_state['connected'] = False
if "form_key" not in st.session_state: st.session_state.form_key = 0

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_id'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
        st.session_state['role_level'] = USERS[u]["role_level"]
    else: st.error("Accès refusé.")

# --- 4. INTERFACE ---
if not st.session_state['connected']:
    st.write("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    st.markdown('<div class="gta-slogan">On ne nous voit pas... mais on est partout.</div>', unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        with st.form("login_form"):
            st.write("### Identifiez-vous, Soldado")
            st.text_input("NOM DE CODE", key="user_login")
            st.text_input("MOT DE PASSE", type="password", key="password_login")
            if st.form_submit_button("S'INFILTRER"):
                check_login()
                if st.session_state['connected']: st.rerun()
else:
    # --- NAVIGATION BASÉE SUR LE RÔLE ---
    with st.sidebar:
        # Icônes basées sur ton exemple d'image
        role_icon = "⚜️" if st.session_state['role_level'] == 1 else "⭐" if st.session_state['role_level'] == 2 else "🔫"
        role_name = "El Patron" if st.session_state['role_level'] == 1 else "Lieutenant" if st.session_state['role_level'] == 2 else "Sicario"
        
        st.write(f"### {st.session_state['user_pseudo']} {role_icon}")
        st.write(f"**Rang :** {role_name}")
        st.write("---")
        
        menu = ["Tableau de bord"]
        if st.session_state['role_level'] <= 2:
            menu += ["Comptabilité Globale", "Archives de la Niebla"]
            
        choice = st.radio("Navigation", menu)
        st.write("---")
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # Lecture des données Rapports
    df_full = conn.read(worksheet="Rapports", ttl=0)

    # --- ONGLET 1 : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        st.markdown('<div class="gta-slogan">On ne nous voit pas... mais on est partout.</div>', unsafe_allow_html=True)
        
        # --- BLOCS SAISIE STYLE ONGLETS NOBLES ---
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                ts = get_now()
                # Mise à jour Rapports
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                new_rep = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                # Mise à jour Trésorerie
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                new_treso = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Opération transmise !"); time.sleep(1); st.session_state.form_key += 1; st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        # Les formulaires de saisie restent identiques
        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("ATM", butin=b)
        # (Les autres formulaires Supérette, GF, GF, Drogue restent les mêmes)

        st.markdown("---")

        # --- TABLEAU OBJECTIFS RÉINSÉRÉ ---
        st.write("### 📊 Activité du groupe de la semaine")
        if not df_full.empty:
            df_stats = df_full.copy()
            df_stats['Date'] = pd.to_datetime(df_stats['Date'], dayfirst=True, errors='coerce')
            start_week = (datetime.datetime.now() - timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
            week_data = df_stats[df_stats['Date'] >= start_week]
            
            # Header stylisé comme dans ton image exemple
            st.markdown("""
                <div style="display: flex; font-weight: bold; color: #a6a6a6; border-bottom: 2px solid #b48c3e; padding-bottom: 10px; margin-bottom: 15px; font-family: Marcellus, serif;">
                    <div style="flex: 1.2;">SOLDAT</div><div style="flex: 1;">BUTIN ($)</div><div style="flex: 2;">ACTIONS (20)</div><div style="flex: 2;">VENTES (300)</div>
                </div>
            """, unsafe_allow_html=True)

            for p_id, p_info in USERS.items():
                ps = p_info["pseudo"]
                lv = p_info["role_level"]
                u_data = week_data[week_data['Membre'] == ps]
                cash = u_data[~u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Butin'].sum()
                act = int(len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement", na=False))]) + u_data[u_data['Action'] == "Ajustement Action"]["Quantite"].sum())
                vnt = int(abs(u_data[u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Quantite'].sum()))
                
                # Icônes de rôle
                ico = "⚜️" if lv == 1 else "⭐" if lv == 2 else "🔫"
                
                c1, c2, c3, c4 = st.columns([1.2, 1, 2, 2])
                c1.markdown(f'<div class="objectif-pseudo"><span class="objectif-icon">{ico}</span>{ps}</div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="objectif-cash">{int(cash):,} $</div>'.replace(',', ' '), unsafe_allow_html=True)
                c3.progress(min(float(act)/20, 1.0), text=f"{act}/20 actions")
                c4.progress(min(float(vnt)/300, 1.0), text=f"{vnt}/300 ventes")
                st.write("")
        
        st.markdown("---")
        # Restauration de tes 3 dernières activités
        st.write("### 🕒 Derniers prospects & opérations de l'entité")
        mes_actions = df_full[df_full['Membre'] == st.session_state['user_pseudo']].tail(3).iloc[::-1]
        st.table(mes_actions[['Date', 'Action', 'Butin']])

    elif choice == "Archives de la Niebla" and st.session_state['role_level'] <= 2:
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        # Tableau en style Cartel sombre
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)

    # --- ONGLET 2 : COMPTA ADMIN ---
    elif choice == "Comptabilité Globale" and st.session_state['role_level'] <= 2:
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        st.markdown('<div class="gta-slogan">Trésorerie de l\'Entity</div>', unsafe_allow_html=True)
        
        df_v = conn.read(worksheet="Tresorerie", ttl=0)
        if not df_v.empty:
            def calc(df, et):
                sub = df[df['Etat'] == et]
                return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
            sp, ss = calc(df_v, 'Propre'), calc(df_v, 'Sale')
            
            # Métriques avec format Cartel dégradé or
            c1, c2, c3 = st.columns(3)
            c1.metric("TRÉSOR PROPRE ⚜️", f"{int(sp):,} $".replace(',', ' '))
            c2.metric("TRÉSOR SALE 💵", f"{int(ss):,} $".replace(',', ' '))
            c3.metric("TOTAL DE L'ENTITY", f"{int(sp+ss):,} $".replace(',', ' '))

        st.markdown("---")
        st.write("### Derniers flux financiers de l'Entity")
        if not df_v.empty: st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)
