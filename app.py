import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="La Niebla - Luxury Cartel", page_icon="⚜️", layout="wide")

# Définition des utilisateurs et rôles
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron", "role_level": 1, "is_drug_manager": True},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith", "role_level": 1, "is_drug_manager": False},
    "Dany": {"password": "081219", "pseudo": "Dany Smith", "role_level": 1, "is_drug_manager": True},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith", "role_level": 1, "is_drug_manager": False},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin", "role_level": 1, "is_drug_manager": False},
}

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

# --- 2. STYLE CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Marcellus&display=swap');
    .stApp {{ background: url('https://w0.peakpx.com/wallpaper/70/463/wallpaper-dark-grey-textured-dark-grey-background-textured-background.jpg'); background-size: cover; background-attachment: fixed; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: #f7e0a3 !important; font-family: 'Marcellus', serif !important; }}
    .gta-title {{ font-family: 'UnifrakturMaguntia', cursive; font-size: 90px; color: transparent; background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e, #f7e0a3); -webkit-background-clip: text; background-clip: text; text-align: center; margin-top: -50px; margin-bottom: 10px; }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #b48c3e !important; border-radius: 8px; padding: 20px; }}
    [data-testid="stSidebar"] {{ background-color: rgba(15, 15, 15, 0.98) !important; border-right: 1px solid #b48c3e; }}
    .stProgress > div > div > div > div {{ background-image: linear-gradient(to right, #b48c3e, #f7e0a3) !important; }}
    th {{ color: #b48c3e !important; }} td {{ color: #ffffff !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS CŒUR ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

# Initialisation de la session
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

# --- 4. LOGIQUE D'AUTHENTIFICATION ---
if not st.session_state['connected']:
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            u_in = st.text_input("NOM DE CODE")
            p_in = st.text_input("MOT DE PASSE", type="password")
            if st.form_submit_button("S'INFILTRER"):
                if u_in in USERS and USERS[u_in]["password"] == p_in:
                    u_info = USERS[u_in]
                    st.session_state.update({
                        "connected": True, 
                        "user_pseudo": u_info["pseudo"], 
                        "role_level": u_info["role_level"], 
                        "is_drug_manager": u_info["is_drug_manager"]
                    })
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

# --- 5. INTERFACE MEMBRE CONNECTÉ ---
else:
    # Sécurisation des variables de session
    u_pseudo = st.session_state.get('user_pseudo', "Inconnu")
    u_role_lv = st.session_state.get('role_level', 3)
    is_drug_boss = st.session_state.get('is_drug_manager', False)

    # Sidebar Navigation
    with st.sidebar:
        role_icon = "⚜️" if u_role_lv == 1 else "⭐" if u_role_lv == 2 else "🔫"
        st.write(f"### {u_pseudo} {role_icon}")
        if is_drug_boss: st.info("🌿 Responsable Drogue")
        st.write("---")
        
        menu = ["Tableau de bord"]
        if u_role_lv <= 2 or is_drug_boss: menu += ["📦 Gestion des Stocks"]
        if u_role_lv <= 2: menu += ["Comptabilité Globale", "Archives"]
        
        choice = st.radio("Navigation", menu)
        st.write("---")
        if st.button("Se déconnecter"):
            st.session_state.clear()
            st.rerun()

    # Chargement des données
    df_full = conn.read(worksheet="Rapports", ttl=0)

    # --- ONGLET TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])
        
        def submit_op(action, butin=0, drogue="N/A", qte=0):
            ts = get_now()
            # Enregistrement Rapport
            df_r = conn.read(worksheet="Rapports", ttl=0)
            new_r = pd.DataFrame([{"Date": ts, "Membre": u_pseudo, "Action": action, "Drogue": drogue, "Quantite": float(qte), "Butin": float(butin)}])
            conn.update(worksheet="Rapports", data=pd.concat([df_r, new_r], ignore_index=True))
            
            # MAJ Stock si vente de drogue
            if action == "Drogue" and drogue != "N/A":
                df_s = conn.read(worksheet="Stocks", ttl=0)
                if drogue in df_s['Produit'].values:
                    df_s.loc[df_s['Produit'] == drogue, 'Quantite'] += float(qte)
                    conn.update(worksheet="Stocks", data=df_s)
            
            st.success("Transmis !"); time.sleep(1); st.rerun()

        with tabs[4]: # Focus sur l'onglet Drogue pour l'exemple
            with st.form("drug_sale"):
                d = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Unités vendues", min_value=0.0)
                b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"):
                    submit_op("Drogue", butin=b, drogue=d, qte=-abs(q))

        # Affichage Objectifs (image_eee65d.png)
        st.write("### 📊 Objectifs de la Semaine")
        # ... [Logique d'affichage des barres de progression ici]

    # --- ONGLET STOCKS ---
    elif choice == "📦 Gestion des Stocks":
        st.markdown('<div class="gta-title">Inventaire</div>', unsafe_allow_html=True)
        df_stock = conn.read(worksheet="Stocks", ttl=0)
        
        # Initialisation auto si vide
        if df_stock.empty or 'Produit' not in df_stock.columns:
            df_stock = pd.DataFrame({"Produit": DRUG_LIST, "Quantite": [0.0]*len(DRUG_LIST)})
            conn.update(worksheet="Stocks", data=df_stock)

        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.table(df_stock)
        with c2:
            with st.form("stock_adj"):
                p_sel = st.selectbox("Produit à ajuster", DRUG_LIST)
                m_sel = st.radio("Action", ["Récolte (+)", "Saisie/Perte (-)"])
                q_sel = st.number_input("Quantité", min_value=0.0)
                if st.form_submit_button("APPLIQUER"):
                    val = q_sel if "Récolte" in m_sel else -q_sel
                    df_stock.loc[df_stock['Produit'] == p_sel, 'Quantite'] += val
                    conn.update(worksheet="Stocks", data=df_stock)
                    st.success("Stock mis à jour !"); time.sleep(1); st.rerun()
