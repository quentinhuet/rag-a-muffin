import os 
import sys
from src.data_loader import load_data
from src.embeddings import RAGTool
from src.vector_store import RecipeDB
from src.generator_v1 import MuffinChef

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


while True:
    question = input("Merci d'indiquer votre recherche. Pour quitter, taper 'exit'.")
    if question == "exit":
        break
    vecteur_question = tool.vectoriser(data=[question])[0].tolist()
    reponse = database.search(query_embedding=vecteur_question)
    if reponse['documents'] and reponse['documents'][0]:
        #titre_recette = reponse['metadatas'][0][0]['titre']
        contenu_recette = reponse['documents'][0][0]

        reponse_chef = chef.generate_response(context_str = contenu_recette, query_str = question)

        print("\n" + "="*60)
        print(f"🍽️  MuffinChef :")
        print(f"\n{reponse_chef}\n")
        print("="*60)        
    else:
        print("\n❌ Désolé, je n'ai trouvé aucune recette correspondante dans mes carnets.\n")
