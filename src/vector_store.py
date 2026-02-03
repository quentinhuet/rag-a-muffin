import chromadb
import os
import uuid

class RecipeDB:
    def __init__(self, collection_name: str = "recettes_muffins"):
        current_file_path = os.path.abspath(__file__)
        src_directory = os.path.dirname(current_file_path)
        project_root = os.path.dirname(src_directory)
        self.db_path = os.path.join(project_root, "data", "chroma_db")

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

        print(f"✅ ChromaDB connecté au dossier : {self.db_path}")

    def add_recipes(self, data, embeddings):
        if not data:
            return

        print(f"💾 Ajout de {len(data)} recettes dans la base...")

        documents = []
        metadata = []
        ids = []

        for recette in data:
            ids.append(str(uuid.uuid4()))
            documents.append(recette.get('texte', ' '))
            metadata.append(recette.get('metadata', {}))
        self.collection.add(documents = documents, embeddings = embeddings, ids = ids, metadatas = metadata)

        print("✅ Sauvegarde terminée.")

    def search(self, query_embedding, k=1):
        results = self.collection.query(
            query_embeddings=[query_embedding], # Chroma attend une liste de vecteurs
            n_results=k
        )
        return results
    

# Zone de test

if __name__ == "__main__":
    print("🧪 Démarrage du test unitaire de RecipeDB...")

    # On utilise une collection 'test' pour ne pas polluer la vraie
    db = RecipeDB(collection_name="test_unitaire")
    recettes_test = [
        {"texte": "Recette A : Tarte aux pommes", "metadata": {"type": "dessert"}},
        {"texte": "Recette B : Steak Frites", "metadata": {"type": "plat"}}
    ]

    vecteurs_test = [
        [0.9, 0.1, 0.1], 
        [0.1, 0.9, 0.1]
    ]

    # 3. Ajout dans la base
    print("\n--- Test d'ajout ---")
    db.add_recipes(recettes_test, vecteurs_test)

    # 4. Recherche
    print("\n--- Test de recherche ---")
    # On cherche quelque chose qui ressemble au vecteur A (le sucré)
    vecteur_requete = [0.15, 0.95, 0.05] 
    
    resultats = db.search(vecteur_requete, k=1)
    
    print("Résultat brut renvoyé par Chroma :")
    print(resultats)
    
    # Vérification visuelle
    docs = resultats['documents'][0]
    print(f"\nDocument trouvé : {docs[0]}")
    
    # Nettoyage
    db.client.delete_collection("test_unitaire")

