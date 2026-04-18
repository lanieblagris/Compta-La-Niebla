import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION ET CONSTANTES ---
st.set_page_config(page_title="La Niebla - Cartel del Oro", page_icon="💰", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith"},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin"},
}

# --- 2. STYLE CSS CARTEL (GRIS/OR) ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

st.markdown(f"""
    <style>
    /* Police gothique pour le titre */
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    
    .stApp {{ background: transparent !important; }}
    
    /* Fond gris très sombre anthracite */
    body {{ background-color: #1a1a1a; color: #d4af37; }}

    /* Titre Principal style Cartel - OR */
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 100px; color: #d4af37;
        text-align: center; text-shadow: 4px 4px 10px #000, 0 0 25px #d4af37;
        margin-top: -60px; margin-bottom: 20px; letter-spacing: 5px;
    }}
    
    /* Titres secondaires - GRIS ARGENTÉ */
    h1, h2, h3, h4 {{ color: #a6a6a6 !important; font-family: 'Courier New', monospace; font-weight: bold; }}
    
    /* Textes et Labels - OR PALLED */
    p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: #d4af37 !important; font-family: 'Courier New', monospace; }}
    
    /* Fond des formulaires - GRIS ARDOISE AVEC BORDURE OR */
    .stForm {{ 
        background-color: #262626 !important; 
        border: 2px solid #d4af37 !important; 
        border-radius: 10px; 
        padding: 20px; 
    }}
    
    /* Sidebar - GRIS TRÈS SOMBRE/OR */
    [data-testid="stSidebar"] {{ background-color: #1a1a1a !important; border-right: 1px solid #d4af37; }}
    [data-testid="stSidebar"] * {{ color: #d4af37 !important; }}
    
    /* Barres de progression - OR */
    .stProgress > div > div > div > div {{ background-color: #d4af37 !important; }}
    
    /* Style pour les colonnes du tableau d'objectifs */
    .objectif-row {{ margin-bottom: 15px; padding: 10px; border-bottom: 1px solid #333; }}
    .objectif-pseudo {{ font-size: 1.1em; color: #d4af37; font-weight: bold; }}
    .objectif-cash {{ font-size: 1.1em; color: #00ff00; font-weight: bold; font-family: 'Courier New', monospace;}}
    
    /* Style pour les métriques de compta admin - OR */
    [data-testid="stMetricValue"] {{ color: #d4af37 !important; font-family: 'Courier New', monospace; font-size: 32px; }}
    [data-testid="stMetricLabel"] {{ color: #a6a6a6 !important; }}
    
    /* Assombrir la vidéo de fond */
    #bgVideo {{ filter: brightness(0.3); }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS SYSTÈME ---
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
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else: st.error("Accès refusé.")

# --- 4. INTERFACE ---
if not st.session_state['connected']:
    st.write("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="gta-title">Cartel del Oro</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            st.write("### Identifiez-vous, Soldado")
            st.text_input("NOM DE CODE", key="user_login")
            st.text_input("MOT DE PASSE", type="password", key="password_login")
            if st.form_submit_button("S'INFILTRER"):
                check_login()
                if st.session_state['connected']: st.rerun()
else:
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin": 
            menu += ["Comptabilité Globale", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        st.write("---")
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    df_full = conn.read(worksheet="Rapports", ttl=0)

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">Cartel del Oro</div>', unsafe_allow_html=True)
        
        # --- SAISIE DES ACTIVITÉS ---
        st.write("### 📝 Déclarer une Opération")
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                ts = get_now()
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                new_rep = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_treso = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Opération transmise !"); time.sleep(1); st.session_state.form_key += 1; st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        # Les formulaires de saisie restent fonctionnellement identiques
        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form(key=f"sup_{st.session_state.form_key}"):
                b = st.number_input("Butin Supérette ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form(key=f"gf_{st.session_state.form_key}"):
                b = st.number_input("Butin Go Fast ($)", min_value=0)
                if st.form_submit_button("VALIDER"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form(key=f"cam_{st.session_state.form_key}"):
                if st.form_submit_button("VALIDER"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form(key=f"dr_{st.session_state.form_key}"):
                d_select = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Quantité", min_value=0.0)
                b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d_select, quantite=-abs(q))

        st.markdown("---")

        # --- OBJECTIFS DE LA SEMAINE (CARTEL Gris/Or) ---
        st.write("### 📊 État de Service des Soldats (dollars inclus)")
        if not df_full.empty:
            df_stats = df_full.copy()
            df_stats['Date'] = pd.to_datetime(df_stats['Date'], dayfirst=True, errors='coerce')
            today = datetime.datetime.now()
            start_week = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            
            week_data = df_stats[
                (df_stats['Date'] >= start_week) & 
                (~df_stats['Action'].str.contains(r'\[LOG\]', na=False, case=False))
            ]
            
            # Header du tableau stylisé
            st.markdown("""
                <div style="display: flex; font-weight: bold; color: #a6a6a6; padding: 10px 0; border-bottom: 2px solid #d4af37; margin-bottom: 10px;">
                    <div style="flex: 1.2;">SOLDADO</div>
                    <div style="flex: 1;">TRÉSOR RÉCOLTÉ ($)</div>
                    <div style="flex: 2;">ACTIONS (Cible: 20)</div>
                    <div style="flex: 2;">VENTES (Cible: 300)</div>
                </div>
            """, unsafe_allow_html=True)

            for p_id, p_info in USERS.items():
                ps = p_info["pseudo"]
                u_data = week_data[week_data['Membre'] == ps]
                
                total_cash = u_data['Butin'].sum()
                normal_actions = len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement", na=False))])
                adj_actions = u_data[u_data['Action'] == "Ajustement Action"]["Quantite"].sum()
                total_actions = int(normal_actions + adj_actions)
                total_ventes = abs(u_data[u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Quantite'].sum())
                
                # Affichage des colonnes avec CSS personnalisé
                c1, c2, c3, c4 = st.columns([1.2, 1, 2, 2])
                c1.markdown(f'<div class="objectif-pseudo">{ps}</div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="objectif-cash">{int(total_cash):,} $</div>'.replace(',', ' '), unsafe_allow_html=True)
                c3.progress(min(float(total_actions)/20, 1.0), text=f"{total_actions}/20")
                c4.progress(min(float(total_ventes)/300, 1.0), text=f"{int(total_ventes)}/300")
                st.write("") # Espace
        else:
            st.info("Aucune donnée pour cette semaine de services.")

    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        # Tableau en style cartel (sombre avec accents dorés)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Compta Admin</div>', unsafe_allow_html=True)
        
        with st.expander("🛠️ CORRIGER/AJOUTER OBJECTIFS D'UN SOLDADO"):
            with st.form("adj_manual_bulk"):
                target_user = st.selectbox("Soldat à créditer", [u["pseudo"] for u in USERS.values()])
                adj_type = st.radio("Type de crédit", ["Actions (Cambriolages, ATM...)", "Ventes de Drogue"])
                adj_val = st.number_input("Nombre à ajouter au bilan", min_value=1, step=1)
                
                if st.form_submit_button("APPLIQUER LE CRÉDIT"):
                    try:
                        ts = get_now()
                        if adj_type == "Actions (Cambriolages, ATM...)":
                            name = "Ajustement Action"; q_to_save = float(adj_val)
                        else:
                            name = "Ajustement Ventes"; q_to_save = -float(adj_val)
                            
                        df_r = conn.read(worksheet="Rapports", ttl=0)
                        new_line = pd.DataFrame([{"Date": ts, "Membre": target_user, "Action": name, "Drogue": "N/A", "Quantite": q_to_save, "Butin": 0}])
                        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_line], ignore_index=True))
                        st.success(f"Opération réussie. Le bilan de {target_user} a été mis à jour."); time.sleep(1); st.rerun()
                    except Exception as e: st.error(e)

        st.markdown("---")

        with st.expander("➕ Opération financière manuelle (Recette/Dépense)"):
            with st.form("man_fin"):
                c_a, c_b = st.columns(2)
                m_t = c_a.selectbox("Type", ["Recette", "Dépense"])
                m_e = c_b.selectbox("État", ["Sale", "Propre"])
                m_c = st.text_input("Catégorie")
                m_v = st.number_input("Montant ($)", min_value=0)
                if st.form_submit_button("VALIDER FINANCES"):
                    try:
                        df_t = conn.read(worksheet="Tresorerie", ttl=0)
                        nl = pd.DataFrame([{"Date": get_now(), "Type": m_t, "Etat": m_e, "Catégorie": m_c, "Montant": float(m_v), "Note": f"Admin: {st.session_state['user_pseudo']}"}])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_t, nl], ignore_index=True))
                        st.success("Opération financière enregistrée."); time.sleep(1); st.rerun()
                    except Exception as e: st.error(e)

        df_v = conn.read(worksheet="Tresorerie", ttl=0)
        if not df_v.empty:
            def calc(df, et):
                sub = df[df['Etat'] == et]
                return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
            sp, ss = calc(df_v, 'Propre'), calc(df_v, 'Sale')
            c1, c2, c3 = st.columns(3)
            # Métriques avec format Cartel (labels gris, valeurs or)
            c1.metric("TRÉSOR PROPRE", f"{int(sp):,} $".replace(',', ' '))
            c2.metric("TRÉSOR SALE", f"{int(ss):,} $".replace(',', ' '))
            c3.metric("TOTAL GLOBAL", f"{int(sp+ss):,} $".replace(',', ' '))
            st.write("### Derniers Mouvements de Fonds")
            st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)
