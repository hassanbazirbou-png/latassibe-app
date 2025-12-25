import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==============================================================================
# 1. CONFIGURATION DU SITE & IDENTITÉ VISUELLE
# ==============================================================================
st.set_page_config(page_title="LATASSIBE MANAGER", page_icon="🦅", layout="wide")

# URL DU LOGO (Tu pourras remplacer ce lien par le lien de ton image plus tard)
LOGO_URL = "https://z-p3-scontent.fnsi1-2.fna.fbcdn.net/v/t39.30808-6/605500787_1270483641767299_1345187654929165393_n.jpg?stp=dst-jpg_s960x960_tt6&_nc_cat=106&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeEDM52dJPlWEfxZs9Z1UB1hrgq3Zf9DQg-uCrdl_0NCD16WcnxokZdIDxmIDrAZVC1DQdOKRP0d-SuA3csin24f&_nc_ohc=8PYjqrsRSqUQ7kNvwFL1CV4&_nc_oc=AdnsYlTskCJ8QKOryGLPTO_3EJJpwHBq_D83Vl6TFEkAO6chC_fwp1ARo7hPhvk1ZuA&_nc_zt=23&_nc_ht=z-p3-scontent.fnsi1-2.fna&_nc_gid=9rf1usD8pxGc3jXTbConrw&oh=00_AfkQXBQbxbITOceBwxt21vs8OIi6VRn-OucivHqo-HrgIw&oe=69539EB0" 

