import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time
import os
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cartel La Niebla | FlashBack FA", page_icon="⚜️", layout="wide")

USERS = {
    "Admin": {"password": "0000", "pseudo": "El Patron", "role_level": 1, "is_drug_manager": True},
    "Alex": {"password": "Alx220717", "pseudo": "Alex Smith", "role_level": 3, "is_drug_manager": False},
    "Dany": {"password": "081219", "pseudo": "Dany Smith", "role_level": 2, "is_drug_manager": True},
    "Aziz": {"password": "asmith", "pseudo": "Aziz Smith", "role_level": 3, "is_drug_manager": False},
    "Alain": {"password": "999cww59", "pseudo": "Alain Bourdin", "role_level": 3, "is_drug_manager": True},
}

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Purple", "Autre"]

# --- 2. VIDÉO DE FOND (CORRIGÉE) ---
# On utilise un lien direct ou une lecture locale robuste
def set_bg_video():
    video_file = "fog.mp4"
    if os.path.exists(video_file):
        with open(video_file, "rb") as f:
            data = f.read()
            import base64
            bin_str = base64.b64encode(data).decode()
            video_html = f'''
            <video autoplay loop muted playsinline style="
                position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;
                z-index: -1; filter: brightness(0.25); opacity: 0.7; object-fit: cover;">
                <source src="data:video/mp4;base64,{bin_str}" type="video/mp4">
            </video>
            '''
            st.markdown(video_html, unsafe_allow_html=True)
    else:
        # Fallback si le fichier n'est pas trouvé pour éviter le bandeau jaune moche
        st.markdown('<style>.stApp { background-color: #0e1117; }</style>', unsafe_allow_html=True)

set_bg_video()

