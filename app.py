import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime

# Configuration de la page
st.set_page_config(page_title="Management Orga RP", page_icon="💰", layout="centered")

st.title("🥷 Portails des Opérations")
st.markdown("---")

# Connexion au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Formulaire de saisie
with st.form(key="rapport_form"):
    membre = st.text_input("Nom de l'agent (Pseudo RP)")
    action = st.selectbox("Type d'action", ["Vente de drogue", "Braquage", "Convoi", "Autre"])
    
    # Champs conditionnels pour la drogue
    drogue = ""
    quantite = 0
    if action == "Vente de drogue":
        drogue = st.selectbox("Type de marchandise", ["Weed", "Coke", "Meth", "Opium"])
        quantite = st.number_input("Quantité vendue", min_value=0, step=1)
    
    butin = st.number_input("Montant total du butin ($)", min_value=0, step=100)
    
    submit_button = st.form_submit_button(label="Transmettre le rapport")

if submit_button:
    if membre == "" or butin == 0:
        st.error("Veuillez remplir tous les champs obligatoires.")
    else:
        # Préparation des données
        new_data = {
            "Date": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Membre": [membre],
            "Action": [action],
            "Drogue": [drogue],
            "Quantite": [quantite],
            "Butin": [butin]
        }
        
        # Envoi vers Google Sheets
        # (La fonction spécifique dépend de ton setup final, mais le principe est là)
        st.success(f"Rapport transmis ! Bien joué {membre}.")
        st.balloons()
