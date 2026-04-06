import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
RANKS_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue"]

# --- 2. STYLE CSS ---
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
    # Force la lecture en string pour éviter les erreurs de comparaison sur les logins/passwords
    df = conn.read(worksheet="Membres", ttl=0)
    return df.astype(str)

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

# --- 4. AUTHENTIFICATION ---
df_members = get_members_df()

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    
    # Recherche du membre
    user_match = df_members[(df_members['Login'] == str(u)) & (df_members['Password'] == str(p))]
    
    if not user_match.empty:
        st.session_state['connected'] = True
        st.session_state['user_login_id'] = str(u)
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
    # --- Barre latérale ---
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        st.write(f"**Rang :** {st.session_state['user_role']}")
        
        menu = ["Tableau de bord", "Hiérarchie Clan"]
        if st.session_state['user_role'] == "Admin": 
            menu.append("Gestion des Membres")
            menu.append("Comptabilité Globale")
            
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- LOGIQUE DE FORMULAIRE (Unique Key pour éviter Erreur de Synchronisation) ---
    # Cette partie résout l'erreur visible sur l'image_112d2b.jpg
    if "submit_id" not in st.session_state:
        st.session_state.submit_id = 0

    def refresh_app():
        st.session_state.submit_id += 1
        st.rerun()

    # --- TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px; margin-bottom:20px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_action(action, butin=0, drogue="N/A", qty=0):
            try:
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                # Mise à jour Rapports
                df_r = conn.read(worksheet="Rapports", ttl=0)
                new_rep = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(qty), "Butin": float(butin)}])
                conn.update(worksheet="Rapports", data=pd.concat([df_r, new_rep], ignore_index=True))
                
                # Mise à jour Trésorerie (Argent Sale par défaut)
                df_t = conn.read(worksheet="Tresorerie", ttl=0)
                new_tres = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_tres], ignore_index=True))
                
                st.success("Transmis avec succès.")
                time.sleep(1)
                refresh_app()
            except Exception as e:
                st.error(f"Erreur Sheets : {e}")

        with tabs[0]: # ATM
            with st.form(key=f"atm_{st.session_state.submit_id}"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"):
                    handle_action("ATM", butin=b)

        with tabs[4]: # Drogue
            with st.form(key=f"drg_{st.session_state.submit_id}"):
                d = st.selectbox("🌿 Produit", DRUG_LIST)
                q = st.number_input("📦 Quantité vendue", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"):
                    handle_action("Drogue", butin=b, drogue=d, qty=-abs(q))

    # --- COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        sub_tabs = st.tabs(["📊 Vue d'ensemble", "🧼 Blanchiment", "📦 Gestion des Stocks"])
        
        with sub_tabs[0]: # Manuel
            with st.form(key=f"treso_{st.session_state.submit_id}"):
                col1, col2, col3, col4 = st.columns(4)
                t_type = col1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = col2.selectbox("Argent", ["Sale", "Propre"])
                t_cat = col3.text_input("Catégorie")
                t_mon = col4.number_input("Montant ($)", min_value=0)
                t_not = st.text_area("Note")
                if st.form_submit_button("Valider l'opération"):
                    df_t = conn.read(worksheet="Tresorerie", ttl=0)
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_mon), "Note": t_not}])
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_op], ignore_index=True))
                    st.success("Opération enregistrée.")
                    time.sleep(1)
                    refresh_app()

        with sub_tabs[2]: # Stocks (Résout SyntaxError et NameError image_b53467.png & image_1134af.png)
            with st.form(key=f"stock_{st.session_state.submit_id}"):
                st.write("#### 📦 Ajouter du Stock (Arrivage)")
                s_col1, s_col2 = st.columns(2)
                d_name = s_col1.selectbox("Produit", DRUG_LIST)
                d_qty = s_col2.number_input("Quantité reçue", min_value=0.0)
                if st.form_submit_button("ENREGISTRER L'ARRIVAGE"):
                    df_r = conn.read(worksheet="Rapports", ttl=0)
                    new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Arrivage Stock", "Drogue": d_name, "Quantite": float(d_qty), "Butin": 0}])
                    conn.update(worksheet="Rapports", data=pd.concat([df_r, new_s], ignore_index=True))
                    st.success("Stock mis à jour !")
                    time.sleep(1)
                    refresh_app()

        # Recapitulatif visuel
        try:
            df_v = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_v.empty:
                st.markdown("---")
                def sum_m(df, etat, t_type):
                    return df[(df['Etat'] == etat) & (df['Type'] == t_type)]['Montant'].astype(float).sum()
                
                solde_sale = sum_m(df_v, 'Sale', 'Recette') - sum_m(df_v, 'Sale', 'Dépense')
                solde_propre = sum_m(df_v, 'Propre', 'Recette') - sum_m(df_v, 'Propre', 'Dépense')
                
                c1, c2, c3 = st.columns(3)
                c1.metric("SOLDE PROPRE", f"{solde_propre:,.0f} $")
                c2.metric("SOLDE SALE", f"{solde_sale:,.0f} $")
                c3.metric("TOTAL GLOBAL", f"{(solde_propre + solde_sale):,.0f} $")
                st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)
        except:
            pass

    # --- HIERARCHIE ---
    elif choice == "Hiérarchie Clan":
        st.markdown('<div class="gta-title">Organigrama</div>', unsafe_allow_html=True)
        for r in RANKS_LIST:
            m_list = df_members[df_members['Role'] == r]['Pseudo'].tolist()
            if m_list:
                st.markdown(f'<div class="rank-card"><div class="rank-header">{r}</div><div style="font-size:22px;">{" • ".join(m_list)}</div></div>', unsafe_allow_html=True)

                # AJOUTE ÇA TEMPORAIREMENT POUR TESTER :
df_members = get_members_df()
st.write("DEBUG : Voici ce que l'IA lit dans le Sheets :")
st.dataframe(df_members)
