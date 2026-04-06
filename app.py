import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
RANKS_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue"]
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

# --- 2. STYLE CSS ---
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
    .rank-card {{ background: rgba(255, 255, 255, 0.05); border-left: 5px solid #555; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
    .rank-header {{ color: #888; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px; }}
    #bgVideo {{ position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; z-index: -1000; filter: brightness(0.3); object-fit: cover; }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #444 !important; border-radius: 10px; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: white !important; font-family: 'Courier New', monospace; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.9) !important; }}
    </style>
    <video autoplay loop muted playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_members_df():
    df = conn.read(worksheet="Membres", ttl=0)
    # Nettoyage critique pour éviter le bug "0.0" au login
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df

if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def reset_form():
    st.session_state.form_key += 1

# --- 4. AUTHENTIFICATION ---
df_members = get_members_df()

def check_login():
    u = str(st.session_state.get("user_login", "")).strip()
    p = str(st.session_state.get("password_login", "")).strip()
    user_match = df_members[(df_members['Login'] == u) & (df_members['Password'] == p)]
    if not user_match.empty:
        st.session_state['connected'] = True
        st.session_state['user_login_id'] = u
        st.session_state['user_pseudo'] = user_match.iloc[0]['Pseudo']
        st.session_state['user_role'] = user_match.iloc[0]['Role']
    else:
        st.error("Accès refusé.")

# --- 5. INTERFACE ---
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
        st.write(f"**Rang :** {st.session_state['user_role']}")
        menu = ["Tableau de bord", "Hiérarchie Clan"]
        if st.session_state['user_role'] == "Admin": 
            menu.extend(["Gestion des Membres", "Comptabilité Globale"])
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- FONCTION DE SAUVEGARDE UNIFIÉE ---
    def save_data(action, butin=0, drogue="N/A", qty=0, note=""):
        try:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Rapports
            df_r = conn.read(worksheet="Rapports", ttl=0)
            new_r = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(qty), "Butin": float(butin)}])
            conn.update(worksheet="Rapports", data=pd.concat([df_r, new_r], ignore_index=True))
            # Trésorerie (si butin > 0)
            if butin != 0:
                df_t = conn.read(worksheet="Tresorerie", ttl=0)
                new_t = pd.DataFrame([{"Date": ts, "Type": "Recette" if butin > 0 else "Dépense", "Etat": "Sale", "Catégorie": action, "Montant": abs(float(butin)), "Note": note or f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_t], ignore_index=True))
            st.success("Données transmises.")
            time.sleep(1); reset_form(); st.rerun()
        except Exception as e: st.error(f"Erreur : {e}")

    # --- PAGES ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])
        
        with tabs[0]: # ATM
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): save_data("ATM", butin=b)
        
        with tabs[4]: # Drogue
            with st.form(key=f"drg_{st.session_state.form_key}"):
                d = st.selectbox("🌿 Produit", DRUG_LIST)
                q = st.number_input("📦 Quantité vendue", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): save_data("Drogue", butin=b, drogue=d, qty=-abs(q))

    elif choice == "Hiérarchie Clan":
        st.markdown('<div class="gta-title">Organigrama</div>', unsafe_allow_html=True)
        for r in RANKS_LIST:
            names = df_members[df_members['Role'] == r]['Pseudo'].tolist()
            if names:
                st.markdown(f'<div class="rank-card"><div class="rank-header">{r}</div><div style="font-size:20px;">{" • ".join(names)}</div></div>', unsafe_allow_html=True)

    elif choice == "Gestion des Membres":
        st.markdown('<div class="gta-title">Admin</div>', unsafe_allow_html=True)
        to_edit = df_members[df_members['Role'] != 'Admin'].copy()
        for _, row in to_edit.iterrows():
            with st.expander(f"👤 {row['Pseudo']} ({row['Role']})"):
                with st.form(key=f"ed_{row['Login']}"):
                    nr = st.selectbox("Rang", RANKS_LIST, index=RANKS_LIST.index(row['Role']) if row['Role'] in RANKS_LIST else 0)
                    if st.form_submit_button("Changer le rang"):
                        df_members.loc[df_members['Login'] == row['Login'], 'Role'] = nr
                        conn.update(worksheet="Membres", data=df_members)
                        st.success("Rang mis à jour."); time.sleep(1); st.rerun()

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        sub = st.tabs(["📊 Vue d'ensemble", "🧼 Blanchiment", "📦 Stocks"])
        
        with sub[1]: # Blanchiment
            with st.form(key=f"wash_{st.session_state.form_key}"):
                amt = st.number_input("Montant Sale ($)", min_value=0)
                taux = st.slider("Taux (%)", 0, 100, 20)
                if st.form_submit_button("Blanchir"):
                    clean = amt * (1 - taux/100)
                    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    df_t = conn.read(worksheet="Tresorerie", ttl=0)
                    op1 = {"Date": ts, "Type": "Dépense", "Etat": "Sale", "Catégorie": "Blanchiment", "Montant": float(amt), "Note": f"Lavage {taux}%"}
                    op2 = {"Date": ts, "Type": "Recette", "Etat": "Propre", "Catégorie": "Blanchiment", "Montant": float(clean), "Note": "Retour Lavage"}
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_t, pd.DataFrame([op1, op2])], ignore_index=True))
                    st.success("Blanchiment enregistré."); time.sleep(1); reset_form(); st.rerun()

        with sub[2]: # Stocks
            with st.form(key=f"stk_{st.session_state.form_key}"):
                col1, col2 = st.columns(2)
                dn = col1.selectbox("Produit", DRUG_LIST)
                dq = col2.number_input("Quantité reçue", min_value=0.0)
                if st.form_submit_button("Aj
