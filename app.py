import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="La Niebla - Luxury Cartel", page_icon="⚜️", layout="wide")

# --- 2. UTILISATEURS (Vérifie bien tes role_levels ici) ---
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron", "role_level": 1},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith", "role_level": 1},
    "Dany": {"password": "081219", "pseudo": "Dany Smith", "role_level": 1},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith", "role_level": 1},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin", "role_level": 1},
}

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]

# --- 3. STYLE CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Marcellus&display=swap');
    .stApp {{ background: url('https://w0.peakpx.com/wallpaper/70/463/wallpaper-dark-grey-textured-dark-grey-background-textured-background.jpg'); background-size: cover; background-attachment: fixed; }}
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ color: #f7e0a3 !important; font-family: 'Marcellus', serif !important; }}
    .gta-title {{ font-family: 'UnifrakturMaguntia', cursive; font-size: 90px; color: transparent; background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e, #f7e0a3); -webkit-background-clip: text; background-clip: text; text-align: center; margin-top: -50px; }}
    .stForm {{ background-color: rgba(10, 10, 10, 0.85) !important; border: 1px solid #b48c3e !important; border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: rgba(15, 15, 15, 0.98) !important; border-right: 1px solid #b48c3e; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

if 'connected' not in st.session_state: st.session_state['connected'] = False

# --- 5. LOGIN ---
if not st.session_state['connected']:
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login"):
            u = st.text_input("NOM DE CODE")
            p = st.text_input("MOT DE PASSE", type="password")
            if st.form_submit_button("S'INFILTRER"):
                if u in USERS and USERS[u]["password"] == p:
                    st.session_state.update({"connected": True, "user_id": u, "user_pseudo": USERS[u]["pseudo"], "role_level": USERS[u]["role_level"]})
                    st.rerun()
                else: st.error("Accès refusé.")
else:
    u_pseudo = st.session_state['user_pseudo']
    u_role_lv = st.session_state['role_level']

    with st.sidebar:
        icon = "⚜️" if u_role_lv == 1 else "⭐" if u_role_lv == 2 else "🔫"
        st.write(f"### {u_pseudo} {icon}")
        menu = ["Tableau de bord"]
        if u_role_lv <= 2: menu += ["Comptabilité Globale", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"): st.session_state.clear(); st.rerun()

    df_full = conn.read(worksheet="Rapports", ttl=0)

    # --- ONGLET TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])
        
        def submit_op(action, butin=0, drogue="N/A", qte=0):
            ts = get_now()
            df_r = conn.read(worksheet="Rapports", ttl=0)
            new_r = pd.DataFrame([{"Date": ts, "Membre": u_pseudo, "Action": action, "Drogue": drogue, "Quantite": float(qte), "Butin": float(butin)}])
            conn.update(worksheet="Rapports", data=pd.concat([df_r, new_r], ignore_index=True))
            df_t = conn.read(worksheet="Tresorerie", ttl=0)
            new_t = pd.DataFrame([{"Date": ts, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Par {u_pseudo}"}])
            conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_t], ignore_index=True))
            st.success("Transmis !"); time.sleep(1); st.rerun()

        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("ATM", butin=b)
        # ... (Autres onglets simplifiés ici pour le code complet)
        with tabs[4]:
            with st.form("drug"):
                d = st.selectbox("Produit", DRUG_LIST); q = st.number_input("Unités", min_value=0.0); b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): submit_op("Drogue", butin=b, drogue=d, qte=-abs(q))

        st.write("### 📊 Objectifs de la Semaine")
        # Logique d'affichage des barres de progression... (Identique à avant)
        # [Insérer ici ta logique d'affichage des objectifs du code précédent]

    # --- ONGLET COMPTABILITÉ (AVEC MODIFS MANUELLES) ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Trésorerie</div>', unsafe_allow_html=True)
        df_v = conn.read(worksheet="Tresorerie", ttl=0)
        
        if not df_v.empty:
            def c_v(df, e): return df[df['Etat']==e][df['Type']=='Recette']['Montant'].sum() - df[df['Etat']==e][df['Type']=='Dépense']['Montant'].sum()
            p, s = c_v(df_v, 'Propre'), c_v(df_v, 'Sale')
            c1, c2, c3 = st.columns(3)
            c1.metric("PROPRE ⚜️", f"{int(p):,} $")
            c2.metric("SALE 💵", f"{int(s):,} $")
            c3.metric("TOTAL", f"{int(p+s):,} $")

        st.write("---")
        
        # --- ICI LES FORMULAIRES DE MODIFICATION (SEULEMENT POUR NIVEAU 1) ---
        if u_role_lv == 1:
            col_admin1, col_admin2 = st.columns(2)
            
            with col_admin1:
                with st.expander("🛠️ AJOUTER ACTIONS/VENTES (Objectifs)"):
                    with st.form("adj_obj"):
                        target = st.selectbox("Membre", [u["pseudo"] for u in USERS.values()])
                        type_adj = st.radio("Type", ["Actions", "Ventes"])
                        valeur = st.number_input("Valeur à ajouter", min_value=1)
                        if st.form_submit_button("APPLIQUER AJUSTEMENT"):
                            name = "Ajustement Action" if type_adj == "Actions" else "Ajustement Ventes"
                            q_save = float(valeur) if type_adj == "Actions" else -float(valeur)
                            df_r = conn.read(worksheet="Rapports", ttl=0)
                            new_l = pd.DataFrame([{"Date": get_now(), "Membre": target, "Action": name, "Drogue": "N/A", "Quantite": q_save, "Butin": 0}])
                            conn.update(worksheet="Rapports", data=pd.concat([df_r, new_l], ignore_index=True))
                            st.success("Objectif mis à jour !"); time.sleep(1); st.rerun()

            with col_admin2:
                with st.expander("💰 AJOUTER/RETIRER ARGENT (Coffre)"):
                    with st.form("adj_fin"):
                        t_m = st.selectbox("Type", ["Recette", "Dépense"])
                        e_m = st.selectbox("État", ["Sale", "Propre"])
                        v_m = st.number_input("Montant ($)", min_value=0)
                        cat = st.text_input("Raison / Catégorie")
                        if st.form_submit_button("MODIFIER TRÉSORERIE"):
                            df_t = conn.read(worksheet="Tresorerie", ttl=0)
                            new_t = pd.DataFrame([{"Date": get_now(), "Type": t_m, "Etat": e_m, "Catégorie": cat, "Montant": float(v_m), "Note": f"Admin: {u_pseudo}"}])
                            conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_t], ignore_index=True))
                            st.success("Finances mises à jour !"); time.sleep(1); st.rerun()

        st.write("### Historique des flux")
        st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)

    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)
