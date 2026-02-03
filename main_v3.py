import os 
import sys
from src.data_loader import load_data
from src.embeddings import RAGTool
from src.vector_store import RecipeDB
from src.generator_v2 import MuffinChef

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)
data_path = os.path.join(project_root, 'data', 'raw', 'mock_recipes.json')

tool = RAGTool()
database = RecipeDB()

# Initialisation de la base de données, si ce n'est pas déjà fait.
if database.collection.count() == 0:
    data = load_data(data_path)
    textes = []
    for recette in data:
        textes.append((recette['texte']))
    
    embeddings = tool.vectoriser(data = textes)
    database.add_recipes(data = data, embeddings=embeddings)

print("✅ Base de données prête !")

# Discussion avec l'utilisateur

#Initialisation du LLM : 
chef = MuffinChef()

recette_active = None

while True:
    question = input("\n 🧑‍🍳 Pose une question sur la recette (ou 'changer' pour une autre) : " if recette_active else "\n 🧑‍🍳 Quelle recette cherches-tu ? (ou 'exit') : ")
    
    if question.lower() in ["exit", "q", "quit"]:
            print("Bon appétit ! 👋")
            break
    
    # --- MÉCANIQUE DE RESET ---
    mots_cles_changement = ["changer", "autre recette", "nouvelle recherche", "nouveau"]
    if any(mot in question.lower() for mot in mots_cles_changement):
        print("🔄 D'accord, changeons de recette !")
        recette_active = None
        chef.reset_memory() # On vide la mémoire du chef
        continue

    # --- CAS 1 : MODE RECHERCHE (Pas de recette active) ---
    if recette_active is None:
        print("🔎 Recherche dans le carnet...")
        vecteur_question = tool.vectoriser([question])[0].tolist()
        reponse = database.search(query_embedding=vecteur_question, k=1)
        
        if reponse['documents']:
            # On a trouvé ! On "verrouille" cette recette
            recette_active = reponse['documents'][0][0] # Le texte de la recette
            titre = reponse['metadatas'][0][0]['titre']
            print(f"📖 J'ai ouvert la page : {titre}")
            
            # On laisse le code continuer vers le LLM 
        else:
            print("❌ Aucune recette trouvée. Essaie autre chose.")
            continue

    # --- CAS 2 : MODE DISCUSSION (Recette active) ---
    
    reponse_llm = chef.generate_response(context_str=recette_active, query_str=question)
    
    print("\n" + "-"*50)
    print(f"👨‍🍳 {reponse_llm}")
    print("-"*50)