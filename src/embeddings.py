from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import numpy as np
import torch
from typing import List

class RAGTool:
    def __init__(self, model_name: str='paraphrase-multilingual-MiniLM-L12-v2'):
        print(f"🔄 Initialisation : Chargement du modèle {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✅ Modèle chargé et prêt !")

    def vectoriser(self, data: List[str]) -> np.ndarray:
        embeddings = self.model.encode(data)
        return embeddings

    # La fonction suivante ne sert plus, elle a été archivée pour maintenir l'historique de travail
    # cf README.md, partie II.3
    '''
    def rechercher(self, question: str, embeddings, k: int=3):
        question_embedding = self.model.encode(question)

        scores = util.cos_sim(question_embedding, embeddings)
        top_results = torch.topk(scores, k=3)
        return top_results
    '''

# Tests 
if __name__ == "__main__":
    tool = RAGTool()

    data = ["J'aime les pommes", "J'aime les poires", "Je conduis un camion"]
    print("\nCalcul des vecteurs...")
    embeddings = tool.vectoriser(data)

    print ("\nTest de recherche:")
    top = tool.rechercher("Je veux une voiture", embeddings)
    top_usable = list(zip(top.indices[0], top.values[0]))
    print(f"Meilleur score index : {top_usable[0][0]} (Score: {top_usable[0][1]})")
