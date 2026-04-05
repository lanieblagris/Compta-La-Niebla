import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

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

# --- 3. CONNEXION ET CACHE ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def load_data(sheet):
    return conn.read(worksheet=sheet)

# --- 4. UTILISATEURS ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Emilio": {"password": "azertyuiop123", "pseudo": "Emilio Montoya"},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith"},
    "Junior": {"password": "Loup1304", "pseudo": "Madra Junior"},
}

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]

# --- 5. LOGIQUE ---
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
        menu = ["Tableau de bord"]
        if st.session_state['user_role'] == "Admin": 
            menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

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
                st.success("Archives mises à jour.")
                time.sleep(1); st.rerun()
            else: st.error("Erreur de connexion.")

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
                if d_select == "Autre": d_final = st.text_input("Nom spécifique")
                q = st.number_input("📦 Quantité", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): 
                    if d_select == "Autre" and not d_final: st.error("Précisez le produit.")
                    else: handle_submit("Drogue", butin=b, drogue=d_final, quantite=-abs(q))

        # --- STATS ---
        st.markdown("---")
        st.write("### 📊 STATISTIQUES DE LA SEMAINE")
        try:
            data = load_data("Rapports")
            if not data.empty:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                start_week = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0)
                week_data = data[data['Date'] >= start_week].copy()
                for p in [u["pseudo"] for u in USERS.values()]:
                    p_data = week_data[week_data['Membre'] == p]
                    nb_a = len(p_data[p_data['Action'] != "Drogue"])
                    nb_d = abs(p_data[p_data['Action'] == "Drogue"]['Quantite'].sum())
                    c1, c2, c3 = st.columns([1, 2, 2])
                    c1.write(f"**{p}**")
                    c2.progress(min(nb_a/20, 1.0), text=f"Actions: {nb_a}")
                    c3.progress(min(nb_d/300, 1.0), text=f"Ventes: {int(nb_d)}")
        except: pass

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        sub_tabs = st.tabs(["📊 Vue d'ensemble", "🧼 Blanchiment", "📦 Gestion des Stocks"])
        
        with sub_tabs[0]: # VUE ENSEMBLE
            with st.form("compta_form"):
                st.write("#### Opération Manuelle")
                col1, col2, col3, col4 = st.columns(4)
                t_type = col1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = col2.selectbox("Argent", ["Sale", "Propre"])
                t_cat = col3.text_input("Catégorie")
                t_montant = col4.number_input("Montant ($)", min_value=0)
                t_note = st.text_area("Note")
                if st.form_submit_button("Valider"):
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note}])
                    try:
                        df_c = conn.read(worksheet="Tresorerie", ttl=0)
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                        st.cache_data.clear(); st.success("Validé."); time.sleep(1); st.rerun()
                    except: st.error("Erreur Sheets")

        with sub_tabs[2]: # STOCKS
            st.write("#### 📦 État des Stocks")
            with st.form("add_stock"):
                st.write("➕ AJOUTER UN ARRIVAGE")
                cs1, cs2 = st.columns(2) # Correction ici (pas de variable 'c')
                d_n_sel = cs1.selectbox("Produit", ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"])
                d_n_fin = d_n_sel
                if d_n_sel == "Autre": d_n_fin = st.text_input("Nom spécifique")
                d_qty = cs2.number_input("Quantité", min_value=0.0)
                if st.form_submit_button("VALIDER L'ARRIVAGE"):
                    new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Drogue", "Drogue": d_n_fin, "Quantite": float(d_qty), "Butin": 0}])
                    try:
                        df_all_r = conn.read(worksheet="Rapports", ttl=0)
                        conn.update(worksheet="Rapports", data=pd.concat([df_all_r, new_s], ignore_index=True))
                        st.cache_data.clear(); st.success("Stock mis à jour !"); time.sleep(1); st.rerun()
                    except: st.error("Erreur Sheets")

            st.write("---")
            try:
                df_rep_s = load_data("Rapports")
                if not df_rep_s.empty:
                    df_drugs = df_rep_s[df_rep_s['Action'] == "Drogue"].copy()
                    stock_f = df_drugs.groupby('Drogue')['Quantite'].sum().reset_index()
                    cols_s = st.columns(4)
                    for i, row in stock_f.iterrows():
                        cols_s[i % 4].metric(row['Drogue'], f"{row['Quantite']:.1f} u")
            except: pass
