import json
import os
from typing import List, Dict

def load_data(file_path: str = "data/raw/recettes_fr.json") -> List[Dict]:
    """
    Charge les recettes depuis un fichier JSON local.
    
    Args:
        file_path (str): Chemin vers le fichier JSON.
    
    Returns:
        List[Dict]: Liste des recettes formatées pour le RAG.
    """
    # Verif de l'existence du fichier
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier de données est introuvable ici : {file_path}")
    
    print(f"Chargement des données depuis {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except json.JSONDecodeError:
        print("Erreur : Le fichier JSON est mal formé.")
        return []
        
    data = []
    
    # Nettoyage et Formatage
    for item in raw_data:
        titre = item.get("titre", "Recette sans titre")
        texte = item.get("texte", "")
        metadata = item.get("metadata")
        metadata["titre"] = titre
        
        # Création du texte pour le RAG
        texte_rag = (
            f"Titre : {titre}\n"
            f"{texte}\n"
        )
        
        data.append({
            "titre": titre,
            "texte": texte_rag,  # On garde le texte formaté
            "metadata": metadata # Utile pour savoir d'où ça vient
        })

    print(f"Succès : {len(data)} recettes chargées.")
    return data

if __name__ == "__main__":
    # Test immédiat
    try:
        recettes = load_data()
        print("\n--- Exemple de recette formatée ---")
        print(recettes[0]['texte'])
    except Exception as e:
        print(f"Erreur : {e}")