# --- PAGE ADMIN : COMPTABILITÉ GLOBALE ---
    elif choice == "Comptabilité Globale":
        st.write("## 🏛️ GESTION DU COFFRE")
        
        # Affichage du solde actuel
        try:
            df_all = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_all.empty:
                rec = df_all[df_all['Type'] == "Recette"]['Montant'].sum()
                dep = df_all[df_all['Type'] == "Dépense"]['Montant'].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("Recettes Totales", f"{rec:,.0f} $")
                m2.metric("Dépenses Totales", f"{dep:,.0f} $")
                m3.metric("SOLDE DU COFFRE", f"{rec-dep:,.0f} $", delta=float(rec-dep))
        except:
            st.warning("Onglet 'Tresorerie' introuvable dans le Google Sheets.")

        st.markdown("---")
        
        # Formulaire d'ajout (C'est ici que l'erreur se trouvait)
        with st.form("admin_compta"):
            st.write("#### ➕ Ajouter une transaction")
            c1, c2, c3 = st.columns(3)
            t_type = c1.selectbox("Nature", ["Recette", "Dépense"])
            t_cat = c2.text_input("Catégorie (Loyer, Blanchiment, Armes...)")
            t_mont = c3.number_input("Montant ($)", min_value=0) # LIGNE CORRIGÉE ICI
            t_note = st.text_area("Note / Justification")
            
            if st.form_submit_button("ENREGISTRER LA TRANSACTION"):
                try:
                    new_op = pd.DataFrame([{
                        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
                        "Type": t_type, 
                        "Catégorie": t_cat, 
                        "Montant": float(t_mont), 
                        "Note": t_note
                    }])
                    df_c = conn.read(worksheet="Tresorerie", ttl=0)
                    conn.update(worksheet="Tresorerie", data=pd.concat([df_c, new_op], ignore_index=True))
                    st.success("C'est enregistré dans les archives.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {e}")

        # Affichage de l'historique
        st.markdown("---")
        st.write("#### 📝 Historique complet")
        try:
            df_v = conn.read(worksheet="Tresorerie", ttl=0)
            if not df_v.empty:
                st.dataframe(df_v.sort_values(by="Date", ascending=False), use_container_width=True)
            else:
                st.info("Aucun mouvement enregistré pour le moment.")
        except:
            pass