# --- 3. STYLE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Marcellus&display=swap');
    
    /* Fond transparent pour l'application */
    .stApp { background: transparent; }
    
    /* Couleurs des textes et polices */
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stWidgetLabel"] { 
        color: #f7e0a3 !important; 
        font-family: 'Marcellus', serif !important; 
    }
    
    /* Titre principal */
    .gta-title { 
        font-family: 'UnifrakturMaguntia', cursive; 
        font-size: 80px; 
        color: transparent; 
        background-image: linear-gradient(to bottom, #f7e0a3, #b48c3e, #f7e0a3); 
        -webkit-background-clip: text; 
        background-clip: text; 
        text-align: center; 
        margin-top: -50px; 
    }
    
    /* MODIFICATION DE L'OPACITÉ ICI */
    /* background-color: rgba(10, 10, 10, 0.4) -> 0.4 = 40% d'opacité */
    .stForm { 
        background-color: rgba(10, 10, 10, 0.4) !important; 
        border: 1px solid rgba(180, 140, 62, 0.5) !important; 
        border-radius: 12px; 
        padding: 20px;
        backdrop-filter: blur(5px); /* Effet de flou derrière le formulaire */
    }
    
    /* Sidebar (Barre latérale) plus ou moins opaque */
    [data-testid="stSidebar"] { 
        background-color: rgba(15, 15, 15, 0.7) !important; 
        border-right: 1px solid #b48c3e;
        backdrop-filter: blur(10px);
    }
    
    /* Barre de progression */
    .stProgress > div > div > div > div { 
        background-image: linear-gradient(to right, #b48c3e, #f7e0a3) !important; 
    }
    
    /* Tableaux */
    th { color: #b48c3e !important; background-color: rgba(0,0,0,0.2) !important; } 
    td { color: #ffffff !important; background-color: rgba(0,0,0,0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_now():
    return (datetime.datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

if 'connected' not in st.session_state:
    st.session_state['connected'] = False

# --- 4. LOGIQUE CONNEXION ---
if not st.session_state['connected']:
    st.markdown('<div class="gta-title">La Niebla</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login"):
            u_in = st.text_input("NOM DE CODE")
            p_in = st.text_input("MOT DE PASSE", type="password")
            if st.form_submit_button("S'INFILTRER"):
                if u_in in USERS and USERS[u_in]["password"] == p_in:
                    u_data = USERS[u_in]
                    st.session_state.update({"connected": True, "user_pseudo": u_data["pseudo"], "role_level": u_data["role_level"], "is_drug_manager": u_data["is_drug_manager"]})
                    st.rerun()
                else: st.error("Accès refusé.")
else:
    u_pseudo = st.session_state.get('user_pseudo')
    u_role_lv = st.session_state.get('role_level')
    is_drug_boss = st.session_state.get('is_drug_manager')

    with st.sidebar:
        icon = "⚜️" if u_role_lv == 1 else "⭐" if u_role_lv == 2 else "🔫"
        st.write(f"### {u_pseudo} {icon}")
        st.write("---")
        menu = ["🔫 Tableau de bord"]
        if u_role_lv <= 2 or is_drug_boss: menu += ["📦 Gestion des Stocks"]
        if u_role_lv <= 2: menu += ["💵 Trésorerie", "Archives"]
        choice = st.radio("Navigation", menu)
        if st.button("Se déconnecter"): st.session_state.clear(); st.rerun()

    # Lecture des données
    df_full = conn.read(worksheet="Rapports", ttl=0)
    df_v = conn.read(worksheet="Tresorerie", ttl=0)
    df_stock = conn.read(worksheet="Stocks", ttl=0)

    # --- TABLEAU DE BORD ---
    if choice == "🔫 Tableau de bord":
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
            
            if action == "Drogue" and drogue != "N/A":
                dfs = conn.read(worksheet="Stocks", ttl=0)
                if drogue in dfs['Produit'].values:
                    dfs.loc[dfs['Produit'] == drogue, 'Quantite'] += float(qte)
                    conn.update(worksheet="Stocks", data=dfs)
            st.success("Transmis !"); time.sleep(1); st.rerun()

        with tabs[0]:
            with st.form("atm"):
                b = st.number_input("Butin ATM ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("ATM", butin=b)
        with tabs[1]:
            with st.form("sup"):
                b = st.number_input("Butin Supérette ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("Supérette", butin=b)
        with tabs[2]:
            with st.form("gf"):
                b = st.number_input("Butin Go Fast ($)", min_value=0)
                if st.form_submit_button("VALIDER"): submit_op("Go Fast", butin=b)
        with tabs[3]:
            if st.button("CONFIRMER CAMBRIOLAGE"): submit_op("Cambriolage")
        with tabs[4]:
            with st.form("drug"):
                d = st.selectbox("Produit", DRUG_LIST); q = st.number_input("Unités", min_value=0.0); b = st.number_input("Prix total ($)", min_value=0)
                if st.form_submit_button("VALIDER VENTE"): submit_op("Drogue", butin=b, drogue=d, qte=-abs(q))

        st.markdown("---")
       # --- CLASSEMENT & OBJECTIFS ---
        if not df_full.empty:
            df_full['Date'] = pd.to_datetime(df_full['Date'], dayfirst=True, errors='coerce')
            
            # Calcul du cycle : Dimanche 19h
            now = datetime.datetime.now()
            monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            start_week = monday - timedelta(hours=5) 
            if now.weekday() == 6 and now.hour >= 19:
                start_week = now.replace(hour=19, minute=0, second=0, microsecond=0)

            # On filtre les données de la semaine
            week_data = df_full[df_full['Date'] >= start_week].copy()
            
            # On calcule le Net UNIQUEMENT pour l'archive (invisible à l'écran)
            if not week_data.empty:
                week_data['Butin_Net'] = week_data['Butin'] * 0.65
            else:
                week_data['Butin_Net'] = 0.0

            # --- ARCHIVAGE AUTOMATIQUE (Discret) ---
            current_week_id = f"Semaine {now.isocalendar()[1]} - {now.year}"
            df_arch = conn.read(worksheet="Archives_Paies", ttl=0)
            
            if now.weekday() == 6 and now.hour >= 19:
                if df_arch.empty or current_week_id not in df_arch['Semaine'].values:
                    new_rows = []
                    for u_id, info in USERS.items():
                        ps = info["pseudo"]
                        u_data = week_data[week_data['Membre'] == ps]
                        cash_n = u_data[~u_data['Action'].str.contains("Drogue|Ajustement", na=False)]['Butin_Net'].sum()
                        act = len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement"))])
                        vnt = abs(u_data[u_data['Action'] == "Drogue"]['Quantite'].sum())
                        new_rows.append({"Semaine": current_week_id, "Date_Archive": get_now(), "Membre": ps, "Total_Net": float(cash_n), "Actions_Terrain": int(act), "Ventes_Drogue": int(vnt)})
                    conn.update(worksheet="Archives_Paies", data=pd.concat([df_arch, pd.DataFrame(new_rows)], ignore_index=True))

            # --- AFFICHAGE (100% REEL) ---
            st.write("### 📊 Objectifs de la Semaine")
            for u_id, info in USERS.items():
                ps = info["pseudo"]
                u_data = week_data[week_data['Membre'] == ps]
                
                # Ici on utilise 'Butin' (le vrai montant) et non 'Butin_Net'
                cash = u_data[~u_data['Action'].str.contains("Drogue|Ajustement", na=False)]['Butin'].sum()
                
                adj_act = u_data[u_data['Action'] == "Ajustement Actions"]['Quantite'].sum()
                act = len(u_data[(u_data['Action'] != "Drogue") & (~u_data['Action'].str.contains("Ajustement"))]) + adj_act
                adj_vnt = abs(u_data[u_data['Action'] == "Ajustement Ventes"]['Quantite'].sum())
                vnt = abs(u_data[u_data['Action'] == "Drogue"]['Quantite'].sum()) + adj_vnt
                
                c1, c2, c3, c4 = st.columns([1.2, 1, 2, 2])
                c1.markdown(f"**{ps}**")
                c2.write(f"{int(cash):,} $".replace(",", " ")) # Retour au montant brut
                c3.progress(min(float(act)/20, 1.0), text=f"{int(act)}/20")
                c4.progress(min(float(vnt)/300, 1.0), text=f"{int(vnt)}/300")

            st.markdown("---")
            st.write("### 🏆 Classement interne (Revenus)")
            top = week_data.groupby("Membre")["Butin"].sum().reset_index().sort_values(by="Butin", ascending=False)
            for i, row in top.reset_index(drop=True).iterrows():
                st.write(f"{i+1}. {row['Membre']} — **{int(row['Butin']):,} $**".replace(",", " "))

        st.markdown("---")
        st.write("### 🕒 Mes 3 dernières activités")
        mes = df_full[df_full['Membre'] == u_pseudo].tail(3).iloc[::-1].copy()
        if not mes.empty:
            mes['Butin'] = mes['Butin'].apply(lambda x: f"{int(float(x)):,} $".replace(',', ' '))
            st.table(mes[['Date', 'Action', 'Butin']])

   # --- STOCKS ---
    elif choice == "📦 Gestion des Stocks":
        st.markdown('<div class="gta-title">Stocks & Ventes</div>', unsafe_allow_html=True)
        
        # Vérification des produits
        for p in DRUG_LIST:
            if p not in df_stock['Produit'].values:
                df_stock = pd.concat([df_stock, pd.DataFrame([{"Produit": p, "Quantite": 0.0}])], ignore_index=True)
        
        c1, c2 = st.columns([1.2, 1])
        
        with c1:
            st.write("### 📦 État des Réserves")
            df_display = df_stock.copy()
            df_display['Quantite'] = df_display['Quantite'].apply(lambda x: f"{int(x):,}".replace(",", " ") + " unités")
            st.table(df_display)
        
        with c2:
            st.write("### 📝 Nouvelle Opération")
            with st.form("stk_pro"):
                ps = st.selectbox("Produit", DRUG_LIST)
                ms = st.radio("Type de mouvement", ["Vente (Sortie de stock)", "Achat (Entrée de stock)"])
                qs = st.number_input("Quantité (Unités)", min_value=0.0)
                amount = st.number_input("Montant de la transaction ($)", min_value=0)

                if st.form_submit_button("ENREGISTRER L'OPÉRATION"):
                    # 1. Mise à jour du stock physique
                    val_stock = -qs if ms == "Vente (Sortie de stock)" else qs
                    df_stock.loc[df_stock['Produit'] == ps, 'Quantite'] += val_stock
                    conn.update(worksheet="Stocks", data=df_stock)
                    
                    # 2. Mise à jour de la trésorerie (Vente = Recette / Achat = Dépense)
                    type_transa = "Recette" if ms == "Vente (Sortie de stock)" else "Dépense"
                    note_auto = f"{ms} de {int(qs)} unités de {ps} par {u_pseudo}"
                    
                    df_t = conn.read(worksheet="Tresorerie", ttl=0)
                    new_t = pd.DataFrame([{
                        "Date": get_now(),
                        "Type": type_transa,
                        "Etat": "Sale", 
                        "Catégorie": "Drogue",
                        "Montant": float(amount),
                        "Note": note_auto
                    }])
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new_t], ignore_index=True))
                    
                    # --- NOTE : On a supprimé l'enregistrement dans df_r (Rapports) ---
                    # Ainsi, cette opération n'apparaîtra plus dans le classement interne
                    # ni dans les objectifs de la semaine.
                    
                    st.success(f"Opération validée : {ms} enregistrée !")
                    time.sleep(1)
                    st.rerun()
                
                    # 3. Rapport d'activité
                    df_r = conn.read(worksheet="Rapports", ttl=0)
                    new_r = pd.DataFrame([{
                        "Date": get_now(),
                        "Membre": u_pseudo,
                        "Action": "Gestion Stock",
                        "Drogue": ps,
                        "Quantite": float(val_stock),
                        "Butin": float(amount)
                    }])
                    conn.update(worksheet="Rapports", data=pd.concat([df_r, new_r], ignore_index=True))
                    
                    st.success(f"Opération validée : {ms} enregistrée !")
                    time.sleep(1)
                    st.rerun()

    # --- COMPTABILITÉ ---
    elif choice == "💵 Trésorerie":
        st.markdown('<div class="gta-title">Trésorerie</div>', unsafe_allow_html=True)
        def solde(etat):
            return df_v[(df_v['Etat']==etat)&(df_v['Type']=='Recette')]['Montant'].sum() - df_v[(df_v['Etat']==etat)&(df_v['Type']=='Dépense')]['Montant'].sum()
        p, s = solde('Propre'), solde('Sale')
        c1, c2, c3 = st.columns(3)
        c1.metric("PROPRE ⚜️", f"{int(p):,} $".replace(',',' '))
        c2.metric("SALE 💵", f"{int(s):,} $".replace(',',' '))
        
        if u_role_lv == 1:
            st.write("---")
            col_a, col_b = st.columns(2)
            with col_a:
                with st.expander("🛠️ CORRECTIONS"):
                    with st.form("adj"):
                        target = st.selectbox("Membre", [u["pseudo"] for u in USERS.values()])
                        t_adj = st.radio("Type", ["Actions", "Ventes"])
                        v_adj = st.number_input("Valeur (+/-)", value=0.0)
                        if st.form_submit_button("OK"):
                            df_r = conn.read(worksheet="Rapports", ttl=0)
                            new = pd.DataFrame([{"Date": get_now(), "Membre": target, "Action": f"Ajustement {t_adj}", "Drogue": "N/A", "Quantite": v_adj, "Butin": 0}])
                            conn.update(worksheet="Rapports", data=pd.concat([df_r, new], ignore_index=True))
                            st.success("Corrigé !"); time.sleep(1); st.rerun()
            with col_b:
                with st.expander("💰 CAISSE"):
                    with st.form("cais"):
                        tm = st.selectbox("Sens", ["Recette", "Dépense"]); em = st.selectbox("Compte", ["Sale", "Propre"]); vm = st.number_input("Montant", min_value=0); rm = st.text_input("Note")
                        if st.form_submit_button("OK"):
                            df_t = conn.read(worksheet="Tresorerie", ttl=0)
                            new = pd.DataFrame([{"Date": get_now(), "Type": tm, "Etat": em, "Catégorie": "Manuel", "Montant": float(vm), "Note": rm}])
                            conn.update(worksheet="Tresorerie", data=pd.concat([df_t, new], ignore_index=True))
                            st.success("Fait !"); time.sleep(1); st.rerun()
        st.dataframe(df_v.sort_index(ascending=False), use_container_width=True)

    elif choice == "Archives":
        st.markdown('<div class="gta-title">Archives</div>', unsafe_allow_html=True)
        st.dataframe(df_full.sort_index(ascending=False), use_container_width=True)
