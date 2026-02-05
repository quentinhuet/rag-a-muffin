import os 
import sys
from src.data_loader import load_data
from src.embeddings import RAGTool
from src.vector_store import RecipeDB
from src.generator_v2 import MuffinChef

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)
data_path = os.path.join(project_root, 'data', 'raw', 'recettes_fr.json')

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
    question = input("\n 🧑‍🍳 CHEF MUFFIN : Pose moi la question que tu veux sur la recette en cours. \n Si tu souhaites changer de recette, entre 'changer' \n " if recette_active else "\n 🧑‍🍳 CHEF MUFFIN : Bonjour ! Je suis Chef Muffin. \n Je vais t'aider à préparer de délicieux muffins. \n Donne moi les ingrédients que tu as à disposition, ou le type de muffins que tu souhaiterais faire. \n Sinon, entre 'exit' pour quitter. \n Votre réponse :")
    #Pour s'assurer, lors de la première demande de l'utilisateur, que tous les éléments clés lui sont donnés
    
    if question.lower() in ["exit", "q", "quit"]:
            print("🧑‍🍳 CHEF MUFFIN : Bon appétit et à bientôt ! 👋")
            break
    
    # --- MÉCANIQUE DE RESET ---
    mots_cles_changement = ["changer", "autre recette", "nouvelle recherche", "nouveau"]
    if any(mot in question.lower() for mot in mots_cles_changement):
        print("🧑‍🍳 CHEF MUFFIN : 🔄 D'accord, changeons de recette !")
        recette_active = None
        chef.reset_memory() # On vide la mémoire du chef
        continue

    # --- CAS 1 : MODE RECHERCHE (Pas de recette active) ---
    if recette_active is None:
        vecteur_question = tool.vectoriser([question])[0].tolist()
        reponse = database.search(query_embedding=vecteur_question, k=1)
        
        if reponse['documents']:
            # On a trouvé ! On "verrouille" cette recette
            recette_active = reponse['documents'][0][0] # Le texte de la recette
            titre = reponse['metadatas'][0][0]['titre']
            
            # On laisse le code continuer vers le LLM 
        else:
            print("🧑‍🍳 CHEF MUFFIN : Désolé, je n'ai aucune recette qui correspond. Essaie autre chose.")
            continue

    # --- CAS 2 : MODE DISCUSSION (Recette active) ---
    
    reponse_llm = chef.generate_response(context_str=recette_active, query_str=question)
    
    print("\n" + "-"*50)
    print(f"🧑‍🍳 CHEF MUFFIN : {reponse_llm}")
    print("-"*50)