# --- LE STYLE LATASSIBE (Gold & Black) ---
st.markdown("""
    <style>
    /* Fond global */
    .stApp { background-color: #F4F4F4; color: #1E1E1E; }
    
    /* Titres en Or et Noir */
    h1, h2, h3 { color: #1E1E1E !important; font-family: 'Arial Black', sans-serif; }
    h1 span, h2 span { color: #D4AF37 !important; }
    
    /* Barre latérale (Sidebar) */
    [data-testid="stSidebar"] { background-color: #1E1E1E; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #D4AF37 !important; }
    
    /* Boutons (Or) */
    .stButton>button { 
        background-color: #D4AF37; 
        color: white; 
        border: none; 
        font-weight: bold; 
        border-radius: 5px;
        text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #B5952F; color: white; }
    
    /* Métriques (Cartes Chiffres) */
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 28px !important; }
    .stMetric { background-color: white; border-left: 5px solid #D4AF37; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    
    /* Messages Succès */
    .stSuccess { background-color: #D4AF3733; border-color: #D4AF37; color: #1E1E1E; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. INITIALISATION DES DONNÉES (MÉMOIRE)
# ==============================================================================

# A. Base Clients (Sécurisée)
if 'users_db' not in st.session_state:
    st.session_state.users_db = pd.DataFrame([
        {"identifiant": "admin", "mdp": "admin", "nom": "LATASSIBE DIRECTION", "role": "admin"},
        {"identifiant": "maimouna", "mdp": "1234", "nom": "Boutique Maimouna", "role": "client"},
        {"identifiant": "electro", "mdp": "1234", "nom": "Electronix 237", "role": "client"}
    ])

# B. Base Stock (Inventaire)
if 'stock_db' not in st.session_state:
    st.session_state.stock_db = pd.DataFrame({
        'Marchand': ['Boutique Maimouna', 'Boutique Maimouna', 'Electronix 237'],
        'Article': ['Robe Bazin', 'Sac à main', 'Ecouteurs BT'],
        'Total_Recu': [10, 5, 20],        
        'Total_Livre': [5, 2, 10],        
        'Stock_Actuel': [5, 3, 10],       
        'Prix_Vente': [15000, 5000, 3000]
    })

# C. Base Livraisons (Flux)
if 'livraisons_db' not in st.session_state:
    st.session_state.livraisons_db = pd.DataFrame(columns=[
        'ID', 'Date', 'Marchand', 'Article', 'Client_Final', 
        'Quartier', 'Zone', 'Prix_Marchand', 'Frais_Livraison', 
        'Total_Encaisse', 'Statut'
    ])

# D. Gestion Session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# E. Tarifs Officiels
TARIFS = {
    "Zone A (Ville)": 1000,
    "Zone B (Université/Dang)": 2000,
    "Zone C (Extérieur)": 3000
}

# ==============================================================================
# 3. ÉCRAN DE CONNEXION (LOGIN)
# ==============================================================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' width='150'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>CONNEXION</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            uid = st.text_input("Identifiant")
            pwd = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("ACCÉDER À L'ESPACE")
            
            if submit:
                users = st.session_state.users_db
                check = users[(users['identifiant'] == uid) & (users['mdp'] == pwd)]
                
                if not check.empty:
                    st.session_state.current_user = check.iloc[0].to_dict()
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

# ==============================================================================
# 4. PLATEFORME PRINCIPALE
# ==============================================================================
else:
    USER = st.session_state.current_user
    NOM = USER['nom']
    ROLE = USER['role']
    
    # --- BARRE LATÉRALE (SIDEBAR) ---
    with st.sidebar:
        st.image(LOGO_URL, width=100)
        st.title("LATASSIBE")
        st.write("---")
        st.write(f"Connecté : **{NOM}**")
        st.caption(f"Statut : {ROLE.upper()}")
        st.write("---")
        if st.button("🔴 SE DÉCONNECTER"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

    # ==========================================================================
    # VUE CLIENT (E-COMMERÇANT)
    # ==========================================================================
    if ROLE == "client":
        st.markdown(f"### 👋 Bienvenue, <span style='color:#D4AF37'>{NOM}</span>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📦 STOCK & ENVOI", "💰 MES FINANCES", "❓ SIMULATEUR"])
        
        # 1. GESTION STOCK & EXPÉDITION
        with tab1:
            col_stock, col_form = st.columns([3, 2])
            
            with col_stock:
                st.subheader("Mon Stock au Dépôt")
                df_s = st.session_state.stock_db
                my_stock = df_s[df_s['Marchand'] == NOM]
                st.dataframe(my_stock[['Article', 'Stock_Actuel', 'Prix_Vente']], use_container_width=True)
                
                with st.expander("➕ Déposer un nouvel article au bureau"):
                    with st.form("add_st"):
                        na = st.text_input("Nom Article")
                        nq = st.number_input("Quantité", min_value=1)
                        np = st.number_input("Prix Vente", step=500)
                        if st.form_submit_button("Ajouter"):
                            # Logique Ajout/Cumul
                            exist = st.session_state.stock_db.index[(st.session_state.stock_db['Marchand']==NOM) & (st.session_state.stock_db['Article']==na)].tolist()
                            if exist:
                                st.session_state.stock_db.at[exist[0], 'Stock_Actuel'] += nq
                                st.session_state.stock_db.at[exist[0], 'Total_Recu'] += nq
                            else:
                                new = {'Marchand':NOM, 'Article':na, 'Total_Recu':nq, 'Total_Livre':0, 'Stock_Actuel':nq, 'Prix_Vente':np}
                                st.session_state.stock_db = pd.concat([st.session_state.stock_db, pd.DataFrame([new])], ignore_index=True)
                            st.success("Stock ajouté !"); st.rerun()

            with col_form:
                st.subheader("🚀 Expédier un colis")
                dispo = my_stock[my_stock['Stock_Actuel'] > 0]
                
                if dispo.empty:
                    st.warning("Stock vide. Ajoutez des articles d'abord.")
                else:
                    with st.form("ship"):
                        art = st.selectbox("Article à livrer", dispo['Article'].unique())
                        info = dispo[dispo['Article'] == art].iloc[0]
                        st.caption(f"Prix : {info['Prix_Vente']} FCFA")
                        
                        cli = st.text_input("Nom & Tel Client")
                        qtr = st.text_input("Quartier")
                        zon = st.selectbox("Zone", list(TARIFS.keys()))
                        
                        total = info['Prix_Vente'] + TARIFS[zon]
                        st.markdown(f"**Total à encaisser : {total} FCFA**")
                        
                        if st.form_submit_button("VALIDER LA LIVRAISON"):
                            # Création commande
                            new_liv = {
                                'ID': f"LIV-{int(time.time())}", 'Date': datetime.now().strftime("%d-%m-%Y"),
                                'Marchand': NOM, 'Article': art, 'Client_Final': cli, 'Quartier': qtr, 'Zone': zon,
                                'Prix_Marchand': info['Prix_Vente'], 'Frais_Livraison': TARIFS[zon],
                                'Total_Encaisse': total, 'Statut': 'En Cours'
                            }
                            st.session_state.livraisons_db = pd.concat([st.session_state.livraisons_db, pd.DataFrame([new_liv])], ignore_index=True)
                            
                            # Update Stock
                            idx = st.session_state.stock_db.index[(st.session_state.stock_db['Marchand']==NOM) & (st.session_state.stock_db['Article']==art)].tolist()[0]
                            st.session_state.stock_db.at[idx, 'Stock_Actuel'] -= 1
                            st.session_state.stock_db.at[idx, 'Total_Livre'] += 1
                            
                            st.success("Demande envoyée !"); st.rerun()

        # 2. FINANCES
        with tab2:
            st.subheader("Portefeuille")
            df_l = st.session_state.livraisons_db
            # Argent disponible = Colis livrés mais PAS ENCORE payés au marchand
            ventes_ok = df_l[(df_l['Marchand'] == NOM) & (df_l['Statut'] == 'Livré')]
            solde = ventes_ok['Prix_Marchand'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("SOLDE DISPONIBLE", f"{solde:,} FCFA")
            c2.info("Contactez Latassibe pour récupérer vos fonds.")
            
            st.write("Historique des ventes livrées (Argent encaissé) :")
            st.dataframe(ventes_ok[['Date', 'Article', 'Prix_Marchand', 'Client_Final']])

        # 3. SIMULATEUR
        with tab3:
            st.write("Calculatrice rapide pour info client")
            pp = st.number_input("Prix Article", step=500)
            zz = st.selectbox("Destination", list(TARIFS.keys()))
            st.metric("Total Facture", f"{pp + TARIFS[zz]} FCFA")

    # ==========================================================================
    # VUE ADMIN (LATASSIBE)
    # ==========================================================================
    elif ROLE == "admin":
        st.markdown("### 🦅 DASHBOARD <span style='color:#D4AF37'>LATASSIBE</span>", unsafe_allow_html=True)
        
        # --- METRICS DU JOUR ---
        today = datetime.now().strftime("%d-%m-%Y")
        df_all = st.session_state.livraisons_db
        
        # Filtres
        day_sales = df_all[(df_all['Date'] == today) & (df_all['Statut'] == 'Livré')]
        global_sales = df_all[df_all['Statut'] == 'Livré']
        en_cours = df_all[df_all['Statut'] == 'En Cours']
        
        # Calcul de la Dette Réelle (Ce qui est 'Livré' mais pas encore 'Payé au Marchand')
        dette_active = df_all[df_all['Statut'] == 'Livré']['Prix_Marchand'].sum()
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("CASH ENTRÉ (Jour)", f"{day_sales['Total_Encaisse'].sum():,} F")
        k2.metric("MON CA (Global)", f"{global_sales['Frais_Livraison'].sum():,} F")
        k3.metric("DETTE ACTIVE", f"{dette_active:,} F", delta="À Reverser", delta_color="inverse")
        k4.metric("EN COURS", len(en_cours))
        
        st.divider()
        
        tabs = st.tabs(["⚡ PILOTAGE", "👥 CLIENTS & STOCK", "⚙️ CONFIG"])
        
        # 1. PILOTAGE DES LIVRAISONS
        with tabs[0]:
            st.subheader("Suivi des Colis")
            st.info("💡 Astuce : Passez le statut à **'Payé au Marchand'** une fois que vous avez donné l'argent au client. Cela fera baisser votre dette.")
            
            edited_df = st.data_editor(
                df_all,
                column_config={
                    "Statut": st.column_config.SelectboxColumn(
                        "Action",
                        options=["En Cours", "Livré", "Annulé", "Payé au Marchand"],
                        required=True,
                    ),
                    "Total_Encaisse": st.column_config.NumberColumn("Total", format="%d F"),
                },
                use_container_width=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 SAUVEGARDER LES MODIFICATIONS"):
                st.session_state.livraisons_db = edited_df
                st.success("Mise à jour effectuée avec succès !")
                st.rerun()

        # 2. CLIENTS & STOCK
        with tabs[1]:
            c_stock, c_users = st.columns(2)
            
            with c_stock:
                st.subheader("Inventaire Global")
                st.dataframe(st.session_state.stock_db, use_container_width=True)
                
            with c_users:
                st.subheader("Liste Clients")
                # On masque les mots de passe pour l'affichage
                display_users = st.session_state.users_db.copy()
                display_users['mdp'] = "****" 
                st.dataframe(display_users, use_container_width=True)
                
                with st.expander("Ajouter un nouveau client"):
                    with st.form("new_u"):
                        nu = st.text_input("Identifiant")
                        np = st.text_input("Mot de Passe")
                        nn = st.text_input("Nom Boutique")
                        if st.form_submit_button("Créer"):
                            new = {"identifiant": nu, "mdp": np, "nom": nn, "role": "client"}
                            st.session_state.users_db = pd.concat([st.session_state.users_db, pd.DataFrame([new])], ignore_index=True)
                            st.success("Client créé !"); st.rerun()

        # 3. ZONE DE DANGER
        with tabs[2]:
            st.error("Zone de réinitialisation")
            if st.button("🔥 FORMATER TOUTE L'APPLICATION (RAZ)"):
                st.session_state.livraisons_db = pd.DataFrame(columns=st.session_state.livraisons_db.columns)
                st.session_state.stock_db = pd.DataFrame(columns=st.session_state.stock_db.columns)
                st.warning("Système remis à zéro.")
                time.sleep(1)
                st.rerun()

