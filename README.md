# II - Historique de construction

## 1ère étape : gestion des données
Afin d'éviter de perdre trop de temps à constituer le dataset, j'ai commencé par créer des données factices (`mock_recipes.json`), comprenant uniquement 5 recettes, dont toutes n'étaient pas des recettes des muffins. L'objectif ici est simplement d'avoir des données à manipuler pour comprendre le fonctionnement des embeddings. 
On reviendra sur la construction d'une base de données propre dans un second temps. 

## 2ème étape : construction des embeddings
Pour ce faire, j'ai choisi d'utiliser le modèle d'embeddings proposé par le module `SentenceTransformers`. 
Après quelques tests, en entrant une question au modèle, et en cherchant la similarité entre ma question et les recettes disponibles, on remarque que la précision n'est pas géniale. 
Par exemple, en demandant une recette de petit gâteau aux pépites, la recette le plus proche est celle du gâteau au yaourt. Cela ne représentera peut être pas de problème lorsque l'on aura uniquement des recettes de muffins, mais est quand même bon à prendre en compte. 
Pour éviter ce problème, on pourra demander au LLM, le moment venu, de faire un choix parmi le top 3 proposé par notre modèle d'embeddings, en prenant la recette qui lui semble être la plus pertinente. Ainsi, le modèle RAG fera le 1er "pré-tri" entre toutes les recettes, et le LLM aura le dernier mot sur le choix final. 

Une fois ces tests faits, on construit le code propre des embeddings dans le fichier `embeddings.py`, notamment la class `RAGTool`.

## 3ème étape : stockage des vecteurs dans une base de données ChromaDB

On construir le fichier `vector_store.py`. 
Remarque : la méthode `collection.query` de ChromaDB permet de faire directement la recherche du vecteur le plus proche d'un vecteur donné dans la collection. J'ai donc construit la méthode `search` dans la classe `RecipeDB`, utilisant la méthode query. 
Ainsi, il n'y a plus besoin de la méthode `rechercher` prévue initialement dans `embeddings.py`