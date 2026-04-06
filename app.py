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
    return conn.read(worksheet="Membres", ttl=0)

if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def reset_form():
    st.session_state.form_key += 1

# --- 4. AUTHENTIFICATION ---
df_members = get_members_df()

def check_login():
    u = st.session_state.get("user_login")
    p = st.session_state.get("password_login")
    # On compare en texte brut pour éviter les soucis de format
    user_match = df_members[(df_members['Login'].astype(str) == str(u)) & (df_members['Password'].astype(str) == str(p))]
    if not user_match.empty:
        st.session_state['connected'] = True
        st.session_state['user_login_id'] = str(u)
        st.session_state['user_pseudo'] = user_match.iloc[0]['Pseudo']
        st.session_state['user_role'] = user_match.iloc[0]['Role']

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
                else: st.error("Accès refusé.")
else:
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        # Récupération du rang en direct
        try:
            current_r = df_members[df_members['Login'].astype(str) == st.session_state['user_login_id']]['Role'].values[0]
            st.write(f"**Rang :** {current_r}")
        except:
            st.write(f"**Rang :** {st.session_state['user_role']}")
        
        menu = ["Tableau de bord", "Hiérarchie Clan"]
        if st.session_state['user_role'] == "Admin": 
            menu.append("Gestion des Membres")
            menu.append("Comptabilité Globale")
            
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- GESTION DES MEMBRES (ADMIN) ---
    if choice == "Gestion des Membres":
        st.markdown('<div class="gta-title">Admin</div>', unsafe_allow_html=True)
        st.write("### 🎖️ Modifier les Rangs")
        
        to_edit = df_members[df_members['Role'] != 'Admin'].copy()
        
        for idx, row in to_edit.iterrows():
            with st.expander(f"👤 {row['Pseudo']} (Actuel: {row['Role']})"):
                with st.form(key=f"f_edit_{row['Login']}"):
                    new_rank = st.selectbox("Nouveau Rang", RANKS_LIST, 
                                          index=RANKS_LIST.index(row['Role']) if row['Role'] in RANKS_LIST else 0)
                    if st.form_submit_button("VALIDER LE CHANGEMENT"):
                        df_members.loc[df_members['Login'] == row['Login'], 'Role'] = new_rank
                        conn.update(worksheet="Membres", data=df_members)
                        st.success("Rang mis à jour dans le Sheets !")
                        time.sleep(1)
                        st.rerun()

    # --- HIÉRARCHIE ---
    elif choice == "Hiérarchie Clan":
        st.markdown('<div class="gta-title">Organigrama</div>', unsafe_allow_html=True)
        for r in RANKS_LIST:
            names = df_members[df_members['Role'] == r]['Pseudo'].tolist()
            if names:
                st.markdown(f'<div class="rank-card"><div class="rank-header">{r}</div><div style="color:white; font-size:20px;">{" • ".join(names)}</div></div>', unsafe_allow_html=True)

    # --- TABLEAU DE BORD ---
    elif choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        LOGO_URL = "https://raw.githubusercontent.com/lanieblagris/Compta-La-Niebla/main/logo.png?v=4"
        st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" style="width:100%; max-height:200px; object-fit:cover; border-radius:10px; margin-bottom:20px;"></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                new_rep = pd.DataFrame([{"Date": ts, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_tres = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                
                df_r = conn.read(worksheet="Rapports", ttl=0)
                df_t = conn.read(worksheet="Tresorerie", ttl=0)
                
                conn.update(worksheet="Rapports", data=pd.concat([df_r, new_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_tres], ignore_index=True))
                
                st.success("Transmis avec succès.")
                time.sleep(1); reset_form(); st.rerun()
            except Exception as e: st.error(f"Erreur Sheets : {e}")

        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("💵 Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[4]:
            with st.form(key=f"drg_{st.session_state.form_key}"):
                d = st.selectbox("🌿 Produit", DRUG_LIST)
                q = st.number_input("📦 Quantité", min_value=0.0)
                b = st.number_input("💵 Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d, quantite=-abs(q))

    # --- COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        sub = st.tabs(["📊 Vue d'ensemble", "🧼 Blanchiment", "📦 Gestion des Stocks"])
        
        with sub[0]: # Vue d'ensemble
            with st.form(key=f"man_{st.session_state.form_key}"):
                c1, c2, c3, c4 = st.columns(4)
                t_type = c1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = c2.selectbox("Argent", ["Sale", "Propre"])
                t_cat = c3.text_input("Catégorie")
                t_mon = c4.number_input("Montant ($)", min_value=0)
                t_not = st.text_area("Note")
                if st.form_submit_button("Valider"):
                    new_op = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": t_type, "Etat": t_etat, "Catégorie": t_cat, "Montant": float(t_mon), "Note": t_not}])
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.success("Enregistré."); time.sleep(1); reset_form(); st.rerun()

        with sub[2]: # Gestion des Stocks (Correction ici)
            with st.form(key=f"stk_{st.session_state.form_key}"):
                st.write("#### 📦 Ajouter du Stock")
                col1, col2 = st.columns(2)
                d_name = col1.selectbox("Produit", DRUG_LIST)
                d_qty = col2.number_input("Quantité reçue", min_value=0.0)
                if st.form_submit_button("VALIDER L'ARRIVAGE"):
                    new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Drogue", "Drogue": d_name, "Quantite": float(d_qty), "Butin": 0}])
                    df_all = conn.read(worksheet="Rapports", ttl=0)
                    conn.update(worksheet="Rapports", data=pd.concat([df_all, new_s], ignore_index=True))
                    st.success("Stock mis à jour !"); time.sleep(1); reset_form(); st.rerun()

        # Recap financier
        try:
            df_v = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_v.empty:
                st.markdown("---")
                def calc(df, et):
                    sub_df = df[df['Etat'] == et]
                    return sub_df[sub_df['Type'] == 'Recette']['Montant'].sum() - sub_df[sub_df['Type'] == 'Dépense']['Montant'].sum()
                s_s, s_p = calc(df_v, 'Sale'), calc(df_v, 'Propre')
                m1, m2, m3 = st.columns(3)
                m1.metric("PROPRE", f"{s_p:,.0f} $")
                m2.metric("SALE", f"{s_s:,.0f} $")
                m3.metric("TOTAL", f"{(s_p+s_s):,.0f} $")
                st.dataframe(df_v.sort_index(ascending=False).head(15), use_container_width=True)
        except: pass
