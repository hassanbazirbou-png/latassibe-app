import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LATASSIBE App", page_icon="📦", layout="centered")

# --- STYLES CSS (POUR LE LOOK OR ET NOIR) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: #D4AF37;
    }
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        background-color: #D4AF37;
        color: black;
        border-radius: 5px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #333333;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE ---
col1, col2 = st.columns([1, 4])
with col1:
    st.write("🌐") # Ici on mettrait votre logo
with col2:
    st.title("LATASSIBE")
    st.caption("SOLUTION SERVICES - NGAOUNDÉRÉ")

st.divider()

# --- MENU DE NAVIGATION ---
menu = st.sidebar.selectbox("Menu", ["📦 Suivi de Colis", "💰 Estimer un Tarif", "🔐 Espace Admin"])

# --- BASE DE DONNÉES SIMULÉE (A remplacer par un vrai fichier Excel/SQL) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Code_Colis': ['LTS-001', 'LTS-002'],
        'Destinataire': ['Moussa B.', 'Fatima A.'],
        'Quartier': ['Bini', 'Centre-Ville'],
        'Statut': ['En Livraison', 'Disponible au dépôt'],
        'Date': ['25-12-2025', '24-12-2025']
    })

# --- PAGE 1 : SUIVI DE COLIS (Pour vos clients) ---
if menu == "📦 Suivi de Colis":
    st.subheader("Où est votre colis ?")
    search_code = st.text_input("Entrez votre numéro de suivi (ex: LTS-001)")
    
    if st.button("Rechercher"):
        result = st.session_state.data[st.session_state.data['Code_Colis'] == search_code]
        if not result.empty:
            statut = result.iloc[0]['Statut']
            st.success(f"Statut : {statut}")
            st.info(f"Destinataire : {result.iloc[0]['Destinataire']}")
            st.write(f"Dernière mise à jour : {result.iloc[0]['Date']}")
            
            # Barre de progression visuelle
            if statut == "Reçu":
                st.progress(25)
            elif statut == "En Livraison":
                st.progress(75)
            elif statut == "Livré":
                st.progress(100)
        else:
            st.error("Code incorrect ou colis non trouvé.")

# --- PAGE 2 : ESTIMATEUR DE PRIX (Pour la prospection) ---
elif menu == "💰 Estimer un Tarif":
    st.subheader("Simulateur de Livraison")
    
    zone = st.selectbox("Quelle zone ?", ["Zone A: Ngaoundéré Ville", "Zone B: Périphérie (Dang, Bini...)"])
    poids = st.radio("Taille du colis", ["Petit (-5kg)", "Moyen/Gros (+5kg)"])
    express = st.checkbox("Livraison Express (Prioritaire)")
    
    prix = 0
    if zone == "Zone A: Ngaoundéré Ville":
        prix = 1000 if "Petit" in poids else 1500
    else:
        prix = 1500 if "Petit" in poids else 3000 # Prix ajusté selon votre demande précédente
        
    if express:
        prix += 1000 # Supplément express
        
    st.metric(label="Tarif Estimé", value=f"{prix} FCFA")
    st.caption("*Tarif indicatif incluant la gestion logistique.*")
    
    st.write("📞 **Contactez-nous pour valider : 654830021**")

# --- PAGE 3 : ADMIN (Pour vous) ---
elif menu == "🔐 Espace Admin":
    st.subheader("Gestion Interne LATASSIBE")
    password = st.text_input("Mot de passe", type="password")
    
    if password == "admin123": # Mot de passe simple pour l'exemple
        st.write("### Liste des colis en cours")
        st.dataframe(st.session_state.data)
        
        st.write("### Ajouter un nouveau colis")
        new_code = st.text_input("Nouveau Code")
        new_dest = st.text_input("Nom Destinataire")
        new_quartier = st.text_input("Quartier")
        new_statut = st.selectbox("Statut", ["Reçu", "En Livraison", "Livré", "Disponible au dépôt"])
        
        if st.button("Ajouter au système"):
            new_row = pd.DataFrame({
                'Code_Colis': [new_code],
                'Destinataire': [new_dest],
                'Quartier': [new_quartier],
                'Statut': [new_statut],
                'Date': [datetime.now().strftime("%d-%m-%Y")]
            })
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            st.success("Colis ajouté avec succès !")
    elif password:
        st.error("Mot de passe incorrect")