import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

# --- 2. LIEN DE LA VIDÉO (FONCTIONNEL) ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

# --- 3. STYLE CSS "LOS SANTOS" & TITRE ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');

    /* Transparence des éléments Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
        background: transparent !important;
    }}

    body {{
        background-color: #000000;
    }}

    /* TITRE STYLE GTA LOS SANTOS */
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive;
        font-size: 85px;
        color: white;
        text-align: center;
        text-shadow: 5px 5px 15px #000, 0 0 25px #555;
        margin-top: -60px;
        margin-bottom: 10px;
        letter-spacing: 3px;
    }}

    /* CONFIGURATION VIDÉO FOND */
    #bgVideo {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -1000;
        filter: brightness(0.3);
        object-fit: cover;
    }}

    /* STYLE DES ÉLÉMENTS UI */
    .stForm {{ 
        background-color: rgba(10, 10, 10, 0.85) !important; 
        border: 1px solid #444 !important;
        border-radius: 10px;
    }}
    
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ 
        color: white !important; 
        font-family: 'Courier New', monospace;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.9) !important;
    }}

    /* Fix visibilité metrics */
    [data-testid="stMetricValue"] {{ color: white !important; }}
    [data-testid="stMetricLabel"] {{ color: #bbb !important; }}
    </style>

    <video autoplay loop muted playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 4. BASE DE DONNÉES DES MEMBRES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
    "Emilio": {"password": "azertyuiop123", "pseudo": "Emilio Montoya"},
}

# --- 5. INITIALISATION DE LA SESSION ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]
    else:
        st.error("Accès refusé.")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 6. LOGIQUE D'AFFICHAGE ---
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
            menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    # --- PAGE 1 : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title" style="font-size:60px;">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                # 1. Mise à jour Rapports
                new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                df = conn.read(worksheet="Rapports", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df, new_row], ignore_index=True))
                
                # 2. Mise à jour Trésorerie (Automatiquement en Sale)
                df_c = conn.read(worksheet="Tresorerie", ttl=0)
                new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                
                st.success("Transmis avec succès.")
                time.sleep(1) # Pause pour stabiliser GSheets
                st.rerun() 
            except Exception as e: 
                st.error(f"Erreur de connexion : {e}")

        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b1")
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form("sup"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b2")
                if st.form_submit_button("VALIDER SUPERETTE"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form("gf"):
                b = st.number_input("💵 Butin ($)", min_value=0, key="b3")
                if st.form_submit_button("VALIDER GO FAST"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form("cam"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form("dr"):
                d = st.text_input("🌿 Produit")
                q = st.number_input("📦 Quantité", min_value=0)
                b = st.number_input("💵 Vente ($)", min_value=0)
                if st.form_submit_button("VALIDER DROGUE"): handle_submit("Drogue", butin=b, drogue=d, quantite=q)

        # STATS HEBDO
        st.markdown("---")
        st.write("### 📊 STATISTIQUES HEBDOMADAIRES")
        try:
            data = conn.read(worksheet="Rapports", ttl=0)
            if data is not None and not data.empty:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                start_week = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0)
                week_data = data[data['Date'] >= start_week].copy()
                if not week_data.empty:
                    s_act = week_data[week_data['Action'] != "Drogue"].groupby('Membre').agg({'Action': 'count', 'Butin': 'sum'}).reset_index()
                    s_dro = week_data[week_data['Action'] == "Drogue"].groupby('Membre').agg({'Quantite': 'sum', 'Butin': 'sum'}).reset_index()
                    stats = pd.merge(s_act, s_dro, on='Membre', how='outer').fillna(0)
                    
                    for _, row in stats.iterrows():
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{row['Membre']}**")
                        c2.progress(min(int(row['Action'])/20, 1.0), text=f"Actions: {int(row['Action'])}")
                        c3.progress(min(int(row['Quantite'])/300, 1.0), text=f"Drogue: {int(row['Quantite'])}")
                    
                    st.write("#### 💸 RÉCAPITULATIF FINANCIER")
                    df_recap = stats[['Membre', 'Butin_x', 'Butin_y']].copy()
                    df_recap.columns = ['Membre', 'Actions ($)', 'Drogue ($)']
                    df_recap['Actions ($)'] = df_recap['Actions ($)'].apply(lambda x: f"{int(x):,.0f} $".replace(',', ' '))
                    df_recap['Drogue ($)'] = df_recap['Drogue ($)'].apply(lambda x: f"{int(x):,.0f} $".replace(',', ' '))
                    st.table(df_recap)
        except: pass

    # --- PAGE 2 : COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title" style="font-size:50px;">Tresorerie</div>', unsafe_allow_html=True)
        
        with st.form("compta_form"):
            st.write("#### Enregistrer une Opération")
            c1, c2, c3, c4 = st.columns(4)
            t_type = c1.selectbox("Type", ["Recette", "Dépense"])
            t_etat = c2.selectbox("Argent", ["Sale", "Propre"])
            t_cat = c3.text_input("Catégorie (Loyer, Armes, Véhicules...)")
            t_montant = c4.number_input("Montant ($)", min_value=0)
            t_note = st.text_area("Note / Justification")
            if st.form_submit_button("Enregistrer l'opération"):
                try:
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note}])
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.success("Opération validée.")
                    time.sleep(1)
                    st.rerun()
                except: st.error("Erreur d'accès à l'onglet 'Tresorerie'.")

        st.markdown("---")
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                # Calculs Propre
                rec_p = df_all[(df_all['Type']=="Recette") & (df_all['Etat']=="Propre")]['Montant'].sum()
                dep_p = df_all[(df_all['Type']=="Dépense") & (df_all['Etat']=="Propre")]['Montant'].sum()
                # Calculs Sale
                rec_s = df_all[(df_all['Type']=="Recette") & (df_all['Etat']=="Sale")]['Montant'].sum()
                dep_s = df_all[(df_all['Type']=="Dépense") & (df_all['Etat']=="Sale")]['Montant'].sum()

                m1, m2, m3 = st.columns(3)
                m1.metric("SOLDE PROPRE", f"{rec_p - dep_p:,.0f} $")
                m2.metric("SOLDE SALE", f"{rec_s - dep_s:,.0f} $")
                m3.metric("TOTAL GLOBAL", f"{(rec_p + rec_s) - (dep_p + dep_s):,.0f} $")
                
                st.dataframe(df_all.sort_values(by="Date", ascending=False), use_container_width=True)
        except: st.warning("Vérifiez l'onglet 'Tresorerie' (Colonnes: Date, Type, Etat, Catégorie, Montant, Note).")
