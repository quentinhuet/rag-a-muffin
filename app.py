import streamlit as st
import os
import time

from src.data_loader import load_data
from src.embeddings import RAGTool
from src.vector_store import RecipeDB
from src.generator_v2 import MuffinChef

st.set_page_config(
    page_title="Chef Muffin AI",
    page_icon="🧁",
    layout="centered"
)

st.title("👨‍🍳 Chef Muffin")
st.caption("L'assistant culinaire qui ne cuisine que des muffins.")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1046/1046857.png", width=100)
    st.title("Options")
    
    # Bouton de Reset complet
    if st.button("🗑️ Nouvelle Conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.recette_active = None
        st.rerun()

    st.divider()

    # Section Guide / Astuces
    st.markdown("### 💡 Comment ça marche ?")
    st.info(
        """
        **1. Chercher une recette :**
        Demandez simplement *"Je veux des muffins aux pépites de chocolat"* ou *"J'ai des bananes et des noix"*.
        
        **2. Changer d'avis :**
        Si la recette proposée ne vous plaît pas, écrivez **"changer"**.
        Le Chef oubliera la recette actuelle et vous pourrez en chercher une autre !
        """
    )
    
    st.divider()

    # Section Technique 
    st.markdown("### ⚙️ Installation")
    st.caption("⚠️ **Important :** Avant d'utiliser cette interface, assurez-vous d'avoir généré la base de données avec la commande :")
    st.code("python src/build_db.py", language="bash")
    
    st.markdown("---")
    st.caption("v1.0 - Powered by Llama 3 & Marmiton")

# INITIALISATION
@st.cache_resource
def initialize_system():
    print("⚙️ Initialisation du système...")
    
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(current_file_path)
    data_path = os.path.join(project_root, 'data', 'raw', 'recettes_fr.json')

    tool = RAGTool()
    database = RecipeDB()
    chef = MuffinChef()

    # Indexation (si vide) - Copié de ton main.py
    if database.collection.count() == 0:
        with st.spinner("👨‍🍳 Je regarde dans mon livre de recettes..."):
            data = load_data(data_path)
            textes = []
            for recette in data:
                textes.append((recette['texte']))
            
            embeddings = tool.vectoriser(data=textes)
            database.add_recipes(data=data, embeddings=embeddings)
            
    return tool, database, chef

# On charge les objets
tool, database, chef = initialize_system()

# GESTION DE LA MÉMOIRE

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Bonjour ! Je suis Chef Muffin. 🧁\nDonne-moi les ingrédients que tu as, ou le type de muffins que tu veux faire."
    }]

if "recette_active" not in st.session_state:
    st.session_state.recette_active = None

# AFFICHAGE 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# BOUCLE D'INTERACTION
if prompt := st.chat_input("Discute avec le chef..."):
    
    # A. Affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. Logique du Cerveau (Adaptée de ton main.py)
    response_text = ""
    
    # --- MÉCANIQUE DE RESET ---
    mots_cles_changement = ["changer", "autre recette", "nouvelle recherche", "nouveau"]
    
    if any(mot in prompt.lower() for mot in mots_cles_changement):
        st.session_state.recette_active = None
        chef.reset_memory()
        response_text = "🔄 D'accord, changeons de recette ! Je t'écoute pour une nouvelle envie."

    # MODE RECHERCHE
    elif st.session_state.recette_active is None:
        with st.spinner("👨‍🍳 Je regarde dans mon livre de recettes..."):
            vecteur_question = tool.vectoriser([prompt])[0].tolist()
            reponse = database.search(query_embedding=vecteur_question, k=1)
            
            if reponse['documents']:
                recette_found = reponse['documents'][0][0]
                titre = reponse['metadatas'][0][0].get('titre', 'Recette Mystère')
                
                st.session_state.recette_active = recette_found
                
                # Feedback visuel
                st.toast(f"Recette trouvée : {titre}", icon="📖")
                
                response_text = chef.generate_response(context_str=recette_found, query_str=prompt)
            else:
                response_text = "Désolé, je n'ai trouvé aucune recette qui correspond. Essaie avec des ingrédients plus simples (chocolat, myrtille...)."

    # MODE DISCUSSION
    else:
        with st.spinner("👨‍🍳 Chef Muffin réfléchi"):
            response_text = chef.generate_response(context_str=st.session_state.recette_active, query_str=prompt)

    with st.chat_message("assistant"):
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})