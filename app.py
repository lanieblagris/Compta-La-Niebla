import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION ET CONSTANTES ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

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
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    
    .stApp {{ background: transparent !important; }}
    body {{ background-color: #1a1a1a; color: #d4af37; }}

    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 100px; color: #d4af37;
        text-align: center; text-shadow: 4px 4px 10px #000, 0 0 25px #d4af37;
        margin-top: -60px; margin-bottom: 20px; letter-spacing: 5px;
    }}
    
    h1, h2, h3, h4 {{ color: #a6a6a6 !important; font-family: 'Courier New', monospace; font-weight: bold; }}
    p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: #d4af37 !important; font-family: 'Courier New', monospace; }}
    
    .stForm {{ 
        background-color: #262626 !important; 
        border: 2px solid #d4af37 !important; 
        border-radius: 10px; 
        padding: 20px; 
    }}
    
    [data-testid="stSidebar"] {{ background-color: #1a1a1a !important; border-right: 1px solid #d4af37; }}
    [data-testid="stSidebar"] * {{ color: #d4af37 !important; }}
    
    .stProgress > div > div > div > div {{ background-color: #d4af37 !important; }}
    
    .objectif-pseudo {{ font-size: 1.1em; color: #d4af37; font-weight: bold; }}
    .objectif-cash {{ font-size: 1.1em; color: #00ff00; font-weight: bold; font-family: 'Courier New', monospace;}}
    
    [data-testid="stMetricValue"] {{ color: #d4af37 !important; font-family: 'Courier New', monospace; font-size: 32px; }}
    
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
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin": 
            menu += ["Comptabilité Globale", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    df_full = conn.read(worksheet="Rapports", ttl=0)

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        
        # --- TABS DE SAISIE ---
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
                st.success("Transmis !"); time.sleep(1); st.session_state.form_key += 1; st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

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

        # --- OBJECTIFS DE LA SEMAINE ---
        st.write("### 📊 Objectifs de la Semaine & Bilan Financier")
        if not df_full.empty:
            df_stats = df_full.copy()
            df_stats['Date'] = pd.to_datetime(df_stats['Date'], dayfirst=True, errors='coerce')
            today = datetime.datetime.now()
            start_week = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            
            week_data = df_stats[
                (df_stats['Date'] >= start_week) & 
                (~df_stats['Action'].str.contains(r'\[LOG\]', na=False, case=False))
            ]
            
            st.markdown("""
                <div style="display: flex; font-weight: bold; color: #a6a6a6; padding: 10px 0; border-bottom: 2px solid #d4af37; margin-bottom: 10px;">
                    <div style="flex: 1.2;">MEMBRE</div>
                    <div style="flex: 1;">RÉCOLTÉ ($)</div>
                    <div style="flex: 2;">ACTIONS (20)</div>
                    <div style="flex: 2;">VENTES (300)</div>
                </div>
            """, unsafe_allow_html=True)

            for p_id, p_info in USERS.items():
                ps = p_info["pseudo"]
                u_data = week_data[week_data['Membre'] == ps]
                total_cash = u_data['Butin'].sum()
                normal_act = len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement", na=False))])
                adj_act = u_data[u_data['Action'] == "Ajustement Action"]["Quantite"].sum()
                total_act = int(normal_act + adj_act)
                total_vnt = abs(u_data[u_data['Action'].str.contains("Drogue|Ventes", case=False, na=False)]['Quantite'].sum())
                
                c1, c2, c3, c4 = st.columns([1.2, 1, 2, 2])
                c1.markdown(f'<div class="objectif-pseudo">{ps}</div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="objectif-cash">{int(total_cash):,} $</div>'.replace(',', ' '), unsafe_allow_html=True)
                c3.progress(min(float(total_act)/20, 1.0), text=f"{total_act}/20")
                c4.progress(min(float(total_vnt)/300, 1.0), text=f"{int(total_vnt)}/300")
                st.write("")
        
        st.markdown("---")

        # --- RESTAURATION : MES 3 DERNIÈRES ACTIVITÉS ---
        st.write("### 🕒 Mes 3 dernières activités")
        if not df_full.empty:
            mes_actions = df_full[
                (df_full['Membre'] == st.session_state['user_pseudo']) & 
                (~df_full['Action'].str.contains(r'\[LOG\]', na=False, case=False))
            ].tail(3).iloc[::-1].copy()
            if not mes_actions.empty:
                mes_actions['Butin'] = mes_actions['Butin'].apply(lambda x: f"{int(float(x)):,} $".replace(',', ' '))
                st.table(mes_actions[['Date', 'Action', 'Butin']])
            else: st.info("Aucune action récente.")

    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        # (Le code d'ajustement Admin reste ici)
        with st.expander("🛠️ CORRIGER/AJOUTER OBJECTIFS"):
            with st.form("adj_manual_bulk"):
                target_user = st.selectbox("Membre", [u["pseudo"] for u in USERS.values()])
                adj_type = st.radio("Type", ["Actions", "Ventes"])
                adj_val = st.number_input("Valeur", min_value=1, step=1)
                if st.form_submit_button("APPLIQUER"):
                    try:
                        ts = get_now()
                        name = "Ajustement Action" if "Actions" in adj_type else "Ajustement Ventes"
                        q_to_save = float(adj_val) if "Actions" in adj_type else -float(adj_val)
                        df_r = conn.read(worksheet="Rapports", ttl=0)
                        nl = pd.DataFrame([{"Date": ts, "Membre": target_user, "Action": name, "Drogue": "N/A", "Quantite": q_to_save, "Butin": 0}])
                        conn.update(worksheet="Rapports", data=pd.concat([df_r, nl], ignore_index=True))
                        st.success("Bilan mis à jour !"); time.sleep(1); st.rerun()
                    except Exception as e: st.error(e)
