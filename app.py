import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
ROLES_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue", "Infiltré"]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #000000; }
    .gta-title {
        font-family: 'UnifrakturMaguntia', cursive; font-size: 85px; color: white;
        text-align: center; text-shadow: 5px 5px 15px #000; margin-top: -60px; margin-bottom: 10px;
    }
    .stForm { background-color: rgba(10, 10, 10, 0.9) !important; border: 1px solid #444 !important; border-radius: 10px; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: white !important; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.9) !important; }
    [data-testid="stMetricValue"] { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def check_login():
    df_m = get_members()
    u_input = st.session_state.get("user_login")
    p_input = str(st.session_state.get("password_login"))
    
    if not df_m.empty:
        # --- BLOC DE DIAGNOSTIC ---
        st.write("### 🔍 Diagnostic Connexion")
        st.write(f"Tu as tapé Login: [{u_input}]")
        st.write(f"Tu as tapé MDP: [{p_input}]")
        
        # On prépare les données du Sheets pour la comparaison
        df_m['Login'] = df_m['Login'].astype(str).str.strip()
        df_m['Password'] = df_m['Password'].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        # On affiche ce que le code voit dans la première ligne du Sheets
        first_user = df_m.iloc[0]
        st.write(f"Dans le Sheets, ligne 1 voit : Login: [{first_user['Login']}] | MDP: [{first_user['Password']}]")
        # --------------------------

        user_row = df_m[(df_m['Login'] == u_input) & (df_m['Password'] == p_input)]
        
        if not user_row.empty:
            st.session_state['connected'] = True
            st.session_state['user_login_name'] = u_input
            st.session_state['user_role'] = "Admin" if u_input == "Admin" else user_row.iloc[0]['Role']
            st.session_state['user_pseudo'] = user_row.iloc[0]['Pseudo']
            log_invisible("Connexion", "Succès")
            return
    st.error("Identifiants incorrects.")# --- 3. PAGE DE CONNEXION ---
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
    # --- 4. NAVIGATION ---
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['user_pseudo']}")
        st.write(f"Grade : **{st.session_state['user_role']}**")
        menu = ["Tableau de bord"]
        if st.session_state['user_login_name'] == "Admin": 
            menu += ["Comptabilité Globale", "Gestion des Membres", "Archives de la Niebla"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- PAGE : TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["💰 ATM", "🛒 Supérette", "🏎️ Go Fast", "🏠 Cambriolage", "🌿 Drogue"])

        def handle_submit(action, butin=0, drogue="N/A", quantite=0):
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                df_rep = conn.read(worksheet="Rapports", ttl=0)
                df_treso = conn.read(worksheet="Tresorerie", ttl=0)
                
                new_rep = pd.DataFrame([{"Date": now, "Membre": st.session_state['user_pseudo'], "Action": action, "Drogue": drogue, "Quantite": float(quantite), "Butin": float(butin)}])
                new_treso = pd.DataFrame([{"Date": now, "Type": "Recette", "Etat": "Sale", "Catégorie": action, "Montant": float(butin), "Note": f"Rapport de {st.session_state['user_pseudo']}"}])
                
                conn.update(worksheet="Rapports", data=pd.concat([df_rep, new_rep], ignore_index=True))
                conn.update(worksheet="Tresorerie", data=pd.concat([df_treso, new_treso], ignore_index=True))
                st.success("Transmis !"); time.sleep(1); reset_form(); st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        with tabs[0]:
            with st.form(key=f"atm_{st.session_state.form_key}"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER ATM"): handle_submit("ATM", butin=b)
        with tabs[1]:
            with st.form(key=f"sup_{st.session_state.form_key}"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER SUPERETTE"): handle_submit("Supérette", butin=b)
        with tabs[2]:
            with st.form(key=f"gf_{st.session_state.form_key}"):
                b = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("VALIDER GO FAST"): handle_submit("Go Fast", butin=b)
        with tabs[3]:
            with st.form(key=f"cam_{st.session_state.form_key}"):
                if st.form_submit_button("VALIDER CAMBRIOLAGE"): handle_submit("Cambriolage")
        with tabs[4]:
            with st.form(key=f"dr_{st.session_state.form_key}"):
                d_select = st.selectbox("Produit", DRUG_LIST)
                q = st.number_input("Quantité", min_value=0.0)
                b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): handle_submit("Drogue", butin=b, drogue=d_select, quantite=-abs(q))

        st.markdown("---")
        st.write("### 📊 STATS DE LA SEMAINE")
        try:
            df_s = conn.read(worksheet="Rapports", ttl=0)
            df_m = get_members()
            if not df_s.empty:
                df_s['Date'] = pd.to_datetime(df_s['Date'], errors='coerce')
                lundi = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).replace(hour=0, minute=0, second=0)
                # On filtre les logs système pour ne pas fausser les stats
                week_data = df_s[(df_s['Date'] >= lundi) & (~df_s['Action'].str.contains(r'\[LOG\]', na=False))]
                
                for _, m in df_m.iterrows():
                    if m['Login'] != "Admin":
                        p = m['Pseudo']
                        u_data = week_data[week_data['Membre'] == p]
                        act = len(u_data[u_data['Action'] != "Drogue"])
                        vnt = abs(u_data[u_data['Action'] == "Drogue"]['Quantite'].sum())
                        c1, c2, c3 = st.columns([1, 2, 2])
                        c1.write(f"**{p}**")
                        c2.progress(min(float(act)/20, 1.0), text=f"Actions: {act}")
                        c3.progress(min(float(vnt)/300, 1.0), text=f"Ventes: {int(vnt)}")
        except: pass

    # --- PAGE : GESTION MEMBRES (ADMIN) ---
    elif choice == "Gestion des Membres":
        st.markdown('<div class="gta-title">Membres</div>', unsafe_allow_html=True)
        df_m = get_members()
        for i, r in df_m.iterrows():
            if r['Login'] == "Admin": continue
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"👤 **{r['Pseudo']}**")
            curr_r = r['Role']
            new_r = c2.selectbox(f"Grade", ROLES_LIST, index=ROLES_LIST.index(curr_r) if curr_r in ROLES_LIST else 0, key=f"r_{r['Login']}")
            if c3.button("MAJ", key=f"b_{r['Login']}"):
                df_m.at[i, 'Role'] = new_r
                conn.update(worksheet="Membres", data=df_m)
                log_invisible("Grade", f"{r['Pseudo']} -> {new_r}")
                st.success("Fait !"); time.sleep(1); st.rerun()

    # --- PAGE : COMPTABILITÉ (ADMIN) ---
    elif choice == "Comptabilité Globale":
        st.markdown('<div class="gta-title">Tresorerie</div>', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["📊 Solde", "🧼 Blanchiment", "📦 Stocks"])
        
        with t1:
            with st.form("op_man"):
                st.write("#### Opération Manuelle")
                col1, col2, col3 = st.columns(3)
                typ = col1.selectbox("Type", ["Recette", "Dépense"])
                et = col2.selectbox("Argent", ["Sale", "Propre"])
                mnt = col3.number_input("Montant ($)", min_value=0)
                cat = st.text_input("Catégorie / Note")
                if st.form_submit_button("Enregistrer"):
                    try:
                        df_c = conn.read(worksheet="Tresorerie", ttl=0)
                        new_o = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Type": typ, "Etat": et, "Catégorie": "Manuel", "Montant": float(mnt), "Note": cat}])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_o], ignore_index=True))
                        st.success("OK !"); time.sleep(1); st.rerun()
                    except: st.error("Erreur Sheets.")

        with t2:
            with st.form("blanchiment"):
                st.write("#### Blanchiment")
                m_s = st.number_input("Montant sale ($)", min_value=0)
                tx = st.slider("Taux (%)", 0, 100, 20)
                if st.form_submit_button("Lancer le lavage"):
                    try:
                        p_net = m_s * (1 - tx/100)
                        df_t = conn.read(worksheet="Tresorerie", ttl=0)
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        lignes = pd.DataFrame([
                            {"Date": now, "Type": "Dépense", "Etat": "Sale", "Catégorie": "Lavage", "Montant": float(m_s), "Note": "Sortie sale"},
                            {"Date": now, "Type": "Recette", "Etat": "Propre", "Catégorie": "Lavage", "Montant": float(p_net), "Note": f"Retour propre (-{tx}%)"}
                        ])
                        conn.update(worksheet="Tresorerie", data=pd.concat([df_t, lignes], ignore_index=True))
                        st.success("Blanchi !"); time.sleep(1); st.rerun()
                    except: st.error("Erreur.")

        with t3:
            with st.form("stock"):
                st.write("#### Entrée de Stock")
                prod = st.selectbox("Produit", DRUG_LIST)
                qty = st.number_input("Quantité", min_value=0.0)
                if st.form_submit_button("Ajouter au stock"):
                    try:
                        df_r = conn.read(worksheet="Rapports", ttl=0)
                        new_s = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Membre": "LA NIEBLA", "Action": "Drogue", "Drogue": prod, "Quantite": float(qty), "Butin": 0}])
                        conn.update(worksheet="Rapports", data=pd.concat([df_r, new_s], ignore_index=True))
                        st.success("Stock mis à jour !"); time.sleep(1); st.rerun()
                    except: st.error("Erreur.")

        try:
            df_v = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_v.empty:
                st.markdown("---")
                def solde(df, e):
                    sub = df[df['Etat'] == e]
                    return sub[sub['Type'] == 'Recette']['Montant'].sum() - sub[sub['Type'] == 'Dépense']['Montant'].sum()
                s_p, s_s = solde(df_v, 'Propre'), solde(df_v, 'Sale')
                c1, c2, c3 = st.columns(3)
                c1.metric("SOLDE PROPRE", f"{s_p:,.0f} $")
                c2.metric("SOLDE SALE", f"{s_s:,.0f} $")
                c3.metric("TOTAL", f"{(s_p+s_s):,.0f} $")
        except: pass

    # --- PAGE : ARCHIVES (ADMIN) ---
    elif choice == "Archives de la Niebla":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        try:
            df_arc = conn.read(worksheet="Rapports", ttl=0)
            st.dataframe(df_arc.sort_index(ascending=False), use_container_width=True)
        except: st.error("Erreur lecture archives.")
