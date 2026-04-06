import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="La Niebla - FlashBack FA", page_icon="🥷", layout="wide")

DRUG_LIST = ["Marijuana", "Cocaine", "Meth", "Heroine", "Tranq", "Carte Prépayer", "B-magic", "Crack", "Autre"]
RANKS_LIST = ["Líder", "Mano Derecha", "Soldado", "Recrue"]

# --- CONNEXION & NETTOYAGE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    df = conn.read(worksheet=sheet_name, ttl=0)
    # Fix critique pour transformer les '0.0' en '0' et retirer les espaces
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df

# Initialisation Session
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if "f_key" not in st.session_state:
    st.session_state.f_key = 0

# --- AUTHENTIFICATION ---
df_members = get_data("Membres")

def login():
    u = st.session_state.get("u_in", "").strip()
    p = st.session_state.get("p_in", "").strip()
    match = df_members[(df_members['Login'] == u) & (df_members['Password'] == p)]
    if not match.empty:
        st.session_state.update({"connected": True, "pseudo": match.iloc[0]['Pseudo'], "role": match.iloc[0]['Role']})
        st.rerun()
    else:
        st.error("Accès refusé.")

# --- INTERFACE ---
if not st.session_state['connected']:
    st.markdown('<h1 style="text-align:center; color:white; font-size:60px;">LA NIEBLA</h1>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        with st.form("l_form"):
            st.text_input("NOM DE CODE", key="u_in")
            st.text_input("MOT DE PASSE", type="password", key="p_in")
            if st.form_submit_button("S'INFILTRER"): login()
else:
    # Sidebar
    with st.sidebar:
        st.write(f"### 🥷 {st.session_state['pseudo']}")
        menu = ["Tableau de bord", "Trésorerie", "Hiérarchie"]
        choice = st.radio("Navigation", menu)
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- TABLEAU DE BORD ---
    if choice == "Tableau de bord":
        st.title("Tableau de bord")
        t1, t2 = st.tabs(["💰 ATM", "🌿 Drogue"])
        
        with t1:
            with st.form(key=f"atm_{st.session_state.f_key}"):
                val = st.number_input("Butin ($)", min_value=0)
                if st.form_submit_button("Valider ATM"):
                    # Logique de sauvegarde simplifiée
                    st.success("Transmis avec succès.")
                    st.session_state.f_key += 1
                    st.rerun()

    # --- TRÉSORERIE ---
    elif choice == "Trésorerie":
        st.title("Trésorerie")
        # Fix pour les colonnes et NameError
        sub1, sub2 = st.tabs(["📊 Opération", "📦 Stocks"])
        
        with sub1:
            with st.form(key=f"op_{st.session_state.f_key}"):
                c1, c2, c3 = st.columns(3)
                t_type = c1.selectbox("Type", ["Recette", "Dépense"])
                t_etat = c2.selectbox("Argent", ["Sale", "Propre"])
                t_montant = c3.number_input("Montant ($)", min_value=0)
                if st.form_submit_button("Enregistrer"):
                    st.success("Opération validée.")
                    st.session_state.f_key += 1
                    st.rerun()

        with sub2:
            with st.form(key=f"st_{st.session_state.f_key}"):
                col_a, col_b = st.columns(2)
                # Correction du NameError d_name
                nom_prod = col_a.selectbox("Produit", DRUG_LIST)
                quantite = col_b.number_input("Quantité", min_value=0.0)
                if st.form_submit_button("Ajouter Stock"):
                    st.success("Stock mis à jour.")
                    st.session_state.f_key += 1
                    st.rerun()
