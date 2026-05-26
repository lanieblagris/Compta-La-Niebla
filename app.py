import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import os

# =========================
# ⚫️ CONFIGURATION
# =========================

st.set_page_config(
    page_title="La División | Network",
    page_icon="⚫️",
    layout="wide"
)

# ⚫️ UTILISATEURS
USERS = {
    "Admin": {"password": "0000", "pseudo": "El Padrino", "role": "Fondateur"},
    "Mateo": {"password": "1234", "pseudo": "Mateo Alvares", "role": "Dirigeant"},
}

# =========================
# ⚫️ STYLE GLOBAL
# =========================

st.markdown("""
<style>

.stApp {
    background-color: #0b0b0f;
    color: #e6e6e6;
}

h1, h2, h3 {
    color: #c9a227;
}

.block-title {
    font-size: 60px;
    text-align: center;
    font-weight: bold;
    color: #c9a227;
    margin-bottom: 20px;
}

.card {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(201,162,39,0.3);
}

.sidebar .sidebar-content {
    background-color: #0f0f14;
}

</style>
""", unsafe_allow_html=True)

# =========================
# ⚫️ SESSION
# =========================

if "connected" not in st.session_state:
    st.session_state.connected = False

# =========================
# ⚫️ LOGIN
# =========================

if not st.session_state.connected:

    st.markdown("<div class='block-title'>LA DIVISIÓN</div>", unsafe_allow_html=True)

    st.markdown("## 🔐 Accès sécurisé au réseau")

    user = st.text_input("Nom de code")
    pwd = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state.connected = True
            st.session_state.user = USERS[user]
            st.rerun()
        else:
            st.error("Accès refusé.")

# =========================
# ⚫️ DASHBOARD
# =========================

else:

    user = st.session_state.user

    # SIDEBAR
    with st.sidebar:
        st.markdown(f"### ⚫️ {user['pseudo']}")
        st.write(f"**Rôle :** {user['role']}")
        st.write("---")

        menu = st.radio("Navigation", [
            "📡 Dashboard",
            "👥 Membres",
            "📦 Stocks",
            "💰 Finance",
            "📁 Dossiers"
        ])

        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # =========================
    # 📡 DASHBOARD
    # =========================

    if menu == "📡 Dashboard":

        st.markdown("<div class='block-title'>DIVISIÓN NETWORK</div>", unsafe_allow_html=True)

        st.markdown("""
        ### ⚫️ Système interne sécurisé

        Bienvenue dans le réseau privé de La División.

        > “Le contrôle appartient à ceux qui observent dans l’ombre.”
        """)

        col1, col2, col3 = st.columns(3)

        col1.markdown("""
        <div class='card'>
        👥 <b>Membres actifs</b><br>
        2 opérateurs
        </div>
        """, unsafe_allow_html=True)

        col2.markdown("""
        <div class='card'>
        📦 <b>Stock global</b><br>
        Système actif
        </div>
        """, unsafe_allow_html=True)

        col3.markdown("""
        <div class='card'>
        💰 <b>Finance</b><br>
        Réseau privé
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # 👥 MEMBRES
    # =========================

    elif menu == "👥 Membres":

        st.markdown("## 👥 Membres du réseau")

        data = pd.DataFrame([
            {"Nom": "Mateo Alvares", "Rôle": "Dirigeant", "Statut": "Actif"},
            {"Nom": "El Padrino", "Rôle": "Fondateur", "Statut": "Actif"}
        ])

        st.table(data)

    # =========================
    # 📦 STOCKS
    # =========================

    elif menu == "📦 Stocks":

        st.markdown("## 📦 Réserves internes")

        stock = pd.DataFrame([
            {"Produit": "Matériel", "Quantité": 12},
            {"Produit": "Argent liquide", "Quantité": 50000},
            {"Produit": "Véhicules", "Quantité": 3}
        ])

        st.table(stock)

    # =========================
    # 💰 FINANCE
    # =========================

    elif menu == "💰 Finance":

        st.markdown("## 💰 Système financier")

        st.markdown("""
        - Recettes internes
        - Transactions privées
        - Flux d'argent contrôlés
        """)

        st.metric("Solde estimé", "125 000 $")

    # =========================
    # 📁 DOSSIERS
    # =========================

    elif menu == "📁 Dossiers":

        st.markdown("## 📁 Fiches internes")

        st.markdown("""
        - Contacts
        - Alliés
        - Observations
        - Informations sensibles
        """)

        st.info("Système de dossiers en développement...")
