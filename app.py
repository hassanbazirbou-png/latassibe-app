import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(page_title="LATASSIBE SOLUTIONS", page_icon="🚚", layout="wide")

# Style Professionnel (Gold & Dark/Grey)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Segoe UI', sans-serif; }
    .stMetric { background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    div[data-testid="stSidebarUserContent"] { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. INITIALISATION DES DONNÉES (PERSISTANCE DE SESSION)
# ==============================================================================

# A. Base Utilisateurs (Modifiable par l'Admin)
if 'users_db' not in st.session_state:
    st.session_state.users_db = pd.DataFrame([
        {"identifiant": "admin", "mdp": "admin", "nom": "LATASSIBE DIRECTION", "role": "admin"},
        {"identifiant": "maimouna", "mdp": "1234", "nom": "Boutique Maimouna", "role": "client"},
        {"identifiant": "electro", "mdp": "1234", "nom": "Electronix 237", "role": "client"}
    ])

# B. Base Stock (L'inventaire dormant au dépôt)
if 'stock_db' not in st.session_state:
    st.session_state.stock_db = pd.DataFrame({
        'Marchand': ['Boutique Maimouna', 'Boutique Maimouna', 'Electronix 237'],
        'Article': ['Robe Bazin', 'Sac à main', 'Ecouteurs BT'],
        'Quantite': [5, 3, 10],
        'Prix_Vente': [15000, 5000, 3000]
    })

# C. Base Livraisons (Le flux logistique)
if 'livraisons_db' not in st.session_state:
    st.session_state.livraisons_db = pd.DataFrame(columns=[
        'ID', 'Date', 'Marchand', 'Article', 'Client_Final', 
        'Quartier', 'Zone', 'Prix_Marchand', 'Frais_Livraison', 
        'Total_Encaisse', 'Statut'
    ])

# D. Gestion de connexion
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# E. Configuration des Tarifs
TARIFS = {
    "Zone A (Ville)": 1000,
    "Zone B (Univ/Dang)": 2000,
    "Zone C (Extérieur)": 3000
}

# ==============================================================================
# 3. FONCTIONS UTILITAIRES
# ==============================================================================
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

# ==============================================================================
# 4. PAGE DE CONNEXION (LOGIN)
# ==============================================================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830310.png", width=120)
        st.title("CONNEXION")
        st.write("Plateforme Logistique LATASSIBE")
        
        with st.form("login_form"):
            uid = st.text_input("Identifiant")
            pwd = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se Connecter")
            
            if submit:
                users = st.session_state.users_db
                check = users[(users['identifiant'] == uid) & (users['mdp'] == pwd)]
                
                if not check.empty:
                    st.session_state.current_user = check.iloc[0].to_dict()
                    st.session_state.logged_in = True
                    st.success("Connexion réussie !")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

# ==============================================================================
# 5. APPLICATION PRINCIPALE (APRÈS LOGIN)
# ==============================================================================
else:
    USER = st.session_state.current_user
    NOM = USER['nom']
    ROLE = USER['role']

    # --- SIDEBAR (Barre latérale commune) ---
    with st.sidebar:
        st.title(f"👤 {NOM}")
        st.info(f"Rôle : {ROLE.upper()}")
        st.divider()
        if st.button("🔴 Se Déconnecter"):
            logout()

    # ==========================================================================
    # SCÉNARIO A : ESPACE CLIENT (E-COMMERÇANT)
    # ==========================================================================
    if ROLE == "client":
        st.title(f"Bienvenue, {NOM}")
        
        # Onglets clairs pour organiser les fonctionnalités
        tab1, tab2, tab3, tab4 = st.tabs(["💰 Calculateur", "📦 Mon Stock", "🚀 Expédier", "📊 Mes Finances"])
        
        # 1. CALCULATEUR DE TARIF (Réintégré)
        with tab1:
            st.subheader("Estimer une livraison")
            c1, c2 = st.columns(2)
            z = c1.selectbox("Zone de destination", list(TARIFS.keys()))
            p = c2.number_input("Prix de votre article", step=500)
            frais = TARIFS[z]
            total = p + frais
            st.success(f"👉 Le client doit payer : **{total} FCFA** (Dont {frais}F pour la livraison)")

        # 2. GESTION STOCK (Voir et Ajouter)
        with tab2:
            st.subheader("Stock disponible au dépôt")
            df_stock = st.session_state.stock_db
            my_stock = df_stock[df_stock['Marchand'] == NOM]
            
            # Affichage tableau
            st.dataframe(my_stock[['Article', 'Quantite', 'Prix_Vente']], use_container_width=True)
            
            with st.expander("➕ Déposer un nouvel article"):
                with st.form("add_stock"):
                    new_art = st.text_input("Nom Article")
                    new_qty = st.number_input("Quantité", min_value=1, value=1)
                    new_price = st.number_input("Prix Vente Unitaire", step=500)
                    if st.form_submit_button("Ajouter au Stock"):
                        line = {'Marchand': NOM, 'Article': new_art, 'Quantite': new_qty, 'Prix_Vente': new_price}
                        st.session_state.stock_db = pd.concat([st.session_state.stock_db, pd.DataFrame([line])], ignore_index=True)
                        st.success("Stock ajouté !")
                        st.rerun()

        # 3. EXPÉDITION (Créer une commande)
        with tab3:
            st.subheader("Lancer une livraison")
            
            # On récupère le stock dispo
            my_stock_dispo = st.session_state.stock_db[
                (st.session_state.stock_db['Marchand'] == NOM) & 
                (st.session_state.stock_db['Quantite'] > 0)
            ]
            
            if my_stock_dispo.empty:
                st.warning("Votre stock est vide. Ajoutez des articles dans l'onglet 'Mon Stock' d'abord.")
            else:
                with st.form("order_form"):
                    col_a, col_b = st.columns(2)
                    art_choix = col_a.selectbox("Quel article ?", my_stock_dispo['Article'].unique())
                    # Auto-remplissage du prix
                    prix_auto = my_stock_dispo[my_stock_dispo['Article'] == art_choix].iloc[0]['Prix_Vente']
                    col_b.info(f"Prix unitaire : {prix_auto} FCFA")
                    
                    st.divider()
                    c_client = st.text_input("Nom & Tel du Client")
                    c_quartier = st.text_input("Quartier")
                    c_zone = st.selectbox("Zone Livraison", list(TARIFS.keys()))
                    
                    if st.form_submit_button("Valider la demande"):
                        frais = TARIFS[c_zone]
                        # Création commande
                        new_liv = {
                            'ID': f"LIV-{int(time.time())}", # ID unique basé sur l'heure
                            'Date': datetime.now().strftime("%d-%m-%Y"),
                            'Marchand': NOM,
                            'Article': art_choix,
                            'Client_Final': c_client,
                            'Quartier': c_quartier,
                            'Zone': c_zone,
                            'Prix_Marchand': prix_auto,
                            'Frais_Livraison': frais,
                            'Total_Encaisse': prix_auto + frais,
                            'Statut': 'En Cours'
                        }
                        # Sauvegarde
                        st.session_state.livraisons_db = pd.concat([st.session_state.livraisons_db, pd.DataFrame([new_liv])], ignore_index=True)
                        
                        # Décrémentation Stock
                        idx = st.session_state.stock_db.index[
                            (st.session_state.stock_db['Marchand'] == NOM) & 
                            (st.session_state.stock_db['Article'] == art_choix)
                        ].tolist()[0]
                        st.session_state.stock_db.at[idx, 'Quantite'] -= 1
                        
                        st.success("Commande envoyée au service logistique !")
                        time.sleep(1)
                        st.rerun()

        # 4. FINANCES (Ce que tu dois au client)
        with tab4:
            st.subheader("Portefeuille")
            df_liv = st.session_state.livraisons_db
            # Filtre : Mes commandes + Statut 'Livré'
            mes_sous = df_liv[(df_liv['Marchand'] == NOM) & (df_liv['Statut'] == 'Livré')]
            
            total_dispo = mes_sous['Prix_Marchand'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Solde Disponible", f"{total_dispo:,} FCFA")
            col2.metric("Colis Livrés", len(mes_sous))
            
            st.write("Détail des ventes terminées :")
            st.dataframe(mes_sous[['Date', 'Article', 'Prix_Marchand', 'Client_Final']], use_container_width=True)

    # ==========================================================================
    # SCÉNARIO B : ESPACE ADMIN (TOI - LATASSIBE)
    # ==========================================================================
    elif ROLE == "admin":
        st.title("🦅 TABLEAU DE BORD GÉNÉRAL")
        
        # NAVIGATION ADMIN
        admin_tabs = st.tabs(["📊 Pilotage & CA", "👥 Gestion Clients", "🏭 Stock Global", "⚙️ Paramètres"])
        
        # 1. PILOTAGE (Les livraisons)
        with admin_tabs[0]:
            # KPIS
            df_all = st.session_state.livraisons_db
            
            ca_total = df_all[df_all['Statut'] == 'Livré']['Frais_Livraison'].sum()
            dette_total = df_all[df_all['Statut'] == 'Livré']['Prix_Marchand'].sum()
            en_cours = len(df_all[df_all['Statut'] == 'En Cours'])
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Mon Chiffre d'Affaires", f"{ca_total:,} FCFA")
            k2.metric("Dette aux Marchands", f"{dette_total:,} FCFA")
            k3.metric("Livraisons En Cours", en_cours, delta_color="inverse")
            
            st.divider()
            st.subheader("Gestion des Livraisons")
            st.info("Modifiez le statut en 'Livré' pour encaisser l'argent.")
            
            # Tableau ÉDITABLE pour changer les statuts
            edited_liv = st.data_editor(
                df_all,
                column_config={
                    "Statut": st.column_config.SelectboxColumn(
                        "Action",
                        options=["En Cours", "Livré", "Annulé", "Payé au Marchand"],
                        required=True
                    )
                },
                use_container_width=True,
                num_rows="dynamic",
                key="editor_livraisons"
            )
            
            if st.button("💾 Sauvegarder les changements"):
                st.session_state.livraisons_db = edited_liv
                st.success("Base de données mise à jour !")
                st.rerun()

        # 2. GESTION CLIENTS (Ajout/Suppression)
        with admin_tabs[1]:
            st.subheader("Partenaires Commerciaux")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.dataframe(st.session_state.users_db, use_container_width=True)
            
            with c2:
                st.write("**Ajouter un Client**")
                with st.form("new_user"):
                    u_id = st.text_input("Identifiant (Login)")
                    u_pass = st.text_input("Mot de passe")
                    u_nom = st.text_input("Nom Commercial")
                    if st.form_submit_button("Créer Compte"):
                        new_u = {"identifiant": u_id, "mdp": u_pass, "nom": u_nom, "role": "client"}
                        st.session_state.users_db = pd.concat([st.session_state.users_db, pd.DataFrame([new_u])], ignore_index=True)
                        st.success("Client créé !")
                        st.rerun()
                
                st.divider()
                st.write("**Supprimer un Client**")
                # Liste sans l'admin
                users_list = st.session_state.users_db[st.session_state.users_db['role'] != 'admin']['identifiant'].unique()
                del_u = st.selectbox("Choisir le compte", users_list)
                if st.button("🗑️ Supprimer définitivement"):
                    st.session_state.users_db = st.session_state.users_db[st.session_state.users_db['identifiant'] != del_u]
                    st.warning("Client supprimé.")
                    st.rerun()

        # 3. STOCK GLOBAL
        with admin_tabs[2]:
            st.subheader("Inventaire du Dépôt (Vue d'ensemble)")
            st.dataframe(st.session_state.stock_db, use_container_width=True)
            # Pas d'édition ici pour simplifier, l'admin peut modifier via le compte client si besoin ou on pourrait ajouter un editor.

        # 4. PARAMÈTRES (Reset)
        with admin_tabs[3]:
            st.error("⚠️ ZONE DANGER")
            if st.button("🔥 RÉINITIALISER TOUTES LES DONNÉES (RAZ)"):
                st.session_state.livraisons_db = pd.DataFrame(columns=st.session_state.livraisons_db.columns)
                st.session_state.stock_db = pd.DataFrame(columns=st.session_state.stock_db.columns)
                st.success("Le système a été remis à zéro.")
                time.sleep(1)
                st.rerun()
