import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - Safe House", page_icon="🥷", layout="wide")

# --- 2. LIEN DE LA VIDÉO ---
VIDEO_URL = "https://assets.mixkit.co/videos/preview/mixkit-mysterious-pale-fog-moving-slowly-over-the-ground-44130-large.mp4"

# --- 3. STYLE CSS "LOS SANTOS" ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{ background: transparent !important; }}
    body {{ background-color: #000000; }}
    .gta-title {{
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 5px 5px 15px #000, 0 0 25px #555;
        margin-top: -60px; margin-bottom: 10px; letter-spacing: 3px;
    }}
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

# --- 4. BASE DE DONNÉES ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "Le Patron"},
    "Alex": {"password": "1234", "pseudo": "Alex Smith"},
    "Dany": {"password": "081219", "pseudo": "Dany Smith"},
}

if 'connected' not in st.session_state: st.session_state['connected'] = False

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    if u in USERS and USERS[u]["password"] == p:
        st.session_state['connected'] = True
        st.session_state['user_role'] = u
        st.session_state['user_pseudo'] = USERS[u]["pseudo"]

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 5. LOGIQUE D'AFFICHAGE ---
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
        if st.session_state['user_role'] == "Admin": menu.append("Comptabilité Globale")
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state['connected'] = False
            st.rerun()

    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title" style="font-size:60px;">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                # Tout butin entrant par les membres est marqué comme "Argent Sale"
                new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin), "Type_Argent": "Sale"}])
                df = conn.read(worksheet="Rapports", ttl=0)
                conn.update(worksheet="Rapports", data=pd.concat([df, new_row], ignore_index=True))
                
                # Mise à jour automatique de la trésorerie sale
                df_c = conn.read(worksheet="Tresorerie", ttl=0)
                new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": "Recette", "Catégorie": f"Action: {action}", "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}", "Etat": "Sale"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                
                st.snow()
                st.rerun() 
            except: st.error("Erreur de synchronisation.")

        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("💵 Butin ($) - ARGENT SALE", min_value=0, key="b1")
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[4]:
            with st.form("dr"):
                d = st.text_input("🌿 Produit")
                q = st.number_input("📦 Quantité", min_value=0)
                b = st.number_input("💵 Vente ($) - ARGENT SALE", min_value=0)
                if st.form_submit_button("VALIDER DROGUE"): handle_submit("Drogue", butin=b, drogue=d, quantite=q)

        # STATS HEBDO (Inchangé)
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
        except: pass

    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title" style="font-size:50px;">Tresorerie</div>', unsafe_allow_html=True)
        
        # FORMULAIRE ADMIN AVEC OPTION SALE/PROPRE
        with st.form("compta_form"):
            st.write("#### Gestion des Fonds")
            c1, c2, c3, c4 = st.columns(4)
            t_type = c1.selectbox("Type", ["Recette", "Dépense", "Blanchiment"])
            t_etat = c2.selectbox("Source/Cible", ["Sale", "Propre"])
            t_montant = c3.number_input("Montant ($)", min_value=0)
            t_cat = c4.text_input("Catégorie")
            t_note = st.text_area("Note (Ex: Blanchi 100k avec 20% de taxe)")
            
            if st.form_submit_button("Enregistrer l'opération"):
                try:
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    # Si blanchiment : on retire du sale et on ajoute au propre (fait manuellement ici)
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Catégorie": t_cat, "Montant": float(t_montant), "Note": t_note, "Etat": t_etat}])
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.success("Transaction enregistrée.")
                    st.rerun()
                except: st.error("Erreur GSheets.")

        st.markdown("---")
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                # CALCUL DES DEUX COFFRES
                sale_rec = df_all[(df_all['Type']=="Recette") & (df_all['Etat']=="Sale")]['Montant'].sum()
                sale_dep = df_all[(df_all['Type']=="Dépense") & (df_all['Etat']=="Sale")]['Montant'].sum()
                
                propre_rec = df_all[(df_all['Type']=="Recette") & (df_all['Etat']=="Propre")]['Montant'].sum()
                propre_dep = df_all[(df_all['Type']=="Dépense") & (df_all['Etat']=="Propre")]['Montant'].sum()

                m1, m2 = st.columns(2)
                m1.metric("🔴 COFFRE SALE (À Blanchir)", f"{sale_rec - sale_dep:,.0f} $")
                m2.metric("🟢 COFFRE PROPRE (Légal)", f"{propre_rec - propre_dep:,.0f} $")
                
                st.write("#### Historique des Flux")
                st.dataframe(df_all.sort_values(by="Date", ascending=False), use_container_width=True)
        except: st.warning("Ajoutez une colonne 'Etat' dans votre onglet 'Tresorerie' sur Google Sheets.")
